---
title: 라이선스
description: "video2text 자체의 MIT 라이선스와, 실행 중에 내려받는 AI 모델들의 라이선스."
weight: 7
---

## video2text

video2text 자체 코드는 [MIT License](https://github.com/neurosamAI/video2text/blob/main/LICENSE)로 공개되어 있습니다.

## AI 모델 라이선스

video2text는 실행 중에 여러 AI 모델을 내려받습니다 — 이 가중치들은 저장소에 함께 배포되지 않으며, 각 사용자가 자신의 HuggingFace 계정으로 직접 내려받습니다. 각 모델은 저마다의 라이선스를 따릅니다:

| 모델 | 용도 | 라이선스 |
|---|---|---|
| [`pyannote/speaker-diarization-3.1`](https://huggingface.co/pyannote/speaker-diarization-3.1) | 화자 분리 | MIT |
| [`pyannote/segmentation-3.0`](https://huggingface.co/pyannote/segmentation-3.0) | 화자 분리 (내부용) | MIT |
| [`mlx-community/whisper-large-v3-turbo`](https://huggingface.co/mlx-community/whisper-large-v3-turbo) | 음성 인식 | MIT |
| [`speechbrain/spkrec-ecapa-voxceleb`](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) | 화자 임베딩 (프로필 매칭) | Apache 2.0 |

**SpeechBrain 모델에 대한 참고 사항**: 이 모델의 모델 카드에는 학습에 사용된 VoxCeleb 데이터셋 자체의 라이선스가 별도로 명시되어 있지 않습니다. 모델 자체를 사용하는 것은 Apache 2.0 하에서 문제가 없지만, 이 특정 지점은 업계 전반에서 아직 완전히 정리되지 않았습니다 — 학습 데이터의 출처에 민감한 용도로 사용한다면 유의할 필요가 있습니다.

## 기여하기

이슈, PR, 피드백 모두 [github.com/neurosamAI/video2text](https://github.com/neurosamAI/video2text)에서 환영합니다.
