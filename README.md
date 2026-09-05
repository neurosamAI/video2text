<p align="center">
  <img src="docs/icon.png" width="120" alt="video2text icon" />
</p>

<p align="center">
  <b>English</b> | <a href="README.ko.md">한국어</a>
</p>

<h1 align="center">video2text</h1>

<p align="center">Turn Webex recordings into speaker-diarized text, entirely on your Mac — nothing gets uploaded to the internet.</p>

<p align="center">
  <a href="https://github.com/neurosamAI/video2text/releases/latest">
    <img src="https://img.shields.io/github/v/release/neurosamAI/video2text?label=%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C&color=4f7fff" alt="Download the latest release" />
  </a>
</p>

<p align="center">
  <img src="docs/screenshot.png" width="720" alt="video2text app screenshot" />
</p>

video2text is a fully local app that takes an mp4 file (typically a Webex recording) and produces a speaker-diarized
transcript. Whether it's an online meeting (split screen) or an in-person meeting recorded with a single camera and
mixed audio, the same problem applies: multiple speakers are mixed into one audio track. So both cases go through the
same pipeline (audio-based speaker diarization).

All processing (speech recognition, speaker diarization) runs locally on this Mac (Apple Silicon), and none of your
files ever leave the machine. The only exception is a one-time download of each AI model's weights from HuggingFace /
Apple (mlx-community) on first run.

---

## Download and use immediately

No need to build the code — you can just grab the finished app and start using it.

### 1. Download the app

