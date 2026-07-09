# -*- coding: utf-8 -*-
"""application/onboarding_usecase — 대화형 온보딩 → 구조화 프로필.

구조화(경력연수·스킬·지역)는 입력에서 결정론적으로 조립한다. LLM 은 '다음 되묻기 질문'
문장 생성(언어 계층)에만 쓰고, 없으면 규칙 기반 질문으로 폴백.
"""
from __future__ import annotations

from app.infrastructure.llm import client
from app.infrastructure.store import memory_store

# 규칙 기반 되묻기(폴백/기본 흐름). 프로필에서 빈 슬롯을 채우는 순서.
_FOLLOWUPS = [
    ("years", "그 일을 몇 년 정도 하셨어요?"),
    ("skills", "특히 어떤 업무나 장비를 다뤄보셨나요?"),
    ("region", "어느 지역에서 일하고 싶으세요?"),
]


def _next_question(profile: dict) -> str | None:
    for key, q in _FOLLOWUPS:
        val = profile.get(key)
        if val in (None, "", [], 0):
            return q
    return None


def build_profile(session_id: str, years, skills, region) -> dict:
    """부분 입력을 세션 프로필에 병합하고 다음 질문/완료여부를 돌려준다."""
    profile = {
        "years": int(years) if years not in (None, "") else 0,
        "skills": [s for s in (skills or []) if s and s.strip()],
        "region": (region or "").strip(),
    }
    memory_store.update(session_id, profile=profile)

    nxt = _next_question(profile)
    complete = nxt is None

    if complete:
        # 완료 멘트는 언어 계층(LLM) — 없으면 템플릿 폴백.
        fallback = f"{profile['years']}년 경력, 잘 정리했어요. 이제 맞는 일자리를 찾아드릴게요."
        text, source = client.complete(
            system="너는 중장년 재취업을 돕는 따뜻한 안내자다. 한 문장으로 격려하라.",
            user=f"경력 {profile['years']}년, 스킬 {profile['skills']}, 희망지역 {profile['region']}",
            fallback=fallback,
        )
        return {"profile": profile, "complete": True, "message": text, "_source": source}

    return {"profile": profile, "complete": False, "message": nxt, "_source": "rule"}
