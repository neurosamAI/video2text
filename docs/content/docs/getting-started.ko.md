---
title: 시작하기
description: "video2text를 다운로드하고, 모델 접근 권한을 설정한 뒤, 첫 전사를 실행합니다."
weight: 2
---

## 요구 사항

- macOS 12 이상을 실행하는 **Apple Silicon Mac** (M1 이상). Intel Mac은 지원되지 않습니다 — torch/mlx는 Apple Silicon 전용으로 빌드됩니다.
- 게이트된 화자 분리 모델에 접근하기 위한 무료 **HuggingFace** 계정.

## 1. 앱 다운로드

[최신 릴리즈](https://github.com/neurosamAI/video2text/releases/latest)에서 `video2text-v1.0.0-macos-arm64.zip`을 받아 압축을 풉니다. `video2text.app`은 원하는 위치에 두면 됩니다 — `/Applications`로 옮기면 다른 앱처럼 관리할 수 있습니다.

빌드 단계가 필요 없습니다 — 앱이 자체 Python 런타임과 ffmpeg를 함께 담고 있습니다.

## 2. 실행하기

`video2text.app`을 더블클릭합니다. 네이티브 창이 열립니다 — 브라우저가 필요 없습니다.

macOS가 "확인되지 않은 개발자" 경고를 표시하면, Finder에서 앱을 우클릭 → **열기**를 한 번 실행해 허용하세요. 이 번들은 완전히 독립적입니다: 별도의 Homebrew나 런타임 설치 없이, 어디에 두든 그대로 동작합니다.

## 3. 화자 분리 모델 접근 권한 얻기 (한 번만)

`pyannote/speaker-diarization-3.1`은 HuggingFace의 게이트된 모델입니다 — 무료 계정, 한 번의 라이선스 동의, 접근 토큰이 필요합니다.

1. [huggingface.co/join](https://huggingface.co/join)에서 무료 계정을 만듭니다 (이미 있다면 건너뛰세요).
2. 두 모델 페이지 모두에서 라이선스에 동의합니다:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)에서 **Read** 범위의 접근 토큰을 만듭니다.
4. 앱을 엽니다 — 상단의 **설정** 카드에 토큰 입력란이 있습니다. 토큰을 붙여넣고 저장하세요.

여러 Mac에서 video2text를 사용하시나요? 각 Mac마다 자체 토큰이 필요합니다 — HuggingFace의 라이선스 동의는 계정 단위이므로, 하나의 토큰을 앱에 미리 넣어둘 수 없습니다.

## 소스에서 직접 빌드하기

앱을 직접 빌드하고 싶다면 (개발용, 또는 `main` 브랜치를 추적하려는 경우):

```bash
git clone https://github.com/neurosamAI/video2text
cd video2text
./build.sh
```

`build.sh`는 가상환경을 만들고, 의존성(torch, mlx-whisper, pyannote.audio, speechbrain, fastapi, pywebview 등)을 설치한 뒤, 코드를 독립 실행형 `video2text.app` 번들로 동기화합니다. `app/`이나 `static/` 아래 코드를 변경할 때마다 다시 실행하세요.

앱 번들을 빌드하지 않고 소스에서 바로 실행하기:

```bash
python3.11 -m venv .venv          # Python 3.11 recommended
./.venv/bin/pip install -r requirements.txt
./run.sh                          # http://127.0.0.1:8765
```

개발 중에는 HF 토큰을 `~/Library/Application Support/video2text/.env`에서 읽습니다 (프로젝트 루트의 `.env`도 동작합니다. `.env.example` 참고).

## 다음 단계

- [동작 방식](/ko/docs/how-it-works/) — 처리 파이프라인과 그 뒤에 있는 모델들
- [사용법](/ko/docs/usage/) — 목소리 프로필, 작업 이력, 재매칭/재라벨링, 내보내기 포맷
- [프라이버시 & 보안](/ko/docs/privacy-security/) — 로컬에 남는 것과 그렇지 않은 것
