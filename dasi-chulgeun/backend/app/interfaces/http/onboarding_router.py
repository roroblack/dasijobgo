# -*- coding: utf-8 -*-
"""interfaces/http/onboarding_router — 대화형 온보딩(STEP 1)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import onboarding_usecase
from app.interfaces.http.responses import ok
from app.schemas.api_schema import OnboardingReq

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("")
def onboard(req: OnboardingReq):
    result = onboarding_usecase.build_profile(
        req.session_id, req.years, req.skills, req.region
    )
    source = result.pop("_source", "rule")
    return ok(result, source=source)
