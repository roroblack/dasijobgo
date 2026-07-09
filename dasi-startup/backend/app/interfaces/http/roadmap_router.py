# -*- coding: utf-8 -*-
"""interfaces/http/roadmap_router — 준비 로드맵 + 지원사업 매칭(STEP 6)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import roadmap_usecase
from app.interfaces.http.responses import err, ok

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("/{cid}")
def build(cid: str):
    r = roadmap_usecase.build(cid)
    if r is None:
        return err("해당 업종 후보를 찾을 수 없어요", code="not_found", status=404)
    source = r.pop("source", "seed")
    return ok(r, source=source)
