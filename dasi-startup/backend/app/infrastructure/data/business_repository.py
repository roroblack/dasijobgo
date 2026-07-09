# -*- coding: utf-8 -*-
"""infrastructure/data/business_repository — 업종 후보 저장소.

RULE §1/§3.1: 아래는 **실측이 아니라 데모용 예시 데이터(seed)**다. 실서비스는
소진공 상가(상권)정보·국세통계 폐업률·기업마당 지원사업 API로 대체하며, 모든 수치에
출처를 병기한다(RAG 인용 강제). 응답 meta.source 는 항상 "seed" 로 표기.

career_fit: 경력→업종 적합도(0~100, 룰 랭킹 입력). keywords: 경력 매칭용.
competitor_density: 반경 5km 동종업체 수(경쟁), customer_pool: 잠재고객 사업장 수.
closure_rate_5y / survival_3y: 업종별 폐업·생존(국세통계 예시). storefront/physical_load: 제약 필터용.
"""
from __future__ import annotations

SOURCE = "seed"  # live 연동 시 "live"

_SEED: list[dict] = [
    {
        "id": "B001", "name": "품질검사 대행업", "sub": "중소 제조사 대상 · 무점포 가능",
        "career_fit": 92, "keywords": ["품질관리", "검사장비", "불량분석", "iso", "품질"],
        "why": "품질관리 15년 + 검사장비 운용 경력이 그대로 사업 자산이 됩니다",
        "risk": "거래처 확보가 관건 — 첫 1년 영업망 없이는 수입 공백 가능",
        "fund": "신사업창업사관학교 교육 + 최대 2천만원 사업화 자금 대상",
        "init_cost": 1000, "storefront": False, "physical_load": "low",
        "competitor_density": 2, "customer_pool": 147, "closure_rate_5y": 38, "survival_3y": 62,
        "market_note": "남동공단 등 제조사 밀집지역이 잠재 고객. 동종 대행업 희소로 경쟁 낮음.",
        "sources": [
            {"label": "반경 5km 제조 사업장 147곳", "org": "소상공인시장진흥공단 상가(상권)정보 2026.1분기"},
            {"label": "업종 5년 생존율", "org": "국세통계포털 업종별 폐업 현황"},
        ],
    },
    {
        "id": "B002", "name": "품질·ISO 교육 강사", "sub": "기업 출강 · 온라인 강의",
        "career_fit": 78, "keywords": ["품질관리", "iso", "교육", "강의", "품질경영"],
        "why": "현장 사례 중심 강의는 경력자만 가능한 차별점",
        "risk": "강의 이력이 없어 초기 실적 쌓기가 필요해요",
        "fund": "중장년 기술창업센터 멘토링 · 1인 지식창업 지원 대상",
        "init_cost": 300, "storefront": False, "physical_load": "low",
        "competitor_density": 12, "customer_pool": 320, "closure_rate_5y": 30, "survival_3y": 70,
        "market_note": "기업 교육 수요는 꾸준하나 강사 공급도 많아 초기 레퍼런스 확보가 진입장벽.",
        "sources": [
            {"label": "기업교육 시장 강사 등록 현황", "org": "직업능력개발 통계(예시)"},
        ],
    },
    {
        "id": "B003", "name": "제조 현장 안전관리 대행", "sub": "50인 미만 사업장 · 방문형",
        "career_fit": 71, "keywords": ["안전관리", "현장관리", "설비", "생산관리"],
        "why": "현장 경력 기반으로 중대재해처벌법 대응 수요와 맞물립니다",
        "risk": "관련 자격(산업안전지도사 등) 취득 여부가 수임 범위를 좌우",
        "fund": "국민내일배움카드로 자격 취득 훈련비 지원 가능",
        "init_cost": 500, "storefront": False, "physical_load": "mid",
        "competitor_density": 5, "customer_pool": 210, "closure_rate_5y": 33, "survival_3y": 67,
        "market_note": "중대재해처벌법 확대로 소규모 사업장 안전관리 위탁 수요 증가 추세.",
        "sources": [
            {"label": "관할 50인 미만 제조 사업장", "org": "소상공인365 상권분석(예시)"},
        ],
    },
    {
        "id": "B004", "name": "중고 산업장비 중개·정비", "sub": "온라인 플랫폼 병행",
        "career_fit": 58, "keywords": ["설비보전", "장비", "정비", "설비"],
        "why": "설비 지식으로 상태 감정·정비가 가능해 단순 중개와 차별화",
        "risk": "재고 보관 공간·초기 매입 자금 부담, 계절 변동성 존재",
        "fund": "소상공인 정책자금(창업기반자금) 융자 대상",
        "init_cost": 6000, "storefront": True, "physical_load": "high",
        "competitor_density": 8, "customer_pool": 130, "closure_rate_5y": 45, "survival_3y": 55,
        "market_note": "진입 자본과 신체 부담이 커 제약 조건에 따라 필터될 수 있는 후보.",
        "sources": [
            {"label": "중고 산업장비 거래 규모", "org": "업종 통계(예시)"},
        ],
    },
    {
        "id": "B005", "name": "스마트스토어 제조상품 판매", "sub": "무점포 · 온라인",
        "career_fit": 44, "keywords": ["생산관리", "제조", "품질"],
        "why": "제조 이해로 상품 소싱·품질 선별에 강점",
        "risk": "온라인 마케팅·CS는 새로 익혀야 하고 초기 경쟁이 치열",
        "fund": "소상공인 온라인 판로지원 · 교육 무료",
        "init_cost": 500, "storefront": False, "physical_load": "low",
        "competitor_density": 40, "customer_pool": 9999, "closure_rate_5y": 55, "survival_3y": 45,
        "market_note": "진입은 쉬우나 과밀. 경력 연관성은 낮아 보조 후보로 제시.",
        "sources": [
            {"label": "온라인 소매 창업 생존율", "org": "통계청 자영업 생존율(예시)"},
        ],
    },
]

_BY_ID = {c["id"]: c for c in _SEED}


def all_candidates() -> list[dict]:
    return [dict(c) for c in _SEED]


def by_id(cid: str) -> dict | None:
    c = _BY_ID.get(cid)
    return dict(c) if c else None
