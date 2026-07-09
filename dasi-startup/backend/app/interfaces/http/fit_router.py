# -*- coding: utf-8 -*-
"""interfaces/http/fit_router — 적합도 진단(STEP 3, 재취업/창업 분기)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import fit_usecase
from app.interfaces.http.responses import ok
from app.schemas.api_schema import FitReq

router = APIRouter(prefix="/fit", tags=["fit"])


@router.post("")
def diagnose(req: FitReq):
    # 점수는 결정론 규칙(고용24 4축). 게이팅 아님·참고용 → source=rule.
    return ok(fit_usecase.diagnose(req.axis_scores), source="rule")
