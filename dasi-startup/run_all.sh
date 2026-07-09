#!/usr/bin/env bash
# 다시,출근 창업 지원 트랙 기동 — FastAPI(:8091) + 정적 프론트(같은 포트 '/').
# venv 는 재취업 트랙(../dasi-chulgeun/.venv)을 공유한다(의존성 동일). 없으면 자체 생성.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/../dasi-chulgeun/.venv/Scripts/python.exe"       # 공유 venv(Windows)
[ -x "$PY" ] || PY="$ROOT/../dasi-chulgeun/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "[run] 공유 venv 없음 → 자체 .venv 생성 및 설치"
  python -m venv "$ROOT/.venv"
  PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$ROOT/.venv/Scripts/python.exe"
  "$PY" -m pip install --quiet -r "$ROOT/backend/requirements.txt"
fi
echo "[run] http://127.0.0.1:8091  (docs: /docs)"
cd "$ROOT/backend"
exec "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8091
