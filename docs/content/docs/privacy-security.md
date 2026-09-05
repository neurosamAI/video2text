---
title: Privacy & Security
description: "What runs locally, what touches the network, and how your HuggingFace token and recordings are handled."
weight: 5
---

## What stays on your Mac

Every processing step — audio extraction, speaker diarization, transcription, and voice matching — runs locally on your machine using Apple Silicon (Metal) acceleration. Your recordings, the resulting transcripts, and any voice profiles you register never get uploaded anywhere by video2text.

## The only network calls video2text makes

- **One-time model downloads**: the first time you run diarization, transcription, or speaker embedding, the corresponding model weights (a few hundred MB to ~1GB each) are downloaded from HuggingFace / Apple (mlx-community) and cached locally. After that, video2text works fully offline.
- **Version check** (docs site only, not the app itself): this documentation site pings the GitHub API to display the latest release tag. The app itself makes no such call.

No recording, transcript, or voice sample is ever sent to neurosam.AI, HuggingFace, or any other server as part of normal use.

## Your HuggingFace token

`pyannote/speaker-diarization-3.1` is a gated model, so video2text needs a **Read**-scoped HuggingFace access token to download it. That token:

- Is stored locally in `~/Library/Application Support/video2text/.env` (or a project-root `.env` during development)
- Is used only to authenticate the one-time model download from HuggingFace
- Is per-user — HuggingFace's gating is account-based, so each person deploying video2text needs their own token; a shared token can't be baked into the app

Treat this token like any other credential: don't commit it to a public repository, and don't share it as if it were a public app config value.

## Sample recordings

The project's own repository does not include any real meeting recordings — `sample/` (used only for local development and testing) is explicitly excluded via `.gitignore` and never pushed. If you fork or extend video2text, keep the same discipline: recordings, voice samples, and anything containing another person's speech should stay out of version control.

## Distributing the app to other Macs

Because `video2text.app` is a fully self-contained bundle (its own Python runtime, ffmpeg, and ML dependencies), it can be copied to another Apple Silicon Mac (AirDrop, USB, etc.) without installing anything system-wide. Each Mac still needs its own HuggingFace token and will download model weights on first run — those two things are inherently per-device/per-user and can't be pre-baked into a shared bundle.
