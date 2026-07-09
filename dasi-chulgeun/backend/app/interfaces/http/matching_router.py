# -*- coding: utf-8 -*-
"""interfaces/http/matching_router — 실시간 매칭(STEP 2)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import matching_usecase
from app.infrastructure.data import jobs_repository
from app.interfaces.http.responses import ok
from app.schemas.api_schema import MatchReq

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("")
def match(req: MatchReq):
    jobs = matching_usecase.rank_jobs(req.years, req.skills, req.region, top=req.top)
    # 데이터는 seed(고용24 직접연동 불가 → data.go.kr 대체, 데모는 시드). RULE §3.1.
    return ok({"count": len(jobs), "jobs": jobs}, source=jobs_repository.SOURCE)
