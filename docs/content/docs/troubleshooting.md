---
title: Troubleshooting
description: "Common errors and how to resolve them."
weight: 6
---

## "HF_TOKEN is not set"

Follow the [model access setup](/docs/getting-started/) steps: create a HuggingFace token and save it to `~/Library/Application Support/video2text/.env`.

## 403 / gated repo error

This means either you haven't accepted the license on both model pages yet, or your token doesn't have Read access:

- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) — click "Agree and access repository"
- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) — click "Agree and access repository"

## First run is slow

The first conversion downloads model weights (hundreds of MB to ~1GB per model). This only happens once — everything is cached locally afterward, and subsequent runs are much faster.

## "Intel Mac not supported" / app won't launch

video2text depends on `torch` and `mlx` builds that target Apple Silicon specifically. There is no Intel Mac build, and none is planned, since MLX (Apple's ML framework) doesn't target Intel Macs.

## macOS blocks the app as "unidentified developer"

Right-click `video2text.app` → **Open** once. macOS will remember your choice for future launches.

## Code changes aren't showing up in `video2text.app`

Run `./build.sh` again — it re-syncs `app/` and `static/` into the bundle. If you already moved the `.app` out of the original project folder (e.g. to `/Applications`), it can no longer be re-synced this way; rebuild before moving it, or clone a fresh copy.
