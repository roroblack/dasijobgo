# -*- coding: utf-8 -*-
"""application/market_usecase — 후보 상권·리스크 리포트. 수치는 seed + 출처 병기(RAG 인용 강제).

⚠️ 수익 예측은 하지 않는다(계획서 Level 4 설계상 금지). "월 얼마 법니다"는 반환하지 않고,
   판단에 필요한 사실(잠재고객·경쟁·생존율)과 출처만 제공한다.
"""
from __future__ import annotations

from app.infrastructure.data import business_repository


def report(cid: str) -> dict | None:
    c = business_repository.by_id(cid)
    if not c:
        return None
    pool, comp = c["customer_pool"], c["competitor_density"]
    # 경쟁 강도(결정론 룰): 잠재고객 대비 경쟁 업체 비율로 낮음/보통/높음
    ratio = comp / pool if pool else 1.0
    competition = "낮음" if ratio < 0.03 else ("보통" if ratio < 0.1 else "높음")
    survival_flag = "주의" if c["survival_3y"] < 50 else ("보통" if c["survival_3y"] < 65 else "양호")
    return {
        "id": c["id"], "name": c["name"],
        "stats": [
            {"key": "customer_pool", "label": "반경 5km 잠재 고객(사업장)", "value": f"{pool:,}곳", "tone": "ok"},
            {"key": "competitor", "label": "동종 업체(경쟁)", "value": f"{comp}곳 · {competition}",
             "tone": "ok" if competition == "낮음" else "warn"},
            {"key": "survival", "label": "업종 3년 생존율", "value": f"{c['survival_3y']}% · {survival_flag}",
             "tone": "warn" if survival_flag == "주의" else "ok"},
        ],
        "market_note": c["market_note"],
        "sources": c["sources"],  # 모든 수치 출처 병기
        "no_revenue_forecast": True,  # 수익 예측 미제공 명시(프론트 고지문 트리거)
        "source": business_repository.SOURCE,  # seed
    }
