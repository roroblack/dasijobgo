# -*- coding: utf-8 -*-
"""main — FastAPI 부트스트랩. 응답 봉투 {ok,data,meta,error}(RULE §4).

- API 라우터(/health, /onboarding, /matching, /resume, /schedule, /interview)
- 정적 프론트(../frontend)를 '/' 에 마운트.
실행: backend/ 에서  uvicorn app.main:app --host 127.0.0.1 --port 8090
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import APP_NAME
from app.interfaces.http import (health_router, interview_router, matching_router,
                                 onboarding_router, resume_router, schedule_router,
                                 stt_router)
from app.interfaces.http.responses import err

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 데모 로컬 전용. 실서비스는 화이트리스트로 좁힌다.
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ---
app.include_router(health_router)
app.include_router(onboarding_router)
app.include_router(matching_router)
app.include_router(resume_router)
app.include_router(schedule_router)
app.include_router(interview_router)
app.include_router(stt_router)


# --- 에러도 동일 봉투로 ---
@app.exception_handler(StarletteHTTPException)
async def _http_exc(_req, exc: StarletteHTTPException):
    return err(str(exc.detail), code="http_error", status=exc.status_code)


@app.exception_handler(RequestValidationError)
async def _validation_exc(_req, exc: RequestValidationError):
    return err(f"요청 형식 오류: {exc.errors()}", code="validation_error", status=422)


# --- 정적 프론트 마운트(맨 마지막: API 경로를 가리지 않게) ---
_FRONTEND = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
_FRONTEND = os.path.abspath(_FRONTEND)
if os.path.isdir(_FRONTEND):
    app.mount("/", StaticFiles(directory=_FRONTEND, html=True), name="frontend")
else:
    print(f"[startup][WARN] frontend 디렉토리 없음: {_FRONTEND} - API 만 동작")
