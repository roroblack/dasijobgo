# -*- coding: utf-8 -*-
"""application/handoff_usecase — 전문가 핸드오프용 개인 리포트 조립.

AI 결과물은 상담사의 사전 자료가 되고, 창업 결정은 사람의 몫으로 남긴다(계획서 §7).
요약 한 줄만 LLM(언어 계층), 없으면 템플릿 폴백. 나머지는 조립(결정론).
"""
from __future__ import annotations

from app.infrastructure.data import business_repository
from app.infrastructure.llm import client


def build_report(name: str, career: str, candidate_ids: list[str], programs: list[str]) -> dict:
    reviewed = []
    for cid in candidate_ids or []:
        c = business_repository.by_id(cid)
        if c:
            reviewed.append({"name": c["name"], "why": c["why"], "risk": c["risk"]})

    names = ", ".join(r["name"] for r in reviewed) or "검토한 후보 없음"
    fallback = f"{name or '회원'}님은 '{career or '현장 경력'}'을 바탕으로 {names} 등을 검토했습니다. 최종 결정 전 전문가 상담을 권합니다."
    summary, source = client.complete(
        system="너는 중장년 창업 탐색을 돕는 안내자다. 결정을 대신하지 말고, 상담사에게 넘길 한 문장 요약만 담담하게 작성하라.",
        user=f"이름:{name} 경력:{career} 검토후보:{names} 확인 지원사업:{', '.join(programs or [])}",
        fallback=fallback,
    )
    return {
        "name": name or "회원", "career": career or "현장 경력",
        "reviewed": reviewed, "programs": programs or [],
        "summary": summary, "_source": source,
        "handoff": {  # 오프라인 연계 안내(예약·신청은 사람/기관 몫 — Path B 상한)
            "org": "거주지 관할 소상공인지원센터", "note": "이 리포트를 인쇄해 방문하면 처음부터 다시 묻지 않습니다.",
        },
    }
