# -*- coding: utf-8 -*-
"""domain/matching — 구직자 프로필 ↔ 채용공고 적합도(결정론).

RULE §3.2/§3.3: 적합도는 상수로 박지 않고 **로직으로 계산**한다. LLM 미사용(순수 함수).
점수 = 스킬 겹침 + 경력 충족 + 지역 근접 + 중장년 우대 가산. 0~100 정수.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# 가중치(합계 100). 튜닝 지점을 한곳에 모아 둔다 — "매직 넘버 흩뿌리기" 방지(RULE §3.2).
W_SKILL = 55       # 요구 스킬과의 겹침
W_EXPERIENCE = 25  # 최소 경력 충족
W_REGION = 12      # 지역 일치/근접
W_SENIOR = 8       # 중장년 우대 태그


@dataclass(frozen=True)
class Profile:
    years: int
    skills: frozenset[str]
    region: str

    @staticmethod
    def of(years: int, skills, region: str) -> "Profile":
        return Profile(int(years), frozenset(_norm(s) for s in skills), _norm(region))


@dataclass(frozen=True)
class Job:
    job_id: str
    company: str
    role: str
    region: str
    required_skills: frozenset[str]
    min_years: int
    senior_friendly: bool = False
    tags: tuple[str, ...] = field(default_factory=tuple)


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _skill_score(profile: Profile, job: Job) -> float:
    req = job.required_skills
    if not req:
        return W_SKILL  # 요구 스킬 미명시면 페널티 주지 않음
    hit = len(profile.skills & req)
    return W_SKILL * (hit / len(req))


def _experience_score(profile: Profile, job: Job) -> float:
    if job.min_years <= 0:
        return W_EXPERIENCE
    ratio = profile.years / job.min_years
    return W_EXPERIENCE * min(ratio, 1.0)


def _region_score(profile: Profile, job: Job) -> float:
    if not job.region or not profile.region:
        return W_REGION * 0.5
    if profile.region == job.region:
        return W_REGION
    # 광역 단위(첫 토큰: '인천','서울' 등) 일치 시 부분 점수
    if profile.region.split()[:1] == job.region.split()[:1]:
        return W_REGION * 0.6
    return 0.0


def _senior_score(job: Job) -> float:
    return W_SENIOR if job.senior_friendly else 0.0


def fit_score(profile: Profile, job: Job) -> int:
    """0~100 정수 적합도."""
    total = (
        _skill_score(profile, job)
        + _experience_score(profile, job)
        + _region_score(profile, job)
        + _senior_score(job)
    )
    return max(0, min(100, round(total)))


def matched_skill_labels(profile: Profile, job: Job) -> list[str]:
    """추천 근거 표시용 — 실제로 겹친 스킬(원문 아닌 정규화 라벨)."""
    return sorted(profile.skills & job.required_skills)


def rank(profile: Profile, jobs: list[Job]) -> list[tuple[Job, int, list[str]]]:
    """(job, score, matched_skills) 내림차순. 동점은 min_years 낮은 순 → job_id 안정 정렬."""
    scored = [(j, fit_score(profile, j), matched_skill_labels(profile, j)) for j in jobs]
    scored.sort(key=lambda t: (-t[1], t[0].min_years, t[0].job_id))
    return scored
