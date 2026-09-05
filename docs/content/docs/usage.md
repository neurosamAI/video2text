---
title: Usage
description: "Voice profiles, converting a file, job history, rematch/relabel, and export formats."
weight: 4
---

## 1. Register voice profiles (optional, but recommended)

Enter a name and either:

- **Record it live** — read the on-screen prompt aloud for 10–20 seconds in a quiet room, or
- **Upload a sample** — an existing audio or video file that contains that person's voice.

Register as many people as you like (teammates, recurring meeting participants). Every registered profile is checked against every new conversion.

Manage profiles from the settings area: list registered profiles, inspect or delete individual voice samples, and remove a profile entirely.

## 2. Convert a file

Drag an mp4 or audio file onto the window (or click to choose one), check which voice profiles to match against for this conversion, and start. Progress is shown live through each pipeline stage: extract audio → diarize → transcribe → match speakers → done.

## 3. Job history

Every conversion is kept as a job you can revisit later:

- List past jobs and re-open any of them
- Cancel a job that's still running
- Delete a job you no longer need

## 4. Rematch & relabel

Two ways to fix a transcript without rerunning the expensive pipeline stages (diarization + transcription):

- **Rematch** — re-run only the voice-profile matching step, e.g. after adding a profile you hadn't registered yet, or after tuning which profiles to include. Diarization and transcription results are reused as-is.
- **Relabel** — manually override a speaker's label for a job (e.g. correct a mismatch by hand, or label an unregistered speaker by name).

Both act on an existing job's already-computed diarization and transcript, so they finish in seconds rather than minutes.

## 5. Export

Every completed job can be downloaded in three formats:

| Format | Use it for |
|---|---|
| **TXT** | A readable transcript: `[00:12:34] Alex: Hi everyone...` |
| **SRT** | Subtitles for a video, timed to the diarized segments |
| **JSON** | Raw data — per-speaker blocks with timestamps, for scripting or further processing |

## Settings

The settings panel lets you set (and persist) your HuggingFace token, and reveal the folder a job's files live in (via macOS Finder) for manual inspection.
