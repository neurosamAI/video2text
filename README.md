# video2text

mp4 파일(주로 Webex 녹화본)을 넣으면 화자 분리(diarization)된 텍스트 전사본을 만들어주는 완전 로컬 앱입니다.
온라인 회의(화면 분할)든 오프라인 회의 녹화(단일 카메라 + 믹스된 오디오)든, 오디오 트랙 하나에 여러 화자가 섞여
들어온다는 점은 동일하므로 같은 파이프라인(오디오 기반 화자 분리)으로 처리합니다.

모든 처리(음성 인식, 화자 분리)는 이 Mac(Apple Silicon) 안에서 로컬로 실행되며, 업로드한 파일이 외부로 전송되지
않습니다. 단, 처음 실행 시 각 AI 모델 가중치를 HuggingFace / Apple(mlx-community)에서 한 번 다운로드합니다.

## 구성

- **화자 분리**: [pyannote.audio](https://github.com/pyannote/pyannote-audio) (`pyannote/speaker-diarization-3.1`)
- **음성 인식**: [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) (Apple Silicon Metal 가속, `large-v3-turbo`)
- **내 목소리 자동 매칭**: SpeechBrain ECAPA-TDNN 화자 임베딩으로 등록된 목소리와 화자분리 결과를 비교
- **백엔드**: FastAPI (로컬 웹 서버)
- **데스크톱 셸**: pywebview (네이티브 macOS 창) — `video2text.app`

## 개발용 vs 배포용

- **개발**: 이 프로젝트 폴더(`app/`, `static/`)에서 코드를 수정하고, 아래처럼 직접 서버를 띄워 테스트합니다.
- **배포(패키징)**: `video2text.app`은 완전히 독립된 앱 번들입니다. 자체 Python 런타임과 모든 의존성
  (torch, mlx-whisper, pyannote.audio, speechbrain, fastapi, pywebview 등)이 `video2text.app/Contents/Resources/venv`
  안에 통째로 들어있고, 앱 코드도 `Contents/Resources/app`, `Contents/Resources/static`에 복사되어 있어서
  **이 프로젝트 폴더를 지우거나 다른 곳으로 옮겨도, `video2text.app`을 `/Applications`로 옮겨도 그대로 동작**합니다.
  (프로젝트 루트의 `.venv`는 실제로는 `video2text.app/Contents/Resources/venv`를 가리키는 심볼릭 링크라서,
  개발용 venv와 배포용 venv가 같은 실체를 공유합니다 — 수 GB짜리 ML 의존성을 두 벌 유지할 필요가 없습니다.)

코드를 수정한 뒤 배포용 앱에 반영하려면:

```bash
./build.sh
```

이 스크립트는 `app/`, `static/`를 번들 안으로 다시 복사하고(venv는 최초 1회만 생성) 최신 상태로 맞춰줍니다.

## 설치 (최초 1회)

```bash
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

또는 그냥 `./build.sh`를 실행하면 venv 생성 + 의존성 설치 + 앱 번들 동기화까지 한 번에 됩니다.

(Python 3.11 권장 — 3.13/3.14는 일부 ML 패키지 호환성 문제가 있을 수 있습니다.)

### 화자분리 모델 접근 권한 (최초 1회, 필수)

`pyannote/speaker-diarization-3.1`은 HuggingFace의 gated 모델이라 무료 계정과 라이선스 동의, 액세스 토큰이 필요합니다.

1. https://huggingface.co/join 에서 무료 계정 생성 (이미 있으면 생략)
2. 아래 두 모델 페이지에서 각각 "Agree and access repository" 클릭해 라이선스 동의
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. https://huggingface.co/settings/tokens 에서 "New token" → Read 권한으로 토큰 생성
4. `~/Library/Application Support/video2text/.env` 파일을 만들고 아래처럼 저장 (`.env.example` 참고):
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   (개발 중 프로젝트 루트에서 직접 돌릴 때 편하도록, 프로젝트 루트의 `.env`도 대체 경로로 함께 인식합니다.
   단, 개발용/배포용 앱이 항상 같은 토큰을 보게 하려면 위 Application Support 경로 쪽을 권장합니다.)

## 실행

### 방법 1 — 데스크톱 앱 (권장)

Finder에서 `video2text.app`을 더블클릭하세요. 네이티브 창이 뜨고 브라우저 없이 바로 사용할 수 있습니다.
(처음 실행 시 macOS가 "확인되지 않은 개발자" 경고를 띄우면, 우클릭 → 열기 로 한 번 허용해주세요.)

완전히 독립된 번들이라 `/Applications`로 옮기거나 원본 프로젝트 폴더를 지워도 그대로 동작합니다
(단, 옮긴 뒤에는 `./build.sh`로 다시 최신화할 수 없으니 배포 전 최종 버전으로 한 번 빌드해두세요).

### 방법 2 — 터미널에서 웹 서버로 실행

```bash
./run.sh
```

그다음 브라우저에서 http://127.0.0.1:8765 접속.

## 사용법

1. **내 목소리 프로필 등록** (선택사항, 하지만 추천): 이름을 입력하고 "녹음해서 등록" 또는 오디오/영상 파일을 업로드합니다.
   화면에 뜨는 문장을 조용한 곳에서 10~20초 정도 또렷하게 읽으면 됩니다. 등록해두면 이후 변환 결과에서 해당 화자가
   자동으로 "화자 1" 대신 등록한 이름으로 표시됩니다. 여러 사람(동료 등)도 등록해서 함께 매칭할 수 있습니다.
2. **mp4 변환**: 파일을 드래그하거나 클릭해서 선택한 뒤, 이번 변환에서 매칭할 프로필을 체크하고 "변환 시작"을 누릅니다.
3. 진행 상황(오디오 추출 → 화자 분리 → 음성 인식 → 화자 매칭 → 완료)이 실시간으로 표시됩니다.
4. 완료되면 TXT / SRT / JSON 형식으로 결과를 내려받을 수 있습니다.
   - TXT: `[00:12:34] 홍길동: 안녕하세요...` 형태의 읽기 편한 전사본
   - SRT: 영상 자막용
   - JSON: 화자별 블록 + 타임스탬프 원본 데이터

## 다른 Mac에 배포하기

`video2text.app`은 완전히 독립적입니다 — 자체 Python 런타임(Homebrew 불필요)과 자체 ffmpeg(dylib까지 전부
포함, Homebrew 불필요)를 담고 있어서, **다른 Apple Silicon Mac에 `video2text.app`만 복사(AirDrop 등)해도
별도 설치 없이 바로 실행**됩니다. 단, 아래 두 가지는 각 Mac에서 한 번씩 필요합니다 (기기별로 다를 수밖에 없는
부분입니다):

1. **HF 토큰**: 앱을 열면 맨 위 "설정" 카드에 토큰 입력창이 보입니다. 사용자마다 본인 HuggingFace 계정의
   토큰을 넣어야 합니다 (라이선스 동의가 사용자 단위라 공유 토큰을 넣어둘 수 없습니다).
2. **첫 실행 시 모델 다운로드**: mlx-whisper / pyannote / speechbrain 모델 가중치(수 GB)를 처음 한 번은
   인터넷에서 받습니다. 이후로는 로컬에 캐시되어 오프라인으로도 동작합니다.

Intel Mac에는 배포할 수 없습니다 (torch/mlx 등이 Apple Silicon용으로 빌드되어 있음).

코드를 수정한 뒤에는 `./build.sh`를 다시 실행해 `video2text.app`에 최신 코드를 반영하세요
(Python 런타임과 ffmpeg는 이미 있으면 재사용하고, `app/`·`static/`만 새로 복사합니다).

## 처리 시간 참고

Apple Silicon(M2 Pro 기준)에서 화자 분리는 오디오 길이의 약 10~30%, 전사는 대체로 실시간보다 빠릅니다.
예: 2시간 녹화 → 화자 분리 15~40분, 전사 10~20분 내외 (파일/모델에 따라 달라질 수 있음).

## 문제 해결

- **"HF_TOKEN이 설정되지 않았습니다"**: 위 "화자분리 모델 접근 권한" 절차를 진행하세요.
- **403 / gated repo 오류**: 두 모델 페이지에서 라이선스 동의를 안 했거나, 토큰에 Read 권한이 없는 경우입니다.
- **첫 실행이 느림**: 모델 가중치를 처음 다운로드하는 중입니다 (수백 MB~1GB대). 이후 실행부터는 캐시되어 빨라집니다.

## 라이선스

이 프로젝트 자체 코드는 [MIT License](LICENSE)입니다. 실행 중 자동으로 내려받는 AI 모델의 라이선스는 각각 다음과 같습니다 (모델 가중치는 저장소에 포함되지 않고, 각 사용자가 직접 내려받습니다):

| 모델 | 용도 | 라이선스 |
|---|---|---|
| `pyannote/speaker-diarization-3.1` | 화자 분리 | MIT |
| `pyannote/segmentation-3.0` | 화자 분리(내부) | MIT |
| `mlx-community/whisper-large-v3-turbo` | 음성 인식 | MIT |
| `speechbrain/spkrec-ecapa-voxceleb` | 화자 임베딩(프로필 매칭) | Apache 2.0 |

참고: SpeechBrain 모델 카드는 학습에 쓰인 VoxCeleb 데이터셋 자체의 라이선스는 별도로 명시하지 않습니다 — 모델 사용 자체는 Apache 2.0으로 문제없지만, 이 지점은 아직 업계 전반에서 명확히 정리되지 않은 부분입니다.
