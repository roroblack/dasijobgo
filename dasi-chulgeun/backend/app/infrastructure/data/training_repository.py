# -*- coding: utf-8 -*-
"""infrastructure/data/training_repository — 내일배움카드 훈련과정 저장소.

RULE §3.1: 실서비스는 data.go.kr '국민내일배움카드 훈련과정' 데이터셋 연동 예정.
데모는 시드 데이터로 폴백. ⚠️ 예시 데이터(seed).
역량 축 키(competency key) → 추천 과정 매핑으로 '역량 갭 → 교육' 루프를 연결한다.
"""
from __future__ import annotations

SOURCE = "seed"

# competency key → 추천 훈련과정. domain/competency 의 축 키와 일치시켜야 함.
_BY_COMPETENCY: dict[str, dict] = {
    "domain_expertise": {
        "course_id": "T-EXP-01", "title": "MSA(측정시스템분석) 실무",
        "provider": "내일배움카드", "weeks": 2, "cost": "무료",
    },
    "communication": {
        "course_id": "T-COM-01", "title": "직무 커뮤니케이션·면접 스피치",
        "provider": "내일배움카드", "weeks": 2, "cost": "무료",
    },
    "quantify_achievement": {
        "course_id": "T-ACH-01", "title": "성과 중심 경력기술서 작성",
        "provider": "내일배움카드", "weeks": 2, "cost": "무료",
    },
    "digital_literacy": {
        "course_id": "T-DIG-01", "title": "중장년 디지털 오피스 실무",
        "provider": "내일배움카드", "weeks": 3, "cost": "무료",
    },
}

_DEFAULT = {
    "course_id": "T-GEN-01", "title": "재취업 직무역량 강화 기초",
    "provider": "내일배움카드", "weeks": 2, "cost": "무료",
}


def recommend_for(competency_key: str) -> dict:
    """역량 축에 맞는 과정. 미매핑 축은 일반 과정으로(명시적 기본값, 조용한 폴백 아님)."""
    return dict(_BY_COMPETENCY.get(competency_key, _DEFAULT))
