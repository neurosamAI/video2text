---
title: How It Works
description: "The pipeline video2text runs, the models behind it, and why the same pipeline handles both video calls and single-camera recordings."
weight: 3
---

## One pipeline, any recording

Whether a recording is a screen-split video call or a single camera pointed at a room full of people, the audio arrives the same way: one track, multiple voices mixed together. video2text doesn't try to separate "online meeting" from "offline meeting" — it treats every input as audio with an unknown number of speakers, and runs the same pipeline:

```
mp4 / audio file
      │
      ▼
1. extract audio       ffmpeg pulls the audio track (or reads it directly if the input is already audio)
      │
      ▼
2. diarize              pyannote/speaker-diarization-3.1 — "who spoke when", as time-stamped segments
      │
      ▼
3. transcribe           mlx-whisper (large-v3-turbo) — "what was said", Metal-accelerated on Apple Silicon
      │
      ▼
4. match speakers        compare each diarized segment's voice embedding against registered profiles
      │
      ▼
5. render                merge diarization + transcript + speaker labels into TXT / SRT / JSON
```

## The models

| Stage | Model | Why this one |
|---|---|---|
| Speaker diarization | [`pyannote/speaker-diarization-3.1`](https://huggingface.co/pyannote/speaker-diarization-3.1) | Strong accuracy, MIT-licensed, actively maintained |
| Speech recognition | [`mlx-community/whisper-large-v3-turbo`](https://github.com/ml-explore/mlx-examples/tree/main/whisper) | Whisper-quality transcription, MLX runtime built for Apple Silicon Metal acceleration |
| Speaker embedding | [`speechbrain/spkrec-ecapa-voxceleb`](https://github.com/speechbrain/speechbrain) | ECAPA-TDNN embeddings, a well-established approach for voice similarity comparison |

Diarization and transcription run as two independent passes over the same audio, then get merged by timestamp — a diarized segment `[00:12:34–00:12:41]` gets matched to whichever transcribed words fall in that window.

## Speaker matching, in detail

Diarization alone only tells you "Speaker 1", "Speaker 2" — it doesn't know names. video2text closes that gap with **voice profiles**:

1. You register a profile (a name + a short voice sample, either recorded live or extracted from an existing file).
2. video2text computes a speaker embedding for that sample using SpeechBrain's ECAPA-TDNN model.
3. For each diarized speaker segment in a new recording, it computes the same kind of embedding and compares it (cosine similarity) against every registered profile.
4. If the best match clears a confidence threshold, the segment is labeled with that profile's name instead of "Speaker 1".

This comparison is cheap relative to diarization and transcription, which is what makes [rematching](/docs/usage/) fast — it doesn't need to touch the audio again.

## Why not one combined model?

Diarization and transcription answer different questions ("who" vs. "what") and are trained on different objectives. Keeping them as separate stages — rather than a single end-to-end model — is what lets video2text swap in a different diarization or transcription model later, and what makes rematch/relabel possible without redoing the expensive steps.
