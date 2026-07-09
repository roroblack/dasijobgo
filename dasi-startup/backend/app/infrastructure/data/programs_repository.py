# -*- coding: utf-8 -*-
"""infrastructure/data/programs_repository — 창업 지원사업 카탈로그.

RULE §1: 데모용 예시(seed). 실서비스는 기업마당(bizinfo) 지원사업정보 API로 대체하고
자격요건(연령·폐업여부·지역)을 원문에서 파싱해 규칙 매칭한다. meta.source="seed".

eligibility: 규칙 매칭용 조건. min_age/senior 등. link: 원문(RAG 인용/방문 안내).
"""
from __future__ import annotations

SOURCE = "seed"

_SEED: list[dict] = [
    {
        "id": "P001", "title": "신사업창업사관학교", "org": "소상공인시장진흥공단",
        "desc": "창업교육(이론 4주, 무료) + 점포경영체험 + 최대 2천만원 사업화 자금",
        "kind": "education", "amount": "최대 2,000만원", "min_age": 0, "senior_only": False,
        "link": "https://www.sbiz.or.kr", "match_keywords": ["대행", "제조", "품질"],
    },
    {
        "id": "P002", "title": "희망리턴패키지(재창업)", "org": "소상공인시장진흥공단",
        "desc": "폐업 경험자 재창업 사업화 자금 최대 2천만원 + 교육·컨설팅",
        "kind": "fund", "amount": "최대 2,000만원", "min_age": 0, "senior_only": False,
        "requires_prior_closure": True,
        "link": "https://www.sbiz.or.kr/nhrp/main.do", "match_keywords": ["재창업"],
    },
    {
        "id": "P003", "title": "중장년 기술창업센터", "org": "창업진흥원",
        "desc": "전국 25개소 · 보육 공간 + 멘토링(만 40세 이상 기술창업)",
        "kind": "space", "amount": "공간·멘토링", "min_age": 40, "senior_only": True,
        "link": "https://www.k-startup.go.kr", "match_keywords": ["기술", "대행", "안전", "정비"],
    },
    {
        "id": "P004", "title": "국민내일배움카드(직업훈련)", "org": "고용노동부",
        "desc": "창업 관련 자격·기술 훈련비 국비 지원(자격 취득형 후보에 유효)",
        "kind": "education", "amount": "최대 500만원 한도", "min_age": 0, "senior_only": False,
        "link": "https://www.hrd.go.kr", "match_keywords": ["안전", "자격", "정비"],
    },
    {
        "id": "P005", "title": "소상공인 정책자금(창업기반자금)", "org": "소상공인시장진흥공단",
        "desc": "창업 초기 시설·운전 자금 저리 융자",
        "kind": "fund", "amount": "융자", "min_age": 0, "senior_only": False,
        "link": "https://ols.sbiz.or.kr", "match_keywords": ["중개", "판매", "점포"],
    },
]


def all_programs() -> list[dict]:
    return [dict(p) for p in _SEED]
