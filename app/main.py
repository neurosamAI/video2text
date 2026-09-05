import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import audio_utils, config, i18n, jobs, speaker_profiles

app = FastAPI(title="video2text")

STATIC_DIR = config.BASE_DIR / "static"


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.post("/api/jobs")
async def create_job(
    file: UploadFile | None = File(None),
    local_path: str | None = Form(None),
    profile_ids: str = Form(""),
    min_speakers: int | None = Form(None),
    max_speakers: int | None = Form(None),
):
    ids = [p for p in profile_ids.split(",") if p] or None

    if local_path:
        # Came from the desktop app's native file picker (see app/desktop.py
        # Api.pick_video) — a real path on disk, so we can read the video
        # directly instead of copying its (often huge) contents first. This
        # file belongs to the user, not to us: never delete or move it.
        path = Path(local_path).expanduser()
        if not path.is_file():
            raise HTTPException(400, i18n.t("file_not_found"))
        real_job_id = jobs.create_job(
            path, path.name, ids, owns_file=False, min_speakers=min_speakers, max_speakers=max_speakers
        )
        return {"job_id": real_job_id}

    if not file:
        raise HTTPException(400, i18n.t("file_or_local_path_required"))

    job_id = uuid.uuid4().hex[:12]
    upload_dir = config.UPLOAD_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename).suffix or ".mp4"
    dest = upload_dir / f"input{suffix}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    real_job_id = jobs.create_job(
        dest, file.filename, ids, owns_file=True, min_speakers=min_speakers, max_speakers=max_speakers
    )
    return {"job_id": real_job_id}


@app.get("/api/jobs")
def list_jobs(offset: int = 0, limit: int = 10):
    page, total = jobs.list_jobs(offset=offset, limit=limit)
    return {
        "jobs": [{k: v for k, v in j.items() if k not in ("input_path",)} for j in page],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str):
    result = jobs.delete_job(job_id)
    if result is None:
        raise HTTPException(400, i18n.t("cannot_delete_running_job"))
    if result is False:
        raise HTTPException(404, "job not found")
    return {"ok": True}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return {k: v for k, v in job.items() if k != "input_path"}


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    if not jobs.cancel_job(job_id):
        raise HTTPException(400, i18n.t("cannot_cancel_job"))
    return {"ok": True}


@app.post("/api/jobs/{job_id}/rematch")
def rematch_job(job_id: str, profile_ids: str = Form("")):
    """Re-run only speaker matching for a finished job (reusing its saved
    diarization/transcription) — much faster than a full re-conversion when
    only the match-sensitivity setting or selected profiles changed."""
    source = jobs.get_job(job_id)
    if not source or source.get("status") != "done":
        raise HTTPException(400, i18n.t("rematch_requires_done"))
    ids = [p for p in profile_ids.split(",") if p] or None
    new_job_id = jobs.create_rematch_job(job_id, ids)
    if new_job_id is None:
        raise HTTPException(404, "job not found")
    return {"job_id": new_job_id}


@app.post("/api/jobs/{job_id}/relabel")
def relabel_job(job_id: str, overrides: str = Form(...)):
    """Manually rename one or more raw speaker labels for a finished job —
    e.g. diarization split one real person across two raw speaker labels;
    this merges them under one name without redoing matching or audio.
    `overrides` is a JSON object like {"SPEAKER_06": "정문창"}; any raw
    label not mentioned keeps its current name."""
    source = jobs.get_job(job_id)
    if not source or source.get("status") != "done" or not source.get("result"):
        raise HTTPException(400, i18n.t("relabel_requires_done"))
    try:
        parsed_overrides = json.loads(overrides)
        if not isinstance(parsed_overrides, dict):
            raise ValueError
    except ValueError:
        raise HTTPException(400, i18n.t("overrides_must_be_object"))

    speaker_names = dict(source["result"].get("speakers") or {})
    speaker_names.update(parsed_overrides)

    new_job_id = jobs.create_relabel_job(job_id, speaker_names)
    if new_job_id is None:
        raise HTTPException(404, "job not found")
    return {"job_id": new_job_id}


@app.get("/api/jobs/{job_id}/download/{fmt}")
def download(job_id: str, fmt: str):
    job = jobs.get_job(job_id)
    if not job or job.get("status") != "done":
        raise HTTPException(404, "result not available")
    if fmt not in ("txt", "srt", "json"):
        raise HTTPException(400, "invalid format")
    path = config.OUTPUT_DIR / job_id / f"transcript.{fmt}"
    if not path.exists():
        raise HTTPException(404, "file not found")
    base = Path(job["filename"]).stem
    return FileResponse(path, filename=f"{base}.{fmt}")


@app.get("/api/speakers")
def list_speakers():
    return speaker_profiles.list_profiles()


