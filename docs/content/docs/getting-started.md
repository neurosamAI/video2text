---
title: Getting Started
description: "Install video2text, set up model access, and run your first transcription."
weight: 2
---

## Requirements

- **Apple Silicon Mac** (M1 or newer) running macOS 12+. Intel Macs are not supported — torch/mlx are built for Apple Silicon only.
- **Python 3.11** recommended. (3.13/3.14 can hit compatibility issues with some ML packages.)
- A free **HuggingFace** account, to access the gated speaker-diarization model.

## 1. Clone and build

```bash
git clone https://github.com/neurosamAI/video2text
cd video2text
./build.sh
```

`build.sh` creates a virtualenv, installs all dependencies (torch, mlx-whisper, pyannote.audio, speechbrain, fastapi, pywebview, and more), and syncs the code into a self-contained `video2text.app` bundle. The first run downloads several gigabytes of ML dependencies — subsequent runs of `./build.sh` reuse the existing venv and just re-sync `app/` and `static/`.

If you'd rather set things up manually:

```bash
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## 2. Get access to the diarization model (one-time)

`pyannote/speaker-diarization-3.1` is a gated model on HuggingFace — it requires a free account, a one-time license agreement, and an access token.

1. Create a free account at [huggingface.co/join](https://huggingface.co/join) (skip if you already have one).
2. Agree to the license on both model pages:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Create a **Read**-scoped access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
4. Save it to `~/Library/Application Support/video2text/.env`:

   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   (For convenience while developing, a `.env` in the project root is also recognized. If you plan to use both the dev checkout and the packaged app, the Application Support path is preferred, so both always see the same token.)

## 3. Run it

**Desktop app (recommended):** double-click `video2text.app` in Finder. A native window opens — no browser needed. On first launch, if macOS shows an "unidentified developer" warning, right-click → Open once to allow it.

**Web server:** run `./run.sh`, then open [http://127.0.0.1:8765](http://127.0.0.1:8765) in a browser.

`video2text.app` is a fully independent bundle — it keeps working even if you delete the original project folder or move the app to `/Applications` (though you won't be able to `./build.sh` a moved app back to the latest code — build once before you move it).

## Next steps

- [How It Works](/docs/how-it-works/) — the processing pipeline and the models behind it
- [Usage](/docs/usage/) — voice profiles, job history, rematch/relabel, export formats
- [Privacy & Security](/docs/privacy-security/) — what stays local, what doesn't
