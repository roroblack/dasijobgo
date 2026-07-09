# -*- coding: utf-8 -*-
"""schemas/api_schema — 요청 바디 스키마(pydantic). 응답은 responses.ok/err 봉투."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OnboardingReq(BaseModel):
    session_id: str = Field(default="demo")
    years: int | None = None
    skills: list[str] = Field(default_factory=list)
    region: str | None = None


class MatchReq(BaseModel):
    years: int = 0
    skills: list[str] = Field(default_factory=list)
    region: str = ""
    top: int = 5


class ResumeReq(BaseModel):
    job_id: str
    years: int = 0
    skills: list[str] = Field(default_factory=list)
    region: str = ""


class ScheduleReq(BaseModel):
    job_id: str
    candidate_slots: list[str] = Field(default_factory=list)


class InterviewSignal(BaseModel):
    key: str
    label: str
    score: int


class InterviewReq(BaseModel):
    signals: list[InterviewSignal] = Field(default_factory=list)


class QuestionsReq(BaseModel):
    job_id: str


class AnswerReq(BaseModel):
    answer_text: str = Field(default="")
