# -*- coding: utf-8 -*-
"""interfaces/http — 라우터 묶음 export."""
from app.interfaces.http.health_router import router as health_router
from app.interfaces.http.interview_router import router as interview_router
from app.interfaces.http.matching_router import router as matching_router
from app.interfaces.http.onboarding_router import router as onboarding_router
from app.interfaces.http.resume_router import router as resume_router
from app.interfaces.http.schedule_router import router as schedule_router
from app.interfaces.http.stt_router import router as stt_router

__all__ = [
    "health_router", "onboarding_router", "matching_router",
    "resume_router", "schedule_router", "interview_router", "stt_router",
]
