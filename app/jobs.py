import json
import queue
import shutil
import threading
import traceback
import uuid
from datetime import datetime
from pathlib import Path

from . import config, i18n
from .errors import JobCancelled

_JOBS_FILE = config.DATA_DIR / "jobs.json"
_TERMINAL_STATUSES = {"done", "error", "cancelled"}

_JOBS: dict[str, dict] = {}
_LOCK = threading.Lock()
_QUEUE: "queue.Queue[str]" = queue.Queue()
_WORKER_STARTED = False
_CANCEL_EVENTS: dict[str, threading.Event] = {}


def _load_jobs():
    if not _JOBS_FILE.exists():
        return
    try:
        records = json.loads(_JOBS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return

    changed = False
    for job in records:
        # a non-terminal status here means the app quit (or crashed) mid-job —
        # nothing will ever resume it, so surface that instead of leaving a
        # progress bar stuck forever.
        if job.get("status") not in _TERMINAL_STATUSES:
            job["status"] = "error"
            job["message"] = i18n.t("app_restarted_interrupted")
            job["error"] = "interrupted by app restart"
            changed = True
        _JOBS[job["id"]] = job

    if changed:
        _persist()


def _persist():
    try:
        _JOBS_FILE.write_text(json.dumps(list(_JOBS.values()), ensure_ascii=False, indent=2))
    except OSError:
        pass


_load_jobs()


def _update(job_id: str, **kwargs):
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(kwargs)
            _persist()


def get_job(job_id: str) -> dict | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        return dict(job) if job else None


def list_jobs(offset: int = 0, limit: int | None = None) -> tuple[list[dict], int]:
    """Returns (page, total_count), most recent first."""
    with _LOCK:
        ordered = sorted(_JOBS.values(), key=lambda j: j["created_at"], reverse=True)
        total = len(ordered)
        page = ordered[offset : offset + limit] if limit is not None else ordered[offset:]
        return [dict(j) for j in page], total


def delete_job(job_id: str) -> bool | None:
    """Delete a finished job's history entry and its saved working files.
    Returns True if deleted, False if not found, None if the job is still
    active (queued/running) and must be cancelled first."""
    with _LOCK:
        job = _JOBS.get(job_id)
        if not job:
            return False
        if job["status"] not in _TERMINAL_STATUSES:
            return None
        del _JOBS[job_id]
        _persist()

    shutil.rmtree(config.OUTPUT_DIR / job_id, ignore_errors=True)
    shutil.rmtree(config.UPLOAD_DIR / job_id, ignore_errors=True)
    return True


def create_job(
    input_path: Path,
    original_filename: str,
    profile_ids: list[str] | None,
    owns_file: bool = True,
    min_speakers: int | None = None,
    max_speakers: int | None = None,
) -> str:
    """`owns_file` marks whether this file is our own copy (safe to delete
    once its audio has been extracted — see pipeline.run_job) or the user's
    own file referenced directly via the desktop app's native file picker
    (never touched). `min_speakers`/`max_speakers` are an optional hint for
    how many distinct speakers to expect, passed straight through to
    diarization — either may be given alone, or both as a range."""
    job_id = uuid.uuid4().hex[:12]
    with _LOCK:
        _JOBS[job_id] = {
            "id": job_id,
            "filename": original_filename,
            "status": "queued",
            "progress": 0,
            "message": i18n.t("queued"),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "input_path": str(input_path),
            "owns_file": owns_file,
            "profile_ids": profile_ids,
            "min_speakers": min_speakers,
            "max_speakers": max_speakers,
            "result": None,
            "error": None,
            "kind": "convert",
            "source_job_id": None,
        }
        _persist()
    _CANCEL_EVENTS[job_id] = threading.Event()
    _QUEUE.put(job_id)
    _ensure_worker()
    return job_id


def create_rematch_job(source_job_id: str, profile_ids: list[str] | None) -> str | None:
    """Queue a fast re-match: reuses the source job's already-computed
    diarization and transcription, only redoing speaker matching (with
    whatever match-sensitivity setting / profiles are current) and
    rendering. Returns None if the source job can't be found."""
    source = get_job(source_job_id)
    if not source:
        return None

    job_id = uuid.uuid4().hex[:12]
    with _LOCK:
        _JOBS[job_id] = {
            "id": job_id,
            "filename": f"{source['filename']} {i18n.t('rematch_suffix')}",
            "status": "queued",
            "progress": 0,
            "message": i18n.t("queued"),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "wav_saved_path": (source.get("result") or {}).get("saved_paths", {}).get("wav"),
            "profile_ids": profile_ids,
            "result": None,
            "error": None,
            "kind": "rematch",
            "source_job_id": source_job_id,
        }
        _persist()
    _CANCEL_EVENTS[job_id] = threading.Event()
    _QUEUE.put(job_id)
    _ensure_worker()
    return job_id


def create_relabel_job(source_job_id: str, speaker_names: dict[str, str]) -> str | None:
    """Queue a manual relabel: apply a user-edited raw-label -> display-name
    mapping to a finished job's already-computed diarization/transcript, no
    audio or matching involved — for correcting diarization mistakes (one
    real person split across multiple raw speaker labels, or two different
    people merged into one) that no amount of profile/threshold tuning can
    fix, since it's a clustering error rather than a low-confidence match."""
    source = get_job(source_job_id)
    if not source:
        return None

    job_id = uuid.uuid4().hex[:12]
    with _LOCK:
        _JOBS[job_id] = {
            "id": job_id,
            "filename": f"{source['filename']} {i18n.t('relabel_suffix')}",
            "status": "queued",
            "progress": 0,
            "message": i18n.t("queued"),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "wav_saved_path": (source.get("result") or {}).get("saved_paths", {}).get("wav"),
            "profile_ids": source.get("profile_ids"),
            "result": None,
            "error": None,
            "kind": "relabel",
            "source_job_id": source_job_id,
            "speaker_names": speaker_names,
        }
        _persist()
    _CANCEL_EVENTS[job_id] = threading.Event()
    _QUEUE.put(job_id)
    _ensure_worker()
    return job_id


def cancel_job(job_id: str) -> bool:
    """Request cancellation of a queued or running job. Takes effect at the
    next checkpoint (pipeline phase boundary, whisper chunk boundary, or the
    next pyannote diarization progress tick) rather than instantly, since the
    underlying libraries don't support interrupting a call mid-flight."""
    job = get_job(job_id)
    if not job or job["status"] in ("done", "error", "cancelled"):
        return False
    event = _CANCEL_EVENTS.get(job_id)
    if not event:
        return False
    event.set()
    _update(job_id, message=i18n.t("cancel_requested"))
    return True


def _ensure_worker():
    global _WORKER_STARTED
    if not _WORKER_STARTED:
        _WORKER_STARTED = True
        t = threading.Thread(target=_worker_loop, daemon=True)
        t.start()


def _worker_loop():
    from . import pipeline

    while True:
        job_id = _QUEUE.get()
        try:
            job = get_job(job_id)
            event = _CANCEL_EVENTS.get(job_id)
            is_cancelled = (lambda ev: (lambda: ev.is_set()))(event) if event else (lambda: False)
            bound_update = lambda **kwargs: _update(job_id, **kwargs)  # noqa: E731

            if is_cancelled():
                raise JobCancelled()

            if job.get("kind") == "rematch":
                if not job.get("wav_saved_path"):
                    raise RuntimeError(i18n.t("rematch_missing_audio"))
                pipeline.rematch_job(
                    job_id,
                    job["source_job_id"],
                    job["wav_saved_path"],
                    job.get("profile_ids"),
                    bound_update,
                    is_cancelled=is_cancelled,
                )
            elif job.get("kind") == "relabel":
                pipeline.relabel_job(
                    job_id,
                    job["source_job_id"],
                    job["speaker_names"],
                    job.get("wav_saved_path"),
                    bound_update,
                )
            else:
                pipeline.run_job(
                    job_id,
                    Path(job["input_path"]),
                    job["filename"],
                    job.get("profile_ids"),
                    bound_update,
                    is_cancelled=is_cancelled,
                    owns_input_file=job.get("owns_file", True),
                    min_speakers=job.get("min_speakers"),
                    max_speakers=job.get("max_speakers"),
                )
        except JobCancelled:
            _update(job_id, status="cancelled", message=i18n.t("cancelled_by_user"))
            shutil.rmtree(config.OUTPUT_DIR / job_id, ignore_errors=True)
        except Exception as e:
            _update(
                job_id,
                status="error",
                error=f"{e}\n{traceback.format_exc()}",
                message=i18n.t("error_occurred", error=e),
            )
        finally:
            _CANCEL_EVENTS.pop(job_id, None)
            _QUEUE.task_done()
