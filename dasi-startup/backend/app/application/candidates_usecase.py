# -*- coding: utf-8 -*-
"""application/candidates_usecase — 경력·제약 → 업종 후보 카드(근거·위험·지원 3요소).

후보 필터·랭킹은 domain/business_filter(결정론, 계획서 Level 1~2). 각 카드는 근거·위험을
반드시 병기(장밋빛 카드 금지). 데이터는 seed(business_repository), 실서비스는 공공데이터.
"""
from __future__ import annotations

from app.domain import business_filter
from app.infrastructure.data import business_repository


def _matched(skills: list[str], keywords: list[str]) -> list[str]:
    sk = [s for s in (skills or []) if s]
    kws = set(keywords or [])
    out = []
    for s in sk:
        low = s.replace(" ", "").lower()
        if any(low in k.lower() or k.lower() in low for k in kws):
            out.append(s)
    return out


def recommend(skills: list[str], *, capital: str = "unknown",
              storefront_ok: bool = True, physical_ok: bool = True, top: int = 4) -> dict:
    cands = business_repository.all_candidates()
    ranked = business_filter.filter_rank(
        cands, capital=capital, storefront_ok=storefront_ok, physical_ok=physical_ok)

    cards = []
    for c in ranked[:top]:
        cards.append({
            "id": c["id"], "name": c["name"], "sub": c["sub"],
            "fit_label": c["fit_label"], "career_fit": c["career_fit"],
            "matched_skills": _matched(skills, c.get("keywords", [])),
            "why": c["why"], "risk": c["risk"], "fund": c["fund"],
            "init_cost": c["init_cost"], "storefront": c["storefront"],
            "physical_load": c["physical_load"],
        })
    return {
        "count": len(cards), "total_considered": len(cands),
        "filtered_out": len(cands) - len(ranked),  # 제약으로 제외된 수(투명 공개)
        "candidates": cards,
        "source": business_repository.SOURCE,  # seed
    }
