# -*- coding: utf-8 -*-
"""domain/competency — 면접 후 역량 갭 산정(결정론).

RULE §3.3: 역량 점수는 면접 신호(0~100)에서 규칙으로 등급화하고, 가장 약한 축을
'보완 필요'로 지목한다. 훈련 추천 매핑은 표현 계층에서 사용(여기선 갭만 계산).
"""
from __future__ import annotations

from dataclasses import dataclass

# 등급 임계값. 튜닝 지점 집약(RULE §3.2).
STRONG_MIN = 75   # 이상: 강점
OK_MIN = 50       # 이상~STRONG 미만: 보통. 미만: 보완 필요


@dataclass(frozen=True)
class CompetencyResult:
    key: str          # 역량 축 키(예: 'domain_expertise')
    label: str        # 표시명(예: '직무 전문성')
    score: int        # 0~100
    grade: str        # 'strong' | 'ok' | 'gap'


def grade_of(score: int) -> str:
    if score >= STRONG_MIN:
        return "strong"
    if score >= OK_MIN:
        return "ok"
    return "gap"


def evaluate(signals: dict[str, tuple[str, int]]) -> list[CompetencyResult]:
    """signals: {key: (label, score)} → 등급화 결과 리스트(입력 순서 유지).

    score 는 0~100 로 클램프. 범위 밖 입력을 조용히 통과시키지 않고 경계로 맞춘다.
    """
    out: list[CompetencyResult] = []
    for key, (lbl, raw) in signals.items():
        score = max(0, min(100, int(raw)))
        out.append(CompetencyResult(key, lbl, score, grade_of(score)))
    return out


def weakest(results: list[CompetencyResult]) -> CompetencyResult | None:
    """가장 낮은 점수 축(동점이면 입력 순서상 먼저). 훈련 연결의 근거."""
    if not results:
        return None
    return min(results, key=lambda r: r.score)
