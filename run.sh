#!/bin/bash
# Runs video2text as a local web server (open http://127.0.0.1:8765 in a browser).
# For the native desktop window instead, double-click video2text.app.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "가상환경이 없습니다. 먼저 README.md의 설치 절차를 따라주세요."
  exit 1
fi

exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
