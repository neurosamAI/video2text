import shutil
import subprocess
from pathlib import Path

from . import config


def _find_binary(name: str) -> str:
    """Prefer the self-contained ffmpeg/ffprobe bundled in the app (see build.sh),
    falling back to the system PATH for dev-source runs."""
    bundled = config.BASE_DIR / "bin" / name
    if bundled.exists():
        return str(bundled)
    found = shutil.which(name)
    if found:
        return found
    raise RuntimeError(f"{name}를 찾을 수 없습니다. `brew install ffmpeg`로 설치해주세요.")


def extract_wav(input_path: Path, output_path: Path, sample_rate: int = 16000) -> Path:
    """Extract mono PCM16 WAV audio from a video/audio file via ffmpeg."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _find_binary("ffmpeg"), "-y",
        "-i", str(input_path),
        "-vn",
        "-ac", "1",
        "-ar", str(sample_rate),
        "-c:a", "pcm_s16le",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-2000:]}")
    return output_path


def probe_duration(input_path: Path) -> float:
    cmd = [
        _find_binary("ffprobe"), "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr[-2000:]}")
    return float(result.stdout.strip())
