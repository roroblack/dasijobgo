# -*- coding: utf-8 -*-
"""schemas/api_schema — 요청 바디 스키마(pydantic). 응답은 responses.ok/err 봉투."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OnboardingReq(BaseModel):
    session_id: str = Field(default="demo")
    years: int | None = None
    skills: list[str] = Field(default_factory=list)
    region: str | None = None


class FitReq(BaseModel):
    # 고용24 창업적성검사 4축 점수(0~100). 프론트 성향 진단 응답 신호에서 산출.
    axis_scores: dict[str, float] = Field(default_factory=dict)


class CandidatesReq(BaseModel):
    skills: list[str] = Field(default_factory=list)
    capital: str = "unknown"        # under_3000 | 3000_7000 | 7000_15000 | unknown
    storefront_ok: bool = True      # 점포 창업 가능 여부(False=무점포 희망)
    physical_ok: bool = True        # 신체 부담 큰 일 가능 여부(False=건강 제약)
    top: int = 4


class HandoffReq(BaseModel):
    name: str = ""
    career: str = ""
    candidate_ids: list[str] = Field(default_factory=list)
    programs: list[str] = Field(default_factory=list)
