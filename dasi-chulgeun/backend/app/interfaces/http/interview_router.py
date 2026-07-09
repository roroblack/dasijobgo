# -*- coding: utf-8 -*-
"""interfaces/http/interview_router — 면접 질문 생성(STEP 7~8)·피드백·역량 갭(STEP 9~10)."""
from __future__ import annotations

from fastapi import APIRouter

from app.application import interview_usecase
from app.interfaces.http.responses import err, ok
from app.schemas.api_schema import AnswerReq, InterviewReq, QuestionsReq

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/questions")
def questions(req: QuestionsReq):
    result = interview_usecase.generate_questions(req.job_id)
    if result is None:
        return err(f"알 수 없는 job_id: {req.job_id}", code="not_found", status=404)
    source = result.pop("_source", "fallback")
    return ok(result, source=source)


@router.post("/analyze")
def analyze(req: InterviewReq):
    signals = {s.key: (s.label, s.score) for s in req.signals}
    result = interview_usecase.analyze(signals)
    source = result.pop("_source", "fallback")
    return ok(result, source=source)


@router.post("/analyze-answer")
def analyze_answer(req: AnswerReq):
    """면접 답변 텍스트 → NCS 루브릭 근거추출 → 역량 등급·최약축·훈련(결정론)."""
    result = interview_usecase.analyze_answer(req.answer_text)
    source = result.pop("_source", "fallback")
    return ok(result, source=source)