Grab `video2text-vX.Y.Z-macos-arm64.zip` from the **[Releases page](https://github.com/neurosamAI/video2text/releases/latest)**
and unzip it. Put `video2text.app` wherever you like (moving it to `/Applications` lets you manage it like any other app).

> Apple Silicon Mac (M1 or newer), macOS 12 or later only. It does not run on Intel Macs.

### 2. Run it

Double-click `video2text.app`. A native app window opens — no browser required.

If macOS shows an "unidentified developer" warning, **right-click the app in Finder → Open** once to allow it.

This app is a fully self-contained bundle — it includes its own Python runtime and its own ffmpeg (no separate
Homebrew or other install needed), so it runs as soon as you download it.

### 3. Set up access to the diarization model (one-time, required)

`pyannote/speaker-diarization-3.1`, used for speaker diarization, is a gated model on HuggingFace, so it requires a
free account, a license agreement, and an access token.

1. Create a free account at https://huggingface.co/join (skip if you already have one).
2. Click "Agree and access repository" on each of these two model pages to agree to the license:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. Create a token with Read access at https://huggingface.co/settings/tokens via "New token".
4. Open the app — the "Settings" card at the top has a token field. Paste in the token you got and save it.

To use this app on another Mac, you'll need to repeat this procedure once on that Mac too (with your own account) —
the license agreement is per-account, so you can't just share a token and paste it in.

### 4. How to use it

1. **Register your own voice profile** (optional, but recommended): enter your name and either "Record to register"
   or upload an audio/video file. Read the sentence shown on screen clearly for about 10–20 seconds somewhere quiet.
   Once registered, that speaker will automatically show up under the name you registered instead of "Speaker 1" in
   future conversion results. You can register other people too (colleagues, etc.) so they get matched as well.
2. **Convert an mp4**: drag in a file, or use "Choose in Finder" (uses the file in place, without copying it), then
   check which profiles to match for this conversion and click "Start conversion." If you have a rough idea of how
   many attendees there were, entering it under "Estimated speaker count" helps diarization accuracy.
3. Progress (extract audio → diarize → transcribe → match speakers → done) is shown in real time.
4. Once done, results are saved in TXT / SRT / JSON format (default location: `~/Downloads/video2text`, changeable in
   Settings).
   - TXT: an easy-to-read transcript in the form `[00:12:34] Alex: Hi everyone...`
   - SRT: for video subtitles
   - JSON: raw data with per-speaker blocks and timestamps

### Processing time notes

On Apple Silicon (M2 Pro as a baseline), diarization takes about 10–30% of the audio's length, and transcription is
generally faster than real time. Example: a 2-hour recording → 15–40 minutes for diarization, roughly 10–20 minutes
for transcription (can vary by file/model).

### Troubleshooting

- **"HF_TOKEN is not set"**: follow the "Set up access to the diarization model" steps above.
- **403 / gated repo error**: you haven't agreed to the license on both model pages, or your token doesn't have Read
  access.
- **First run is slow**: it's downloading the model weights for the first time (several hundred MB to ~1GB). Runs
  after that are cached and faster.

---

## For developers

Everything from here on is for developers who want to modify or build the code directly.

### Components

- **Speaker diarization**: [pyannote.audio](https://github.com/pyannote/pyannote-audio) (`pyannote/speaker-diarization-3.1`)
- **Speech recognition**: [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) (Apple Silicon Metal acceleration, `large-v3-turbo`)
- **Automatic voice matching**: compares registered voices against diarization output using SpeechBrain ECAPA-TDNN speaker embeddings
- **Backend**: FastAPI (local web server)
- **Desktop shell**: pywebview (native macOS window) — `video2text.app`

### Dev build vs. packaged build

- **Development**: edit the code in this project folder (`app/`, `static/`) and test by running the server directly, as shown below.
- **Packaged (distribution)**: running `./build.sh` produces `video2text.app` — its own Python runtime and every
  dependency (torch, mlx-whisper, pyannote.audio, speechbrain, fastapi, pywebview, etc.) get bundled whole into
  `Contents/Resources/venv`, and the app code is copied into `Contents/Resources/app` and
  `Contents/Resources/static` too, making it a **fully self-contained bundle** (it keeps working even if you delete
  or move this project folder, or move `video2text.app` to `/Applications`). The `.app`'s own skeleton
  (`Info.plist`, launch script, icon) lives in `packaging/`, and `video2text.app/` itself is entirely a build
  artifact produced by `build.sh`, so it's not checked into the repo.
  (The `.venv` at the project root is actually a symlink to `video2text.app/Contents/Resources/venv`, so the dev
  venv and the packaged venv share the same underlying files — no need to maintain two multi-gigabyte sets of ML
  dependencies.)

To carry code changes over into the packaged app:

```bash
./build.sh
```

This script copies `app/`, `static/`, and `packaging/` back into the bundle (the Python runtime/ffmpeg are only
downloaded once) to bring it up to date.

### Install (one-time)

```bash
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Or just run `./build.sh`, which creates the venv, installs dependencies, and syncs the app bundle all in one step.

(Python 3.11 recommended — 3.13/3.14 may have compatibility issues with some ML packages.)

During development, your HF token is stored at `~/Library/Application Support/video2text/.env` (see `.env.example`),
and a `.env` at the project root is also recognized as an alternate path — but if you want the dev and packaged app
to always see the same token, the Application Support path is recommended.

### Running from source (terminal)

```bash
./run.sh
```

Then open http://127.0.0.1:8765 in a browser.

### Distributing to another Mac

`video2text.app` is fully self-contained — it bundles its own Python runtime (no Homebrew needed) and its own
ffmpeg (dylibs included, no Homebrew needed), so **copying just `video2text.app` to another Apple Silicon Mac (via
AirDrop, etc.) runs it immediately with no separate install**. To publish a new version on GitHub Releases:

```bash
./build.sh
ditto -c -k --sequesterRsrc --keepParent video2text.app video2text-vX.Y.Z-macos-arm64.zip
gh release create vX.Y.Z video2text-vX.Y.Z-macos-arm64.zip --title "video2text vX.Y.Z" --notes "..."
```

It cannot be distributed to Intel Macs (torch/mlx and other dependencies are built for Apple Silicon only).

## License

This project's own code is under the [MIT License](LICENSE). The AI models it downloads automatically at runtime
each carry their own license (model weights aren't included in the repo — each user downloads them directly):

| Model | Purpose | License |
|---|---|---|
| `pyannote/speaker-diarization-3.1` | Speaker diarization | MIT |
| `pyannote/segmentation-3.0` | Speaker diarization (internal) | MIT |
| `mlx-community/whisper-large-v3-turbo` | Speech recognition | MIT |
| `speechbrain/spkrec-ecapa-voxceleb` | Speaker embedding (profile matching) | Apache 2.0 |

Note: the SpeechBrain model card doesn't separately specify a license for the VoxCeleb dataset used to train it —
using the model itself is fine under Apache 2.0, but this is a point the industry hasn't fully settled yet.
