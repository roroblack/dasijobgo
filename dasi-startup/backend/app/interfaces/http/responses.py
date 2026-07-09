# -*- coding: utf-8 -*-
"""interfaces/http/responses — 표준 응답 봉투 {ok,data,meta,error} (RULE §4).

meta.source 로 live/seed/fallback 을 항상 표기해 데이터 출처를 드러낸다(RULE §1).
"""
from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any, *, source: str = "live", **meta) -> dict:
    m = {"source": source}
    m.update(meta)
    return {"ok": True, "data": data, "meta": m, "error": None}


def err(message: str, *, code: str = "error", status: int = 400) -> JSONResponse:
    body = {"ok": False, "data": None, "meta": {"source": "n/a"},
            "error": {"code": code, "message": message}}
    return JSONResponse(status_code=status, content=body)
