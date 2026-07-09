# -*- coding: utf-8 -*-
"""interfaces/http/candidates_router — 업종 후보 카드(TRACK C STEP 4, 킬러)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import candidates_usecase
from app.interfaces.http.responses import ok
from app.schemas.api_schema import CandidatesReq

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("")
def recommend(req: CandidatesReq):
    r = candidates_usecase.recommend(
        req.skills, capital=req.capital, storefront_ok=req.storefront_ok,
        physical_ok=req.physical_ok, top=req.top)
    source = r.pop("source", "seed")
    return ok(r, source=source)
