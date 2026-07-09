# -*- coding: utf-8 -*-
"""interfaces/http/schedule_router — 면접 일정 자동 확정(STEP 6)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import schedule_usecase
from app.interfaces.http.responses import err, ok
from app.schemas.api_schema import ScheduleReq

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.post("/confirm")
def confirm(req: ScheduleReq):
    result = schedule_usecase.confirm(req.job_id, req.candidate_slots)
    if result is None:
        return err(f"알 수 없는 job_id: {req.job_id}", code="not_found", status=404)
    # 확정 자체는 결정론 계산(live 로직). 화상 링크는 meet_source 필드로 별도 표기.
    return ok(result, source="live")
