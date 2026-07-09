# -*- coding: utf-8 -*-
"""application/resume_usecase — 회사별 맞춤 이력서 초안 + 4종 안내.

4종 안내(①요구 ②강조 ③부족역량 ④정부교육)는 규칙으로 조립(결정론). 이력서 '문장'은
LLM 언어 계층으로 생성하고, 키 없으면 템플릿 폴백. (목업 STEP 4 대응)
"""
from __future__ import annotations

from app.domain.matching import Job, Profile
from app.infrastructure import rag
from app.infrastructure.data import jobs_repository, training_repository
from app.infrastructure.llm import client


def _gap_skill(profile: Profile, job: Job) -> str | None:
    """요구 스킬 중 프로필에 없는 것 하나 = '더 기르면 좋은 역량'."""
    missing = sorted(job.required_skills - profile.skills)
    return missing[0] if missing else None


# 부족 스킬 → 훈련 competency 축 매핑(표현 계층 규칙).
_SKILL_TO_COMPETENCY = {
    "iso9001": "domain_expertise",
    "haccp": "domain_expertise",
    "검사장비": "domain_expertise",
    "전기": "domain_expertise",
    "안전관리": "domain_expertise",
}


def build_resume(job_id: str, years: int, skills, region: str) -> dict | None:
    job_raw = jobs_repository.raw(job_id)
    if not job_raw:
        return None  # 없는 job_id → 상위에서 404(조용한 기본값 아님)

    profile = Profile.of(years, skills, region)
    job = next(j for j in jobs_repository.all_jobs() if j.job_id == job_id)

    matched = sorted(profile.skills & job.required_skills)
    gap = _gap_skill(profile, job)
    emphasis = matched[0] if matched else "관련 현장 경험"

    # RAG: 유사 '문체 참고' 예시 검색(임계값 이상만). 사실은 지원자 것만 쓰도록 명시(오염 방지).
    rag_query = f"{' '.join(sorted(job.required_skills))} {years}년 {region}"
    rag_hits = rag.retrieve(rag_query)
    rag_block = ""
    if rag_hits:
        rag_block = ("\n[문체·구성 참고 예시 — 회사·업종·수치는 베끼지 말고 지원자 사실만 사용]\n"
                     + "\n".join(f"· {h['text']}" for h in rag_hits))

    # 이력서 핵심 문장 — 언어 계층(로컬 LLM → API → 템플릿). RAG 예시를 문체 참고로만 주입.
    fallback_body = (
        f"{region or '해당 지역'} 기반 {years}년 경력. "
        f"'{emphasis}' 경험을 앞세워 {job.company}의 {job.role} 직무에 맞춰 재구성했습니다."
    )
    body, source = client.complete(
        system=("너는 중장년 구직자의 자기소개서를 회사 맞춤으로 쓴다. [지원자 경력]의 사실만 사용하고, "
                "참고 예시의 회사·업종·수치를 지원자 것으로 가져오지 않는다. 과장 없이 3~4문장, 본문만 출력."),
        user=(f"[채용공고] {job.company} · {job.role} (요구: {', '.join(sorted(job.required_skills))})\n"
              f"[지원자 경력] {years}년, 강조 '{emphasis}', 보유 {', '.join(matched) or '현장 경험'}, 부족 '{gap}'"
              f"{rag_block}\n위 사실만으로 자기소개서 본문을 쓰세요."),
        fallback=fallback_body,
    )

    # 4종 안내 카드(결정론 조립)
    training = None
    if gap:
        comp_key = _SKILL_TO_COMPETENCY.get(gap, "domain_expertise")
        training = training_repository.recommend_for(comp_key)

    guide = [
        {"n": 1, "label": "이 회사가 원하는 것",
         "text": ", ".join(sorted(job.required_skills)) + f" · {job.min_years}년+ 경력"},
        {"n": 2, "label": "그래서 강조한 것", "text": f"'{emphasis}' 이력을 맨 위로 배치"},
        {"n": 3, "label": "더 기르면 좋은 역량", "text": gap or "핵심 요건 충족 — 추가 필수 없음"},
        {"n": 4, "label": "정부 지원 교육",
         "text": training["title"] if training else "현재 추천 과정 없음"},
    ]

    return {
        "job_id": job_id,
        "company": job.company,
        "role": job.role,
        "resume_body": body,
        "emphasis": emphasis,
        "gap_skill": gap,
        "guide": guide,
        "training": training,
        "auto_apply": bool(job_raw.get("auto_apply", False)),
        "rag": {
            "used": bool(rag_hits),
            "backend": rag.backend_status(),
            "examples": [{"id": h["id"], "role": h["role"], "sim": h["sim"]} for h in rag_hits],
        },
        "_source": source,
    }
