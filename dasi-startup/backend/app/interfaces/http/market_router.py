# -*- coding: utf-8 -*-
"""interfaces/http/market_router — 후보 상권·리스크 리포트(STEP 5). 수치는 seed + 출처 병기."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import market_usecase
from app.interfaces.http.responses import err, ok

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/{cid}")
def report(cid: str):
    r = market_usecase.report(cid)
    if r is None:
        return err("해당 업종 후보를 찾을 수 없어요", code="not_found", status=404)
    source = r.pop("source", "seed")
    return ok(r, source=source)
