# -*- coding: utf-8 -*-
"""interfaces/http/stt_router — 음성 입력 전사(STEP 1 온보딩 마이크). 오디오 업로드 → 텍스트."""
from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.domain import slots
from app.infrastructure import stt
from app.interfaces.http.responses import err, ok

router = APIRouter(prefix="/stt", tags=["stt"])


@router.post("")
async def transcribe(audio: UploadFile = File(...)):
    """멀티파트 오디오(webm/wav 등) → 한국어 전사 + 핵심 슬롯 추출(규칙).

    하이브리드의 '빠른 규칙 층': 전사 텍스트에서 직무·연수·지역·자격만 뽑아 즉시 반환.
    잡담은 사전에 없으면 자연히 버려진다. LLM 정제는 상위(온보딩) 계층 몫.
    """
    data = await audio.read()
    if stt.backend_status() != "ready":
        return err("STT 미설정 — 서버에 faster-whisper 필요(브라우저 텍스트 입력으로 대체하세요)",
                   code="stt_unavailable", status=503)
    text = stt.transcribe(data) or ""
    return ok({"text": text, "chars": len(text), "slots": slots.extract(text)}, source="local")
