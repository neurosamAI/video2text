import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Data (and the .env with HF_TOKEN) live outside the app bundle / project
# folder so they survive moving or rebuilding video2text.app, and so the
# same .env works no matter which copy (dev source vs bundled app) runs.
DATA_DIR = Path.home() / "Library" / "Application Support" / "video2text"
DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(DATA_DIR / ".env")
load_dotenv(BASE_DIR / ".env")  # fallback for dev convenience, doesn't override
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
SPEAKERS_DIR = DATA_DIR / "speakers"
SPEAKERS_SAMPLES_DIR = SPEAKERS_DIR / "samples"
PROFILES_FILE = SPEAKERS_DIR / "profiles.json"

for d in (UPLOAD_DIR, OUTPUT_DIR, SPEAKERS_DIR, SPEAKERS_SAMPLES_DIR):
    d.mkdir(parents=True, exist_ok=True)

HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "ko")

DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
EMBEDDING_MODEL = "speechbrain/spkrec-ecapa-voxceleb"

SPEAKER_MATCH_THRESHOLD = float(os.environ.get("SPEAKER_MATCH_THRESHOLD", "0.72"))

# How similar two raw diarization labels' voices must be to each other before
# they're treated as the same person and merged — separate from (and
# deliberately more conservative than) SPEAKER_MATCH_THRESHOLD above, since
# wrongly merging two different real people is harder to undo later (no
# re-split) than wrongly leaving two labels of the same person unmerged
# (still fixable per-label via manual relabeling).
SPEAKER_CONSOLIDATION_THRESHOLD = float(os.environ.get("SPEAKER_CONSOLIDATION_THRESHOLD", "0.70"))

# Where finished transcripts are delivered to the user (separate from
# OUTPUT_DIR above, which is just the internal per-job working directory).
# Defaults to Downloads; changeable at runtime via the settings UI.
DEFAULT_RESULT_SAVE_DIR = Path.home() / "Downloads" / "video2text"
RESULT_SAVE_DIR = Path(os.environ.get("RESULT_SAVE_DIR") or DEFAULT_RESULT_SAVE_DIR)
