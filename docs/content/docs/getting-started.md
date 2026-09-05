---
title: Getting Started
description: "Download video2text, set up model access, and run your first transcription."
weight: 2
---

## Requirements

- **Apple Silicon Mac** (M1 or newer) running macOS 12+. Intel Macs are not supported — torch/mlx are built for Apple Silicon only.
- A free **HuggingFace** account, to access the gated speaker-diarization model.

## 1. Download the app

Grab `video2text-v1.0.1-macos-arm64.zip` from the [latest release](https://github.com/neurosamAI/video2text/releases/latest) and unzip it. Put `video2text.app` wherever you like — moving it to `/Applications` lets you manage it like any other app.

No build step needed — the app bundles its own Python runtime and ffmpeg.

## 2. Run it

Double-click `video2text.app`. A native window opens — no browser required.

If macOS shows an "unidentified developer" warning, right-click the app in Finder → **Open** once to allow it. This bundle is fully self-contained: it works wherever you put it, with no separate Homebrew or runtime install.

## 3. Get access to the diarization model (one-time)

`pyannote/speaker-diarization-3.1` is a gated model on HuggingFace — it requires a free account, a one-time license agreement, and an access token.

1. Create a free account at [huggingface.co/join](https://huggingface.co/join) (skip if you already have one).
2. Agree to the license on both model pages:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Create a **Read**-scoped access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
4. Open the app — the **Settings** card at the top has a token field. Paste your token in and save.

Using video2text on more than one Mac? Each Mac needs its own token — HuggingFace's license agreement is per-account, so a shared token can't be baked into the app.

## Building from source instead

If you'd rather build the app yourself (for development, or to track `main`):

```bash
git clone https://github.com/neurosamAI/video2text
cd video2text
./build.sh
```

`build.sh` creates a virtualenv, installs dependencies (torch, mlx-whisper, pyannote.audio, speechbrain, fastapi, pywebview, and more), and syncs the code into a self-contained `video2text.app` bundle. Re-run it any time you change code under `app/` or `static/`.

Run it from source without building the app bundle:

```bash
python3.11 -m venv .venv          # Python 3.11 recommended
./.venv/bin/pip install -r requirements.txt
./run.sh                          # http://127.0.0.1:8765
```

During development, your HF token is read from `~/Library/Application Support/video2text/.env` (a project-root `.env` also works, see `.env.example`).

## Next steps

- [How It Works](/docs/how-it-works/) — the processing pipeline and the models behind it
- [Usage](/docs/usage/) — voice profiles, job history, rematch/relabel, export formats
- [Privacy & Security](/docs/privacy-security/) — what stays local, what doesn't
