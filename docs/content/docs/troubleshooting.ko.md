---
title: 문제 해결
description: "자주 발생하는 오류와 해결 방법."
weight: 6
---

## "HF_TOKEN is not set"

[모델 접근 권한 설정](/ko/docs/getting-started/) 단계를 따라 HuggingFace 토큰을 만들고 `~/Library/Application Support/video2text/.env`에 저장하세요.

## 403 / gated repo 오류

이는 두 모델 페이지 모두에서 아직 라이선스에 동의하지 않았거나, 토큰에 Read 권한이 없다는 의미입니다:

- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) — "Agree and access repository"를 클릭하세요
- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) — "Agree and access repository"를 클릭하세요

## 첫 실행이 느려요

첫 변환에서는 모델 가중치(모델당 수백 MB~약 1GB)를 내려받습니다. 이는 딱 한 번만 발생합니다 — 이후에는 모든 것이 로컬에 캐시되어, 다음 실행부터는 훨씬 빨라집니다.

## "Intel Mac not supported" / 앱이 실행되지 않아요

video2text는 Apple Silicon을 특정해 빌드된 `torch`와 `mlx`에 의존합니다. Intel Mac용 빌드는 없으며, 계획도 없습니다 — Apple의 ML 프레임워크인 MLX 자체가 Intel Mac을 대상으로 하지 않기 때문입니다.

## macOS가 앱을 "확인되지 않은 개발자"로 차단해요

`video2text.app`을 우클릭 → **열기**를 한 번 실행하세요. macOS는 이후 실행부터 이 선택을 기억합니다.

## 코드 변경사항이 `video2text.app`에 반영되지 않아요

`./build.sh`를 다시 실행하세요 — `app/`과 `static/`을 번들로 다시 동기화합니다. 이미 원본 프로젝트 폴더 밖으로 `.app`을 옮겼다면(예: `/Applications`로), 이 방식으로는 더 이상 재동기화할 수 없습니다. 옮기기 전에 다시 빌드하거나, 새로 클론하세요.
