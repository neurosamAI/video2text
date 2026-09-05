import gc
import re
from typing import Callable, Optional

import numpy as np
import soundfile as sf

from . import config
from .errors import JobCancelled

_CHUNK_SECONDS = 300  # transcribe in 5-minute chunks so we can report real progress
_SAMPLE_RATE = 16000

_REPEATED_WORD_RE = re.compile(r"\b(\S+)(?:\s+\1\b){3,}", re.IGNORECASE)


def _collapse_repetition(text: str) -> str:
    """Safety net for whisper's repeated-word hallucination loops
    (e.g. "go go go go go..."): collapse 4+ consecutive repeats of the same
    word down to one. Real speech essentially never repeats a word this many
    times in a row, so this only ever fires on hallucinated output.
    """
    return _REPEATED_WORD_RE.sub(r"\1", text)


def transcribe(
    wav_path,
    language: str | None = None,
    progress_cb: Optional[Callable[[float, float], None]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
):
    """Transcribe a WAV file with mlx-whisper, in chunks so progress can be reported.

    Chunks are read from disk on demand (not the whole file loaded into RAM
    up front) — on long recordings, holding the entire audio array alongside
    the loaded whisper model risks memory pressure on 16GB machines.

    `progress_cb(processed_seconds, total_seconds)` is called after each chunk.
    Returns a list of dicts: [{"start": float, "end": float, "text": str}, ...]
    """
    import mlx_whisper

    info = sf.info(str(wav_path))
    total_seconds = info.frames / info.samplerate

    segments = []
    prev_text_tail = ""

    with sf.SoundFile(str(wav_path)) as f:
        chunk_frames = int(_CHUNK_SECONDS * f.samplerate)
        offset = 0
        while True:
            if is_cancelled and is_cancelled():
                raise JobCancelled()

            data = f.read(frames=chunk_frames, dtype="float32", always_2d=True)
            if len(data) == 0:
                if offset == 0:
                    break  # empty file
                break

            chunk = data.mean(axis=1)
            if f.samplerate != _SAMPLE_RATE:
                from scipy.signal import resample_poly

                chunk = resample_poly(chunk, _SAMPLE_RATE, f.samplerate).astype(np.float32)

            chunk_offset_s = offset / f.samplerate

            kwargs = dict(
                path_or_hf_repo=config.WHISPER_MODEL,
                language=language or config.WHISPER_LANGUAGE,
                word_timestamps=False,
                # False, not True: letting a bad decode's text condition the
                # next segment is the main way whisper spirals into repeated-
                # word hallucination loops ("go go go...") on noisy/unclear
                # audio. We still bridge context across chunks ourselves via
                # initial_prompt below, just not segment-to-segment within one.
                condition_on_previous_text=False,
                # Use silence detection to drop segments that are likely
                # hallucinated rather than actually spoken.
                hallucination_silence_threshold=2.0,
            )
            if prev_text_tail:
                kwargs["initial_prompt"] = prev_text_tail

            result = mlx_whisper.transcribe(chunk, **kwargs)
            del chunk, data

            chunk_segments = [
                {
                    "start": chunk_offset_s + seg["start"],
                    "end": chunk_offset_s + seg["end"],
                    "text": _collapse_repetition(seg["text"].strip()),
                }
                for seg in result.get("segments", [])
                if seg["text"].strip()
            ]
            segments.extend(chunk_segments)
            if chunk_segments:
                prev_text_tail = chunk_segments[-1]["text"][-200:]

            offset += chunk_frames
            processed = min(offset / f.samplerate, total_seconds)
            if progress_cb:
                progress_cb(processed, total_seconds)

            gc.collect()

    return segments
