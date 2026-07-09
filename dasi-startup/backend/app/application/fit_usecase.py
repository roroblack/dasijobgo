# -*- coding: utf-8 -*-
"""application/fit_usecase — 적합도 진단(재취업/창업 성향). 점수는 domain/fit(결정론)."""
from __future__ import annotations

from app.domain import fit


def diagnose(axis_scores: dict) -> dict:
    """4축 점수 → 성향 진단 결과(게이팅 아님·참고용)."""
    return fit.evaluate(axis_scores or {})
