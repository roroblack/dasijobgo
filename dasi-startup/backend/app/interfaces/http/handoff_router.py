# -*- coding: utf-8 -*-
"""interfaces/http/handoff_router — 전문가 핸드오프 리포트(STEP 7)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import handoff_usecase
from app.interfaces.http.responses import ok
from app.schemas.api_schema import HandoffReq

router = APIRouter(prefix="/handoff", tags=["handoff"])


@router.post("")
def build(req: HandoffReq):
    r = handoff_usecase.build_report(req.name, req.career, req.candidate_ids, req.programs)
    source = r.pop("_source", "fallback")
    return ok(r, source=source)
