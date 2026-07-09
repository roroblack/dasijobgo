# -*- coding: utf-8 -*-
"""domain/fit — 적합도 진단(재취업/창업 성향). 결정론 규칙, LLM 아님(RULE §3.3).

축은 우리가 임의로 만들지 않고 **고용24 창업적성검사가 쓰는 4축**을 그대로 채용한다
(사업지향성·대인관계·문제해결·설득력). "정부가 검증한 기준을 적용"이라는 심사 방어 논리.
점수는 게이팅이 아니라 참고용 — 두 경로 모두 항상 선택 가능(계획서 §3, §4.1).
"""
from __future__ import annotations

from dataclasses import dataclass

# 고용24 창업적성검사 4축(키·라벨)
AXES = [
    ("business_orientation", "사업지향성"),
    ("interpersonal", "대인관계"),
    ("problem_solving", "문제해결"),
    ("persuasion", "설득력"),
]
_LABEL = dict(AXES)


@dataclass(frozen=True)
class AxisResult:
    key: str
    label: str
    score: int  # 0~100


def _clamp(v) -> int:
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        n = 0
    return max(0, min(100, n))


def evaluate(axis_scores: dict[str, float]) -> dict:
    """4축 점수(dict) → 축별 결과 + 재취업/창업 성향(%) + 문구.

    창업 성향  = 사업지향성 0.40 + 문제해결 0.25 + 설득력 0.20 + 대인관계 0.15
    재취업 성향 = 대인관계 0.35 + 문제해결 0.35 + (100-사업지향성) 0.30  (안정·조직 지향)
    둘은 상호보완적 신호일 뿐 합이 100은 아니다(둘 다 높을 수도 있음).
    """
    a = {k: _clamp(axis_scores.get(k, 0)) for k, _ in AXES}
    axes = [AxisResult(k, _LABEL[k], a[k]) for k, _ in AXES]

    startup = _clamp(0.40 * a["business_orientation"] + 0.25 * a["problem_solving"]
                     + 0.20 * a["persuasion"] + 0.15 * a["interpersonal"])
    reemploy = _clamp(0.35 * a["interpersonal"] + 0.35 * a["problem_solving"]
                      + 0.30 * (100 - a["business_orientation"]))

    lean = "reemploy" if reemploy >= startup else "startup"
    return {
        "axes": [{"key": r.key, "label": r.label, "score": r.score} for r in axes],
        "startup_fit": startup,
        "reemploy_fit": reemploy,
        "lean": lean,  # 참고용 우세 경로(게이팅 아님)
    }
