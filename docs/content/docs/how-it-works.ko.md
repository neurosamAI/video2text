---
title: 동작 방식
description: "video2text가 실행하는 파이프라인, 그 뒤에 있는 모델들, 그리고 같은 파이프라인이 화상 회의와 단일 카메라 녹화를 모두 처리할 수 있는 이유."
weight: 3
---

## 파이프라인 하나로 모든 녹화를 처리합니다

녹화본이 화면 분할된 화상 회의든, 사람들로 가득한 방을 향한 카메라 한 대로 찍은 것이든, 오디오는 같은 형태로 도착합니다: 트랙 하나에 여러 목소리가 섞여 있는 형태로요. video2text는 "온라인 회의"와 "오프라인 회의"를 구분하려 하지 않습니다 — 모든 입력을 화자 수를 알 수 없는 오디오로 취급하고, 동일한 파이프라인을 실행합니다:

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

## 사용하는 모델들

| 단계 | 모델 | 선택 이유 |
|---|---|---|
| 화자 분리 | [`pyannote/speaker-diarization-3.1`](https://huggingface.co/pyannote/speaker-diarization-3.1) | 높은 정확도, MIT 라이선스, 활발한 유지보수 |
| 음성 인식 | [`mlx-community/whisper-large-v3-turbo`](https://github.com/ml-explore/mlx-examples/tree/main/whisper) | Whisper급 전사 품질, Apple Silicon Metal 가속을 위해 만들어진 MLX 런타임 |
| 화자 임베딩 | [`speechbrain/spkrec-ecapa-voxceleb`](https://github.com/speechbrain/speechbrain) | ECAPA-TDNN 임베딩, 목소리 유사도 비교에 널리 쓰이는 검증된 방식 |

화자 분리와 전사는 같은 오디오에 대해 서로 독립적인 두 번의 처리로 실행된 뒤, 타임스탬프 기준으로 병합됩니다 — `[00:12:34–00:12:41]`로 분리된 구간은 그 시간대에 포함되는 전사 텍스트와 매칭됩니다.

## 화자 매칭, 자세히 보기

화자 분리만으로는 "화자 1", "화자 2"까지만 알 수 있습니다 — 이름은 알지 못합니다. video2text는 **목소리 프로필**로 이 간극을 메웁니다:

1. 프로필을 등록합니다(이름 + 짧은 목소리 샘플. 실시간 녹음이든 기존 파일에서 추출한 것이든 상관없습니다).
2. video2text는 SpeechBrain의 ECAPA-TDNN 모델을 사용해 해당 샘플의 화자 임베딩을 계산합니다.
3. 새 녹화본에서 화자 분리된 각 구간에 대해 같은 방식의 임베딩을 계산하고, 등록된 모든 프로필과 코사인 유사도를 비교합니다.
4. 가장 근접한 매칭이 신뢰도 임계값을 넘으면, 해당 구간은 "화자 1" 대신 그 프로필의 이름으로 라벨링됩니다.

이 비교 작업은 화자 분리나 전사에 비해 비용이 훨씬 적게 들며, 이 덕분에 [재매칭](/ko/docs/usage/)이 빠릅니다 — 오디오를 다시 건드릴 필요가 없기 때문입니다.

## 왜 하나로 합친 모델을 쓰지 않나요?

화자 분리와 전사는 서로 다른 질문("누가"와 "무엇을")에 답하며, 서로 다른 목적으로 학습됩니다. 이를 단일 엔드투엔드 모델이 아니라 별개의 단계로 유지하는 것이야말로, 이후에 다른 화자 분리 모델이나 전사 모델로 교체할 수 있게 해주고, 비용이 큰 단계를 다시 거치지 않고도 재매칭/재라벨링을 가능하게 해줍니다.
