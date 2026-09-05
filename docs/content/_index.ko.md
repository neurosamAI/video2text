---
title: 홈
---

<div class="hero">
  <img src="/icon.png" alt="video2text" style="width:72px;height:72px;border-radius:18px;margin:0 auto 1.25rem;display:block;">
  <h1>video2text</h1>
  <p class="subtitle">mp4 영상이나 오디오 녹음을 화자 분리된 전사본으로 바꿔드립니다 — 전부 내 Mac 안에서. 어디에도 업로드되지 않습니다.</p>
  <div class="hero-buttons">
    <a href="https://github.com/neurosamAI/video2text/releases/latest" class="btn btn-primary">macOS용 다운로드</a>
    <a href="https://github.com/neurosamAI/video2text" class="btn btn-secondary">GitHub</a>
  </div>
</div>

<p style="text-align:center;">
  <img src="/screenshot.png" alt="video2text app window — drag-and-drop mp4 conversion, voice profile matching, and job history" style="max-width:100%;border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
</p>

## video2text란?

video2text는 macOS(Apple Silicon)용 **완전 로컬, 화자 분리 전사 앱**입니다. mp4나 오디오 파일 — 화상 회의 녹화본, 카메라 한 대로 찍은 오프라인 회의, 강연, 인터뷰 — 을 넣으면 화자별로 정리된 전사본을 만들어 줍니다.

```
[00:12:34] Alex: Hi everyone, let's start today's meeting.
[00:12:41] Jordan: Sure, I'll share last week's issues first.
```

음성 인식과 화자 분리 모두 **기기 안에서** 실행됩니다. 최초 실행 시 한 번 내려받는 모델 가중치를 제외하면, 어떤 오디오도 영상도 전사본도 여러분의 기기를 벗어나지 않습니다.

<div class="features">
  <div class="feature">
    <h3>완전 로컬</h3>
    <p>음성 인식(mlx-whisper)과 화자 분리(pyannote.audio) 모두 Apple Silicon Metal 가속으로 실행됩니다. 클라우드 업로드는 결코 없습니다.</p>
  </div>
  <div class="feature">
    <h3>내 목소리 자동 매칭</h3>
    <p>내 목소리를 한 번(10~20초) 등록해두면 이후 모든 전사본에서 자동으로 매칭됩니다 — "화자 1" 대신 실제 이름으로.</p>
  </div>
  <div class="feature">
    <h3>재매칭 & 재라벨링</h3>
    <p>잘못된 화자 매칭을 고치거나 프로필을 나중에 추가해도 — 전체 파이프라인을 다시 돌릴 필요가 없습니다. 몇 초 만에 재매칭하거나 재라벨링하세요.</p>
  </div>
  <div class="feature">
    <h3>독립 실행형 앱</h3>
    <p>video2text.app은 자체 Python 런타임, ffmpeg, ML 의존성을 모두 담고 있습니다. 다른 Apple Silicon Mac에 복사만 해도 바로 동작합니다.</p>
  </div>
  <div class="feature">
    <h3>3가지 내보내기 포맷</h3>
    <p>읽기 편한 TXT, 영상 자막용 SRT, 타임스탬프가 포함된 화자별 원본 블록의 JSON.</p>
  </div>
  <div class="feature">
    <h3>네이티브 데스크톱 UI</h3>
    <p>네이티브 macOS 창(pywebview) — 파일을 드래그 앤 드롭하고, 실시간으로 진행 상황을 확인하세요. 브라우저가 필요 없습니다.</p>
  </div>
</div>

## 동작 방식

```
Local file                         On this Mac only
───────────                        ─────────────────
1. extract audio   →  ffmpeg
2. diarize         →  pyannote/speaker-diarization-3.1   (who spoke when)
3. transcribe      →  mlx-whisper large-v3-turbo          (what was said)
4. match speakers   →  SpeechBrain ECAPA-TDNN embeddings   (registered voice profiles)
5. render           →  TXT / SRT / JSON
```

1~5단계 그 어느 과정도 네트워크를 거치지 않습니다. video2text가 네트워크에 접속하는 유일한 순간은 최초 실행 시 HuggingFace / Apple(mlx-community)에서 모델을 한 번 내려받을 때뿐입니다.

