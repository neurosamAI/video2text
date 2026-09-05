---
title: License
description: "video2text's own MIT license, and the licenses of the AI models it downloads at runtime."
weight: 7
---

## video2text

video2text's own code is released under the [MIT License](https://github.com/neurosamAI/video2text/blob/main/LICENSE).

## AI model licenses

video2text downloads several AI models at runtime — their weights are not bundled in the repository, and each user downloads them directly under their own HuggingFace account. Each model carries its own license:

| Model | Purpose | License |
|---|---|---|
| [`pyannote/speaker-diarization-3.1`](https://huggingface.co/pyannote/speaker-diarization-3.1) | Speaker diarization | MIT |
| [`pyannote/segmentation-3.0`](https://huggingface.co/pyannote/segmentation-3.0) | Speaker diarization (internal) | MIT |
| [`mlx-community/whisper-large-v3-turbo`](https://huggingface.co/mlx-community/whisper-large-v3-turbo) | Speech recognition | MIT |
| [`speechbrain/spkrec-ecapa-voxceleb`](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) | Speaker embedding (profile matching) | Apache 2.0 |

**A note on the SpeechBrain model**: its model card doesn't separately spell out the license of the VoxCeleb dataset it was trained on. Using the model itself is fine under Apache 2.0, but this particular point hasn't been fully settled industry-wide — worth keeping in mind if your use case is sensitive to training-data provenance.

## Contributing

Issues, PRs, and feedback are welcome at [github.com/neurosamAI/video2text](https://github.com/neurosamAI/video2text).
