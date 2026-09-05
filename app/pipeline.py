import gc
import json
import re
import shutil
from pathlib import Path
from typing import Callable

from . import audio_utils, config, diarize as diarize_mod, merge, render
from . import speaker_profiles, transcribe as transcribe_mod
from .errors import JobCancelled

RAW_SEGMENTS_FILENAME = "raw_segments.json"


def _safe_stem(filename: str) -> str:
    stem = Path(filename).stem
    return re.sub(r'[\/:*?"<>|]', "_", stem).strip() or "transcript"


def _release_ml_memory():
    """Free cached accelerator memory between heavy phases (diarization,
    transcription, embedding matching each load their own multi-hundred-MB
    to multi-GB models) — on 16GB machines, letting cached-but-unused memory
    pile up across phases risks the OS killing the app under memory pressure."""
    gc.collect()
    try:
        import torch

        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:
        pass
    try:
        import mlx.core as mx

        mx.clear_cache()
    except Exception:
        pass


def _fmt_hms(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _load_raw_segments(source_job_id: str) -> dict:
    raw_path = config.OUTPUT_DIR / source_job_id / RAW_SEGMENTS_FILENAME
    if not raw_path.exists():
        raise RuntimeError(
            "이 작업에 필요한 원본 데이터가 없습니다 (예전 버전에서 만든 작업이거나 이미 삭제된 작업입니다)."
        )
    return json.loads(raw_path.read_text())


def _render_and_deliver(
    job_id: str,
    out_dir: Path,
    original_filename: str,
    diarization_segments: list[dict],
    transcript_segments: list[dict],
    speaker_names: dict[str, str],
    match_debug: dict,
    update: Callable,
    wav_path_to_copy: Path | None = None,
    existing_wav_saved_path: str | None = None,
    speaker_merges: dict[str, list[str]] | None = None,
):
    """Shared tail end of every code path that produces a result: merging,
    rendering, and delivering the output files.

    Exactly one of `wav_path_to_copy` (a fresh 16kHz audio file to copy into
    the result folder — only the original conversion has one of these) or
    `existing_wav_saved_path` (an already-saved audio file's path, carried
    forward unchanged from the source job this one was derived from) should
    be given, so every job in a rematch/relabel chain still has an audio
    file available for a future rematch, without ever duplicating it.
    """
    update(status="merging", progress=92, message="결과 정리 중...")
    assigned = merge.assign_speakers(transcript_segments, diarization_segments)
    blocks = merge.group_by_speaker(assigned)

    txt_path = render.write_txt(blocks, speaker_names, out_dir / "transcript.txt")
    srt_path = render.write_srt(assigned, speaker_names, out_dir / "transcript.srt")
    json_path = render.write_json(blocks, speaker_names, out_dir / "transcript.json")

    # Deliver the final files to the user's configured save location
    # (Downloads by default) rather than only the internal app-data folder —
    # and so the UI never needs an in-page download link (those navigate the
    # embedded webview to a raw file response and can leave it stuck there).
    save_dir = config.RESULT_SAVE_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"{_safe_stem(original_filename)}_{job_id[:8]}"
    saved_paths = {}
    for src, ext in ((txt_path, "txt"), (srt_path, "srt"), (json_path, "json")):
        dest = save_dir / f"{base_name}.{ext}"
        shutil.copyfile(src, dest)
        saved_paths[ext] = str(dest)

    if wav_path_to_copy is not None:
        wav_dest = save_dir / f"{base_name}.wav"
        shutil.copyfile(wav_path_to_copy, wav_dest)
        saved_paths["wav"] = str(wav_dest)
    elif existing_wav_saved_path:
        saved_paths["wav"] = existing_wav_saved_path

    update(
        status="done",
        progress=100,
        message="완료",
        result={
            "txt": txt_path.name,
            "srt": srt_path.name,
            "json": json_path.name,
            "speakers": speaker_names,
            "match_debug": match_debug,
            "speaker_merges": speaker_merges or {},
            "saved_dir": str(save_dir),
            "saved_paths": saved_paths,
            "can_rematch": True,
        },
    )


def run_job(
    job_id: str,
    input_path: Path,
    original_filename: str,
    profile_ids: list[str] | None,
    update: Callable,
    is_cancelled: Callable[[], bool] | None = None,
    owns_input_file: bool = True,
    min_speakers: int | None = None,
    max_speakers: int | None = None,
):
    def check_cancelled():
        if is_cancelled and is_cancelled():
            raise JobCancelled()

    out_dir = config.OUTPUT_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    wav_path = out_dir / "audio.wav"

    update(status="extracting_audio", progress=5, message="오디오 추출 중...")
    audio_utils.extract_wav(input_path, wav_path)
    check_cancelled()

    if owns_input_file:
        # This is our own copy (uploaded via the browser-style file picker/
        # drag-and-drop, which never exposes a real path to copy from
        # instead) — often hundreds of MB, and never needed again once we
        # have the extracted audio, so free it immediately rather than
        # leaving it to accumulate.
        shutil.rmtree(input_path.parent, ignore_errors=True)
    # else: this path was handed to us directly by the desktop app's native
    # file picker and belongs to the user — never delete or move it.

    update(status="diarizing", progress=15, message="화자 분리 중... (파일 길이에 따라 시간이 걸릴 수 있습니다)")

    def hook(step_name, step_artifact, file=None, total=None, completed=None):
        check_cancelled()
        if total and completed is not None:
            frac = completed / total
            update(
                progress=15 + int(frac * 35),
                message=f"화자 분리 중... {int(frac * 100)}% ({step_name})",
            )

    diarization_segments = diarize_mod.diarize(
        wav_path, hook=hook, min_speakers=min_speakers, max_speakers=max_speakers
    )
    check_cancelled()

    update(status="diarizing", progress=48, message="화자 그룹 정리 중...")
    diarization_segments, speaker_merges = speaker_profiles.consolidate_fragmented_speakers(
        wav_path, diarization_segments
    )
    _release_ml_memory()

    update(status="transcribing", progress=50, message="음성 인식(전사) 중... 0%")

    def transcribe_progress(processed_seconds, total_seconds):
        frac = processed_seconds / total_seconds if total_seconds else 1.0
        pct = int(frac * 100)
        update(
            progress=50 + int(frac * 35),
            message=f"음성 인식(전사) 중... {pct}% ({_fmt_hms(processed_seconds)} / {_fmt_hms(total_seconds)})",
        )

    transcript_segments = transcribe_mod.transcribe(
        wav_path, progress_cb=transcribe_progress, is_cancelled=is_cancelled
    )
    check_cancelled()
    _release_ml_memory()

    # Keep the (lightweight, just timestamps/labels/text — no audio) raw
    # diarization and transcript segments around after the job finishes, so
    # that changing the match-sensitivity setting, which voice profiles to
    # match, or manually renaming a speaker later doesn't require redoing
    # the two slow steps (diarization, transcription) — see rematch_job()
    # and relabel_job() below.
    (out_dir / RAW_SEGMENTS_FILENAME).write_text(
        json.dumps(
            {
                "diarization_segments": diarization_segments,
                "transcript_segments": transcript_segments,
                "original_filename": original_filename,
            },
            ensure_ascii=False,
        )
    )

    update(status="matching_speakers", progress=85, message="화자 매칭 중...")
    speaker_names, match_debug = speaker_profiles.match_speakers_debug(
        wav_path, diarization_segments, profile_ids
    )

    check_cancelled()
    _render_and_deliver(
        job_id, out_dir, original_filename, diarization_segments, transcript_segments, speaker_names, match_debug,
        update, wav_path_to_copy=wav_path, speaker_merges=speaker_merges,
    )
    wav_path.unlink(missing_ok=True)


def rematch_job(
    job_id: str,
    source_job_id: str,
    wav_saved_path: str,
    profile_ids: list[str] | None,
    update: Callable,
    is_cancelled: Callable[[], bool] | None = None,
):
    """Re-run only speaker matching (+ merge/render) for a job that already
    finished diarization and transcription, reusing those saved results —
    used when the user only changed the match-sensitivity setting or which
    voice profiles to match against, which would otherwise mean waiting
    through the two slowest pipeline steps again for no reason. Uses the
    audio saved alongside the source job's results directly (no video to
    re-extract from — see run_job(), which deletes the upload right after
    extracting its audio)."""

    def check_cancelled():
        if is_cancelled and is_cancelled():
            raise JobCancelled()

    wav_path = Path(wav_saved_path)
    if not wav_path.exists():
        raise RuntimeError(
            "재매칭에 필요한 오디오 파일을 찾을 수 없습니다 "
            f"({wav_path.name}이 결과 저장 위치에서 옮겨졌거나 삭제된 것 같습니다)."
        )

    raw = _load_raw_segments(source_job_id)
    diarization_segments = raw["diarization_segments"]
    transcript_segments = raw["transcript_segments"]
    original_filename = raw["original_filename"]

    out_dir = config.OUTPUT_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    # copy the SOURCE job's raw_segments.json verbatim (pre-consolidation) so
    # a future rematch always starts from the same original diarization data
    # rather than compounding an already-merged result.
    shutil.copyfile(config.OUTPUT_DIR / source_job_id / RAW_SEGMENTS_FILENAME, out_dir / RAW_SEGMENTS_FILENAME)
    check_cancelled()

    update(status="matching_speakers", progress=40, message="화자 그룹 정리 중...")
    diarization_segments, speaker_merges = speaker_profiles.consolidate_fragmented_speakers(
        wav_path, diarization_segments
    )
    check_cancelled()

    update(status="matching_speakers", progress=50, message="화자 매칭 재계산 중...")
    speaker_names, match_debug = speaker_profiles.match_speakers_debug(
        wav_path, diarization_segments, profile_ids
    )

    check_cancelled()
    _render_and_deliver(
        job_id, out_dir, original_filename, diarization_segments, transcript_segments, speaker_names, match_debug,
        update, existing_wav_saved_path=wav_saved_path, speaker_merges=speaker_merges,
    )


def relabel_job(
    job_id: str,
    source_job_id: str,
    speaker_names: dict[str, str],
    wav_saved_path: str | None,
    update: Callable,
):
    """Apply a manually-edited raw-label -> display-name mapping to a
    finished job's already-computed diarization/transcript. No audio or
    matching involved at all, so this is close to instant — for correcting
    cases where diarization split one real person's speech across multiple
    raw speaker labels (or merged two different people), which no amount of
    voice-profile tuning can fix on its own since it's a clustering mistake,
    not a matching-confidence problem."""
    raw = _load_raw_segments(source_job_id)
    diarization_segments = raw["diarization_segments"]
    transcript_segments = raw["transcript_segments"]
    original_filename = raw["original_filename"]

    out_dir = config.OUTPUT_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config.OUTPUT_DIR / source_job_id / RAW_SEGMENTS_FILENAME, out_dir / RAW_SEGMENTS_FILENAME)

    update(status="merging", progress=50, message="이름 반영 중...")
    _render_and_deliver(
        job_id, out_dir, original_filename, diarization_segments, transcript_segments, speaker_names, {},
        update, existing_wav_saved_path=wav_saved_path,
    )