## 빠른 시작

빌드가 필요 없습니다 — 패키징된 앱을 내려받아 실행하세요:

1. [최신 릴리즈](https://github.com/neurosamAI/video2text/releases/latest)에서 `video2text-v1.0.0-macos-arm64.zip`을 다운로드하고 압축을 풉니다.
2. `video2text.app`을 더블클릭합니다. (macOS가 "확인되지 않은 개발자" 경고를 표시하면, 우클릭 → 열기를 한 번 실행하세요.)
3. 화자 분리 모델에 필요한 HuggingFace 접근 권한을 설정합니다(한 번만, 무료) — [시작하기](/ko/docs/getting-started/)를 참고하세요.

소스에서 직접 빌드하고 싶으신가요?

```bash
git clone https://github.com/neurosamAI/video2text
cd video2text
./build.sh      # builds video2text.app locally
./run.sh        # or run it as a local web server at http://127.0.0.1:8765
```

## 왜 로컬인가?

| | video2text | Otter.ai | Whisper API | Zoom AI Companion |
|---|:---:|:---:|:---:|:---:|
| 실행 위치 | **온디바이스** | 클라우드 | 클라우드 | 클라우드 |
| 파일 업로드 필요 | **불필요** | 필요 | 필요 | 필요 |
| 화자 분리 | **내장** | 내장 | 직접 구현 필요 | 내장 |
| 내 목소리 자동 매칭 | **지원** | 지원(계정 기반) | 미지원 | 미지원 |
| 전체 재실행 없는 재매칭 | **지원** | 미지원 | 미지원 | 미지원 |
| 오프라인 사용 | **지원** | 미지원 | 미지원 | 미지원 |
| 비용 | **무료, 오픈소스** | 구독 | 사용량 기반 | 부가 구독 |

video2text의 입장은 분명합니다: 녹화본이 민감한 내용 — 사내 회의, 채용 인터뷰, 고객 상담 — 이라면 그 방을 벗어날 필요가 없습니다.

## 실제 사용 시나리오

### "모든 팀 회의를 녹화하고 나중에 노트가 필요해요"

녹화본을 넣고, 팀원들의 목소리를 한 번만 등록해두면, 실제 이름으로 라벨링된 전사본을 얻을 수 있습니다 — 클라우드 전사 비용도, 제3자에게 업로드되는 녹화본도 없습니다.

### "녹화된 강연에 자막이 필요해요"

바로 SRT로 내보내서 영상 편집기에 넣으세요.

### "화자가 잘못 매칭됐어요 — 하지만 30분을 다시 기다리고 싶지 않아요"

빠진 목소리 프로필을 추가하고 **재매칭**을 누르세요. 화자 분리와 전사는 이미 끝나 있으므로 — 화자 매칭만 다시 실행됩니다.

## 누구를 위한 도구인가요?

- 회의, 인터뷰, 고객 상담을 녹화하지만 그 오디오가 외부로 나가는 것을 원하지 않는 팀
- 분당 클라우드 비용 없이 Whisper급 전사 품질을 원하는 모든 사람
- 업로드를 기다리기보다 로컬에서 15~40분을 쓰는 편이 나은 Apple Silicon Mac 사용자
- 직접 검사하고, 포크하고, 확장할 수 있는 화자 분리를 원하는 개발자와 연구자

## 실제 필요에서 시작된 프로젝트

video2text는 반복되는 문제 하나를 풀기 위한 주말 프로젝트로 시작됐습니다: 녹화된 회의를 텍스트로 남기되, 어디에도 업로드하지 않는 것. [Murry Jeong(comchangs)](https://github.com/comchangs)과 neurosam.AI가 배포 도구 [Tow](https://tow-cli.neurosam.ai)에 이어 공개하는 두 번째 오픈소스 프로젝트입니다.

<div class="line-glow"></div>

<p class="brand-footer">
  Created by <a href="https://github.com/comchangs">Murry Jeong</a> &middot; Supported by <a href="https://neurosam.ai">neurosam.AI</a> &middot; MIT License &middot; <a href="https://oss.neurosam.ai">Open Source</a>
</p>
