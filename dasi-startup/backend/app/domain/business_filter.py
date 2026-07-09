# -*- coding: utf-8 -*-
"""domain/business_filter — 업종 후보 필터·랭킹(결정론). LLM 아님(계획서 Level 2).

후보(경력에서 도출된 업종) × 제약(가용자본·점포희망·신체조건) × 시장신호(경쟁밀도·폐업률)
을 규칙으로 걸러 순위를 매긴다. 판정은 규칙, 서사는 LLM — "판정은 규칙" 원칙 그대로.
수익 예측은 하지 않는다(Level 4 금지).
"""
from __future__ import annotations

# 자본 범위 라벨 → 상한(만원). 후보 초기비용과 비교.
CAPITAL_MAX = {
    "under_3000": 3000,
    "3000_7000": 7000,
    "7000_15000": 15000,
    "unknown": 10_000_000,  # 모르면 필터 안 함
}
_LOAD_RANK = {"low": 0, "mid": 1, "high": 2}


def _fit_label(career_fit: int) -> str:
    if career_fit >= 80:
        return "경력 직결"
    if career_fit >= 55:
        return "경력 활용"
    return "경력 인접"


def filter_rank(candidates: list[dict], *, capital: str = "unknown",
                storefront_ok: bool = True, physical_ok: bool = True) -> list[dict]:
    """제약으로 후보를 거르고 순위를 매겨 반환. 각 후보에 fit_label·filtered_reason 부여.

    - 자본: 초기비용(init_cost) > 자본상한 → 제외
    - 점포: 무점포 희망(storefront_ok=False)인데 점포 필수(storefront=True) → 제외
    - 신체: 신체부담 큰 일 불가(physical_ok=False)인데 physical_load='high' → 제외
    정렬: 경력적합도 desc → 폐업률 asc(생존↑) → 경쟁밀도 asc(경쟁↓)
    """
    cap = CAPITAL_MAX.get(capital, CAPITAL_MAX["unknown"])
    kept = []
    for c in candidates:
        if c.get("init_cost", 0) > cap:
            continue
        if not storefront_ok and c.get("storefront", False):
            continue
        if not physical_ok and c.get("physical_load") == "high":
            continue
        item = dict(c)
        item["fit_label"] = _fit_label(c.get("career_fit", 0))
        kept.append(item)

    kept.sort(key=lambda c: (
        -c.get("career_fit", 0),
        c.get("closure_rate_5y", 100),
        c.get("competitor_density", 100),
    ))
    return kept
