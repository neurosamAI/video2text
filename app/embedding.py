import numpy as np
import soundfile as sf
import torch

from . import config

_classifier = None
_TARGET_SR = 16000

# A speaker embedding is stable from a few seconds of audio; feeding it much
# more than that is pure waste, and long enough segments (multi-minute) crash
# ECAPA-TDNN's conv layers on the MPS backend ("Output channels > 65536 not
# supported"). Cap what we ever hand to the model.
_MAX_SEGMENT_SECONDS = 30.0


def _get_classifier():
    global _classifier
    if _classifier is None:
        from speechbrain.inference.speaker import EncoderClassifier

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        _classifier = EncoderClassifier.from_hparams(
            source=config.EMBEDDING_MODEL,
            savedir=str(config.SPEAKERS_DIR / ".sb_model_cache"),
            run_opts={"device": device},
        )
    return _classifier


def _load_segment(wav_path, start: float | None = None, end: float | None = None) -> np.ndarray:
    info = sf.info(str(wav_path))
    sr = info.samplerate
    start = start or 0
    file_duration = info.frames / sr
    end = min(end if end is not None else file_duration, start + _MAX_SEGMENT_SECONDS)
    start_frame = int(start * sr)
    stop_frame = int(end * sr)
    data, sr = sf.read(str(wav_path), start=max(start_frame, 0), stop=stop_frame, dtype="float32", always_2d=True)
    mono = data.mean(axis=1)

    if sr != _TARGET_SR:
        # our pipeline always extracts audio at 16kHz, so this is just a safety net
        from scipy.signal import resample_poly

        mono = resample_poly(mono, _TARGET_SR, sr).astype(np.float32)

    return mono


def embed_segment(wav_path, start: float | None = None, end: float | None = None) -> np.ndarray:
    """Compute an L2-normalized speaker embedding for a segment of a WAV file."""
    mono = _load_segment(wav_path, start, end)
    if mono.shape[0] < _TARGET_SR // 4:
        return None
    waveform = torch.from_numpy(mono).unsqueeze(0)
    classifier = _get_classifier()
    with torch.no_grad():
        emb = classifier.encode_batch(waveform)
    emb = emb.squeeze().detach().cpu().numpy().astype(np.float64)
    norm = np.linalg.norm(emb)
    if norm == 0:
        return None
    return emb / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
