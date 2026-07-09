# 다시,출근 프로토타입 기동 — FastAPI(:8090) + 정적 프론트(같은 포트 '/').
# 실행:  .\run_all.ps1      (dasi-chulgeun 폴더에서)
# 종료:  Ctrl+C
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
  Write-Host "[run] .venv 없음 → 생성 및 설치" -ForegroundColor Yellow
  python -m venv (Join-Path $root ".venv")
  & $py -m pip install --quiet -r (Join-Path $root "backend\requirements.txt")
}
Write-Host "[run] 백엔드+프론트 기동 → http://127.0.0.1:8090  (docs: /docs)" -ForegroundColor Cyan
Push-Location (Join-Path $root "backend")
try {
  & $py -m uvicorn app.main:app --host 127.0.0.1 --port 8090
}
finally { Pop-Location }
