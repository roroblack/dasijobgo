# -*- coding: utf-8 -*-
"""interfaces/http/health_router — 헬스체크 + 런타임 소스 상태(창업 트랙)."""
from __future__ import annotations

from fastapi import APIRouter

from app.config import APP_NAME
from app.infrastructure.data import business_repository, programs_repository
from app.infrastructure.llm import client
from app.infrastructure.store import memory_store
from app.interfaces.http.responses import ok

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return ok({
        "app": APP_NAME,
        "status": "up",
        "sessions": memory_store.count(),
        "sources": {
            "candidates": business_repository.SOURCE,  # seed
            "programs": programs_repository.SOURCE,     # seed
            "llm": "live" if client.available() else "fallback",
        },
    }, source="live")
