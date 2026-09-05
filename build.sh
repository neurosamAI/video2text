#!/bin/bash
# Builds two separate things:
#   1. ./.venv       — dev venv (Homebrew python3.11), for fast local iteration.
#   2. video2text.app — a FULLY INDEPENDENT distributable bundle: its own
#      standalone Python runtime (python-build-standalone, no Homebrew
#      dependency), its own copy of app/ and static/, and a self-contained
#      ffmpeg/ffprobe (bundled with all dylibs via dylibbundler, no Homebrew
#      dependency either). Can be moved to /Applications, or copied to any
#      other Apple Silicon Mac, independent of this project folder.
set -e
cd "$(dirname "$0")"

PY_STANDALONE_RELEASE="20260901"
PY_STANDALONE_VERSION="3.11.16"
PY_STANDALONE_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PY_STANDALONE_RELEASE}/cpython-${PY_STANDALONE_VERSION}%2B${PY_STANDALONE_RELEASE}-aarch64-apple-darwin-install_only.tar.gz"

BUNDLE="video2text.app/Contents/Resources"
mkdir -p "$BUNDLE"

# --- 0. app bundle skeleton (Info.plist + launcher) from packaging/ ---
# video2text.app/ itself is entirely build output (gitignored) — its
# hand-authored source lives in packaging/ instead, so a fresh clone never
# has a half-built .app-named folder sitting in the source tree.
mkdir -p "video2text.app/Contents/MacOS"
cp packaging/Info.plist "video2text.app/Contents/Info.plist"
cp packaging/launch "video2text.app/Contents/MacOS/launch"
chmod +x "video2text.app/Contents/MacOS/launch"
cp packaging/AppIcon.icns "$BUNDLE/AppIcon.icns"

# --- 1. dev venv (Homebrew-based, for local development only) ---
if [ ! -e .venv ]; then
  echo "[dev] .venv 생성 중..."
  python3.11 -m venv .venv
  .venv/bin/pip install --upgrade pip -q
  .venv/bin/pip install -r requirements.txt
fi

# --- 2. distributable bundle: standalone Python runtime ---
if [ ! -e "$BUNDLE/venv" ]; then
  echo "[dist] 독립 실행형 Python 런타임 다운로드 중..."
  curl -L -o /tmp/video2text-cpython.tar.gz "$PY_STANDALONE_URL"
  mkdir -p /tmp/video2text-cpython
  tar xzf /tmp/video2text-cpython.tar.gz -C /tmp/video2text-cpython
  mv /tmp/video2text-cpython/python "$BUNDLE/venv"
  rm -rf /tmp/video2text-cpython /tmp/video2text-cpython.tar.gz

  echo "[dist] 의존성 설치 중 (Homebrew와 무관한 독립 환경)..."
  "$BUNDLE/venv/bin/python3" -m ensurepip --upgrade -q
  "$BUNDLE/venv/bin/python3" -m pip install --upgrade pip -q
  "$BUNDLE/venv/bin/python3" -m pip install -r requirements.txt
fi

# --- 3. distributable bundle: self-contained ffmpeg/ffprobe ---
if [ ! -e "$BUNDLE/bin/ffmpeg" ]; then
  if ! command -v ffmpeg >/dev/null; then
    echo "ffmpeg가 필요합니다: brew install ffmpeg"
    exit 1
  fi
  if ! command -v dylibbundler >/dev/null; then
    echo "dylibbundler가 필요합니다: brew install dylibbundler"
    exit 1
  fi
  echo "[dist] ffmpeg/ffprobe를 독립 실행형으로 재포장 중..."
  mkdir -p "$BUNDLE/bin" "$BUNDLE/lib"
  cp "$(command -v ffmpeg)" "$BUNDLE/bin/ffmpeg"
  cp "$(command -v ffprobe)" "$BUNDLE/bin/ffprobe"
  dylibbundler -od -b \
    -x "$BUNDLE/bin/ffmpeg" \
    -x "$BUNDLE/bin/ffprobe" \
    -d "$BUNDLE/lib" \
    -p "@executable_path/../lib/"
fi

# --- 4. sync app code into the bundle ---
rsync -a --delete --exclude '__pycache__' app/ "$BUNDLE/app/"
rsync -a --delete static/ "$BUNDLE/static/"

echo "빌드 완료:"
echo "  - 개발용: ./.venv (프로젝트 폴더 안에서만 동작)"
echo "  - 배포용: video2text.app (독립적으로 이동/복사 가능)"
