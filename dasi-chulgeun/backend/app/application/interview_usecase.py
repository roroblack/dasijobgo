# -*- coding: utf-8 -*-
"""application/interview_usecase — 면접 후 피드백·역량 갭·훈련 추천(핵심 차별점).

등급화·최약축 선정은 domain/competency(결정론). 훈련 매핑은 시드. 격려/요약 '문장'만
LLM 언어 계층 → 폴백. (목업 STEP 9 대응 — 탈락으로 끝내지 않고 교육으로 연결)
"""
from __future__ import annotations

from app.domain import competency, rubric
from app.infrastructure.data import jobs_repository, training_repository
from app.infrastructure.llm import client

_GRADE_KR = {"strong": "강점", "ok": "보통", "gap": "보완 필요"}


def analyze_answer(answer_text: str) -> dict:
    """면접 답변(전사 텍스트) → NCS 루브릭 근거추출 → 역량 등급 + 최약축 + 훈련(결정론).

    점수·근거·최약축은 규칙(domain/rubric·competency). 요약 '문장'만 LLM 언어계층→폴백.
    (PART 3: 답변 분석 → NCS rubric 매핑 → 역량 갭). 이전엔 프론트가 신호값을 하드코딩했으나,
    이제 실제 답변에서 결정론적으로 산출한다.
    """
    scored = rubric.extract(answer_text)  # [{key,label,score,evidence,hits}]
    ev_by_key = {r["key"]: r["evidence"] for r in scored}
    signals = {r["key"]: (r["label"], r["score"]) for r in scored}
    results = competency.evaluate(signals)
    weak = competency.weakest(results)
    training = training_repository.recommend_for(weak.key) if weak else None

    fallback = "답변에서 강점은 근거로 확인됐어요. 부족한 축은 교육으로 채우면 다음엔 더 좋아집니다."
    summary, source = client.complete(
        system="너는 면접 답변 분석을 따뜻하게 요약하는 코치다. 판정 금지, 1~2문장 격려.",
        user="역량: " + ", ".join(f"{r.label}={_GRADE_KR[r.grade]}" for r in results),
        fallback=fallback,
    )
    return {
        "competencies": [
            {"key": r.key, "label": r.label, "score": r.score, "grade": r.grade,
             "grade_kr": _GRADE_KR[r.grade], "evidence": ev_by_key.get(r.key, [])}
            for r in results
        ],
        "weakest": {"key": weak.key, "label": weak.label, "score": weak.score} if weak else None,
        "training": training,
        "summary": summary,
        "analysis": "ncs_rubric",  # 근거추출 방식 표기
        "_source": source,
    }


def generate_questions(job_id: str) -> dict | None:
    """STEP 7~8 — 회사 정보 기반 면접 질문 세트(Q1~5).

    Q1~3 은 직무·요구역량에서 규칙으로 조립(면접관이 승인하는 기본 질문 자리).
    Q4~5 는 LLM 언어 계층으로 '꼬리질문'을 생성하고, 키 없으면 템플릿 폴백(RULE §3.3).
    실서비스에선 기업이 작성·승인한 질문 세트가 들어오는 자리 — 데모는 seed 기반 생성.
    """
    job_raw = jobs_repository.raw(job_id)
    if not job_raw:
        return None  # 없는 job_id → 상위에서 404

    company = job_raw["company"]
    role = job_raw["role"]
    req_skills = list(job_raw.get("required_skills", []))
    top_skill = req_skills[0] if req_skills else "담당 업무"

    # Q1~3: 규칙 조립(결정론). 회사·직무·요구역량에서 파생.
    base = [
        {"n": 1, "tag": "기본", "text": f"{role} 업무를 지원하신 이유를 말씀해 주세요."},
        {"n": 2, "tag": "경력", "text": f"{top_skill} 관련 경험 중 가장 자신 있는 사례를 소개해 주세요."},
        {"n": 3, "tag": "직무", "text": "품질관리를 하시면서 가장 어려웠던 불량 문제는 무엇이었나요?"},
    ]

    # Q4~5: LLM 꼬리질문(언어 계층) → 폴백 템플릿.
    fallback_tail = (
        f"그 문제를 해결하며 {company}에 바로 적용할 수 있는 강점은 무엇이라고 생각하세요?\n"
        f"입사 후 첫 3개월 동안 이루고 싶은 목표가 있다면 말씀해 주세요."
    )
    tail_text, source = client.complete(
        system="너는 채용 면접관을 돕는 보조자다. 앞 질문에 이어질 꼬리질문 2개만, 줄바꿈으로 구분해 출력하라.",
        user=f"회사 {company}, 직무 {role}, 요구역량 {req_skills}. Q1~3에 이어질 심화 질문 2개.",
        fallback=fallback_tail,
    )
    tail_lines = [ln.strip() for ln in tail_text.splitlines() if ln.strip()][:2]
    while len(tail_lines) < 2:  # 폴백/모델이 2줄 못 채우면 명시적 보정(조용한 누락 금지)
        tail_lines.append("이 직무에서 앞으로 더 키우고 싶은 역량은 무엇인가요?")
    followups = [
        {"n": 4, "tag": "AI 꼬리질문", "text": tail_lines[0]},
        {"n": 5, "tag": "AI 꼬리질문", "text": tail_lines[1]},
    ]

    return {
        "job_id": job_id,
        "company": company,
        "role": role,
        "questions": base + followups,
        "_source": source,  # Q4~5 생성 출처(live/fallback). Q1~3 은 규칙.
    }


def analyze(signals: dict[str, tuple[str, int]]) -> dict:
    """signals: {competency_key: (label, score)}."""
    results = competency.evaluate(signals)
    weak = competency.weakest(results)

    training = training_repository.recommend_for(weak.key) if weak else None

    fallback = "수고하셨어요. 강점은 살리고 부족한 부분은 교육으로 채우면 다음엔 더 좋아져요."
    summary, source = client.complete(
        system="너는 면접 결과를 따뜻하게 요약하는 코치다. 1~2문장, 격려 위주.",
        user="역량: " + ", ".join(f"{r.label}={_GRADE_KR[r.grade]}" for r in results),
        fallback=fallback,
    )

    return {
        "competencies": [
            {"key": r.key, "label": r.label, "score": r.score,
             "grade": r.grade, "grade_kr": _GRADE_KR[r.grade]}
            for r in results
        ],
        "weakest": {"key": weak.key, "label": weak.label, "score": weak.score} if weak else None,
        "training": training,
        "summary": summary,
        "_source": source,
    }