@app.post("/api/speakers")
async def add_speaker(name: str = Form(...), file: UploadFile = File(...)):
    tmp_id = uuid.uuid4().hex[:12]
    raw_path = config.SPEAKERS_SAMPLES_DIR / f"{tmp_id}_raw{Path(file.filename).suffix or '.dat'}"
    with raw_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    wav_path = config.SPEAKERS_SAMPLES_DIR / f"{tmp_id}.wav"
    try:
        audio_utils.extract_wav(raw_path, wav_path)
        profile = speaker_profiles.add_profile(name, wav_path, original_filename=file.filename)
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        raw_path.unlink(missing_ok=True)
        wav_path.unlink(missing_ok=True)
    return profile


@app.delete("/api/speakers/{profile_id}")
def delete_speaker(profile_id: str):
    if not speaker_profiles.delete_profile(profile_id):
        raise HTTPException(404, "profile not found")
    return {"ok": True}


@app.get("/api/speakers/{profile_id}/samples")
def list_speaker_samples(profile_id: str):
    samples = speaker_profiles.list_samples(profile_id)
    if samples is None:
        raise HTTPException(404, "profile not found")
    return samples


@app.delete("/api/speakers/{profile_id}/samples/{index}")
def delete_speaker_sample(profile_id: str, index: int):
    result = speaker_profiles.delete_sample(profile_id, index)
    if result is None:
        raise HTTPException(404, "sample not found")
    return {"ok": True, "result": result}


@app.get("/api/speakers/{profile_id}/samples/{index}/audio")
def get_speaker_sample_audio(profile_id: str, index: int):
    path = speaker_profiles.get_sample_audio_path(profile_id, index)
    if path is None:
        raise HTTPException(404, "audio not found")
    return FileResponse(path, media_type="audio/wav")


def _persist_env_var(key: str, value: str):
    env_path = config.DATA_DIR / ".env"
    lines = []
    if env_path.exists():
        lines = [line for line in env_path.read_text().splitlines() if not line.startswith(f"{key}=")]
    lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines) + "\n")
    os.environ[key] = value


@app.get("/api/settings")
def get_settings():
    token = config.HF_TOKEN
    return {
        "hf_token_set": bool(token),
        "hf_token_preview": (token[:6] + "…") if token else None,
        "result_save_dir": str(config.RESULT_SAVE_DIR),
        "speaker_match_threshold": config.SPEAKER_MATCH_THRESHOLD,
        "speaker_consolidation_threshold": config.SPEAKER_CONSOLIDATION_THRESHOLD,
        "ui_language": config.UI_LANGUAGE,
        "effective_language": i18n.effective_language(),
    }


@app.post("/api/settings")
def save_settings(
    hf_token: str | None = Form(None),
    result_save_dir: str | None = Form(None),
    speaker_match_threshold: float | None = Form(None),
    speaker_consolidation_threshold: float | None = Form(None),
    ui_language: str | None = Form(None),
):
    if hf_token is not None and hf_token.strip():
        token = hf_token.strip()
        _persist_env_var("HF_TOKEN", token)
        config.HF_TOKEN = token

    if result_save_dir is not None and result_save_dir.strip():
        path = Path(result_save_dir.strip()).expanduser()
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise HTTPException(400, i18n.t("cannot_create_folder", error=e))
        _persist_env_var("RESULT_SAVE_DIR", str(path))
        config.RESULT_SAVE_DIR = path

    if speaker_match_threshold is not None:
        if not (0.0 <= speaker_match_threshold <= 1.0):
            raise HTTPException(400, i18n.t("threshold_range"))
        _persist_env_var("SPEAKER_MATCH_THRESHOLD", str(speaker_match_threshold))
        config.SPEAKER_MATCH_THRESHOLD = speaker_match_threshold

    if speaker_consolidation_threshold is not None:
        if not (0.0 <= speaker_consolidation_threshold <= 1.0):
            raise HTTPException(400, i18n.t("threshold_range"))
        _persist_env_var("SPEAKER_CONSOLIDATION_THRESHOLD", str(speaker_consolidation_threshold))
        config.SPEAKER_CONSOLIDATION_THRESHOLD = speaker_consolidation_threshold

    if ui_language is not None:
        if ui_language not in ("system", "ko", "en"):
            raise HTTPException(400, "ui_language must be 'system', 'ko', or 'en'")
        _persist_env_var("UI_LANGUAGE", ui_language)
        config.UI_LANGUAGE = ui_language

    return {"ok": True}


@app.post("/api/reveal")
def reveal(path: str = Form(...)):
    """Reveal a file/folder in Finder — used instead of in-page download
    links, which navigate the embedded desktop window to a raw file
    response and can leave it stuck there."""
    target = Path(path)
    if not target.exists():
        raise HTTPException(404, i18n.t("path_not_found"))
    subprocess.run(["open", "-R", str(target)])
    return {"ok": True}
