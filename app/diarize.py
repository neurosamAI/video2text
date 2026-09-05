import gc
from pathlib import Path
from typing import Callable, Optional

import torch

from . import config


def _get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _load_pipeline():
    from pyannote.audio import Pipeline

    if not config.HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN이 설정되지 않았습니다. .env 파일에 HuggingFace 토큰을 설정하세요 "
            "(README.md의 화자분리 모델 접근 권한 안내를 참고하세요)."
        )
    pipeline = Pipeline.from_pretrained(
        config.DIARIZATION_MODEL, use_auth_token=config.HF_TOKEN
    )
    pipeline.to(_get_device())
    return pipeline


def diarize(
    wav_path: Path,
    hook: Optional[Callable] = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
):
    """Run speaker diarization on a WAV file.

    `hook`, if given, is a callable matching pyannote's hook signature
    (step_name, step_artifact, file=None, total=None, completed=None).

    `min_speakers`/`max_speakers`, if given, bound how many distinct
    speakers pyannote's clustering step may settle on — left unset, it
    estimates the count entirely on its own, which is prone to
    over-segmenting one person's voice into several speaker labels
    (see speaker_profiles.consolidate_fragmented_speakers for the
    complementary post-hoc fix). Either bound may be given alone, or both
    together as a range, per pyannote's own API.

    The pipeline is loaded fresh and released right after use (rather than
    cached for the process lifetime) — on a memory-constrained machine,
    keeping pyannote's models resident while mlx-whisper's model also loads
    for the transcription phase risks the OS killing the app for memory
    pressure on long recordings. The reload cost per job (a few seconds) is
    a worthwhile trade for that headroom.

    Returns a list of dicts: [{"start": float, "end": float, "speaker": "SPEAKER_00"}, ...]
    """
    pipeline = _load_pipeline()
    kwargs = {"hook": hook} if hook is not None else {}
    if min_speakers is not None:
        kwargs["min_speakers"] = min_speakers
    if max_speakers is not None:
        kwargs["max_speakers"] = max_speakers

    diarization = pipeline(str(wav_path), **kwargs)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({"start": turn.start, "end": turn.end, "speaker": speaker})
    segments.sort(key=lambda s: s["start"])

    del pipeline, diarization
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return segments
