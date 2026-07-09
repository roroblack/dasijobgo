#!/usr/bin/env bash
# 다시,출근 프로토타입 기동 — FastAPI(:8090) + 정적 프론트(같은 포트 '/').
# 실행:  ./run_all.sh   (dasi-chulgeun 폴더에서)
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$ROOT/.venv/Scripts/python.exe"   # Windows Git Bash
if [ ! -x "$PY" ]; then
  echo "[run] .venv 없음 → 생성 및 설치"
  python -m venv "$ROOT/.venv"
  PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$ROOT/.venv/Scripts/python.exe"
  "$PY" -m pip install --quiet -r "$ROOT/backend/requirements.txt"
fi
echo "[run] http://127.0.0.1:8090  (docs: /docs)"
cd "$ROOT/backend"
exec "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8090
