# -*- coding: utf-8 -*-
"""application/matching_usecase — 프로필 → 적합도 순위 + 추천 근거.

점수·순위는 domain/matching(결정론). 추천 근거 문구는 겹친 스킬로 규칙 생성(LLM 불필요).
"""
from __future__ import annotations

from app.domain.matching import Profile
from app.infrastructure.data import jobs_repository


def _reason(company: str, matched: list[str], senior: bool) -> str:
    if matched:
        skills = ", ".join(matched)
        base = f"보유하신 '{skills}' 경험이 이 회사의 요구 직무와 맞아요"
    else:
        base = "직무 계열이 유사해 도전해볼 만해요"
    if senior:
        base += " · 중장년 우대 공고"
    return base


def rank_jobs(years: int, skills, region: str, top: int = 5) -> list[dict]:
    profile = Profile.of(years, skills, region)
    ranked = []
    from app.domain.matching import rank as _rank

    for job, score, matched in _rank(profile, jobs_repository.all_jobs())[:top]:
        raw = jobs_repository.raw(job.job_id) or {}
        ranked.append({
            "job_id": job.job_id,
            "company": job.company,
            "role": job.role,
            "region": job.region,
            "fit": score,
            "matched_skills": matched,
            "reason": _reason(job.company, matched, job.senior_friendly),
            "tags": list(job.tags),
            "auto_apply": bool(raw.get("auto_apply", False)),
        })
    return ranked
