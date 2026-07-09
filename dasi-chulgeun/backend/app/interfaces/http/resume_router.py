# -*- coding: utf-8 -*-
"""interfaces/http/resume_router — 회사별 맞춤 이력서 + 4종 안내(STEP 3~4)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import resume_usecase
from app.interfaces.http.responses import err, ok
from app.schemas.api_schema import ResumeReq

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("")
def resume(req: ResumeReq):
    result = resume_usecase.build_resume(req.job_id, req.years, req.skills, req.region)
    if result is None:
        return err(f"알 수 없는 job_id: {req.job_id}", code="not_found", status=404)
    source = result.pop("_source", "fallback")
    return ok(result, source=source)
