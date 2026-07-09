# -*- coding: utf-8 -*-
"""tests/test_domain — 창업 트랙 결정론 로직 단위 검증(RULE §2).

fit(적합도 4축)·business_filter(후보 필터/랭킹)·slots(전사 슬롯)는 순수 함수 → 외부 의존 없이 검증.
실행: backend/ 에서  python -m pytest -q
"""
from __future__ import annotations

from app.domain import business_filter, fit, slots


# ---- 적합도 진단(fit) ----
def test_fit_axes_and_clamp():
    r = fit.evaluate({"business_orientation": 250, "interpersonal": -5,
                      "problem_solving": 70, "persuasion": 60})
    scores = {a["key"]: a["score"] for a in r["axes"]}
    assert scores["business_orientation"] == 100 and scores["interpersonal"] == 0  # 범위 클램프
    assert 0 <= r["startup_fit"] <= 100 and 0 <= r["reemploy_fit"] <= 100


def test_fit_high_business_orientation_leans_startup():
    hi = fit.evaluate({"business_orientation": 90, "interpersonal": 50,
                       "problem_solving": 70, "persuasion": 80})
    lo = fit.evaluate({"business_orientation": 10, "interpersonal": 80,
                       "problem_solving": 70, "persuasion": 30})
    assert hi["startup_fit"] > lo["startup_fit"]
    assert lo["reemploy_fit"] > hi["reemploy_fit"]  # 사업지향 낮으면 재취업 성향↑


# ---- 후보 필터/랭킹(business_filter) ----
def _cands():
    return [
        {"id": "A", "career_fit": 90, "init_cost": 1000, "storefront": False,
         "physical_load": "low", "closure_rate_5y": 38, "competitor_density": 2},
        {"id": "B", "career_fit": 60, "init_cost": 6000, "storefront": True,
         "physical_load": "high", "closure_rate_5y": 45, "competitor_density": 8},
        {"id": "C", "career_fit": 50, "init_cost": 500, "storefront": False,
         "physical_load": "low", "closure_rate_5y": 55, "competitor_density": 40},
    ]


def test_filter_drops_by_constraints():
    # 무점포·건강제약·자본 3천 상한 → 점포+고신체+6천짜리 B 제외
    r = business_filter.filter_rank(_cands(), capital="under_3000",
                                    storefront_ok=False, physical_ok=False)
    ids = [c["id"] for c in r]
    assert "B" not in ids and set(ids) == {"A", "C"}


def test_rank_by_career_fit_then_survival():
    r = business_filter.filter_rank(_cands())  # 제약 없음
    assert [c["id"] for c in r] == ["A", "B", "C"]  # career_fit 내림차순
    assert r[0]["fit_label"] == "경력 직결"  # 90 → 직결


# ---- 전사 슬롯(공통 재사용) ----
def test_slots_keep_core_drop_filler():
    s = slots.extract("음 그러니까 제가 이제 지게차 면허도 있고 물류 현장에서 일했어요 부천에서 25년")
    assert s.get("region") == "부천" and s.get("years") == 25
    assert slots.extract("음 어 그러니까 뭐 그냥 이제") == {}
