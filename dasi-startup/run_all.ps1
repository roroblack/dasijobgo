# 다시,출근 창업 지원 트랙 기동 — FastAPI(:8091) + 정적 프론트(같은 포트 '/').
# venv 는 재취업 트랙(..\dasi-chulgeun\.venv)을 공유. 실행:  .\run_all.ps1   종료: Ctrl+C
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$py = Join-Path $root "..\dasi-chulgeun\.venv\Scripts\python.exe"   # 공유 venv
if (-not (Test-Path $py)) {
  Write-Host "[run] 공유 venv 없음 → 자체 .venv 생성 및 설치" -ForegroundColor Yellow
  $py = Join-Path $root ".venv\Scripts\python.exe"
  python -m venv (Join-Path $root ".venv")
  & $py -m pip install --quiet -r (Join-Path $root "backend\requirements.txt")
}
Write-Host "[run] 창업 트랙 기동 → http://127.0.0.1:8091  (docs: /docs)" -ForegroundColor Cyan
Push-Location (Join-Path $root "backend")
try {
  & $py -m uvicorn app.main:app --host 127.0.0.1 --port 8091
}
finally { Pop-Location }
