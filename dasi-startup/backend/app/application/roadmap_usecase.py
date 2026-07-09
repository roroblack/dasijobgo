# -*- coding: utf-8 -*-
"""application/roadmap_usecase — 준비 체크리스트 + 지원사업 자동 매칭(규칙).

지원사업 매칭은 규칙(자격요건·키워드). 인허가 항목은 원문 링크 필수(RAG 인용 강제, 자유생성 금지).
"""
from __future__ import annotations

from app.infrastructure.data import business_repository, programs_repository


def _checklist(cand: dict) -> list[dict]:
    """후보별 준비 절차(순서대로). 인허가는 원문 확인 링크로 안내."""
    return [
        {"n": 1, "title": "창업 교육 이수", "note": "신사업창업사관학교 · 이론 4주(무료)", "kind": "ok"},
        {"n": 2, "title": "사업자등록(면세/과세 판단)", "note": "홈택스 — 서류 초안 준비 지원", "kind": "todo"},
        {"n": 3, "title": f"{cand['name']} 인허가·자격요건 확인",
         "note": "업종 인허가 원문 보기(법령정보센터)", "kind": "link"},
    ]


def _match_programs(cand: dict) -> list[dict]:
    """후보 키워드/이름과 지원사업 match_keywords 교집합으로 규칙 매칭."""
    text = (cand["name"] + " " + " ".join(cand.get("keywords", []))).lower()
    out = []
    for p in programs_repository.all_programs():
        hit = any(k.lower() in text for k in p.get("match_keywords", []))
        # 재창업 전용은 폐업 경험 필요 → 데모 프로필엔 없으므로 '조건부'로 표기
        eligible = hit and not p.get("requires_prior_closure", False)
        if hit:
            out.append({
                "id": p["id"], "title": p["title"], "org": p["org"], "desc": p["desc"],
                "amount": p["amount"], "kind": p["kind"], "link": p["link"],
                "badge": "자격 충족" if eligible else "조건 확인",
            })
    # 매칭이 적으면 범용 교육 지원 1건 보강
    if len(out) < 2:
        for p in programs_repository.all_programs():
            if p["id"] == "P001" and all(o["id"] != "P001" for o in out):
                out.append({"id": p["id"], "title": p["title"], "org": p["org"], "desc": p["desc"],
                            "amount": p["amount"], "kind": p["kind"], "link": p["link"], "badge": "신청 가능"})
    return out


def build(cid: str) -> dict | None:
    cand = business_repository.by_id(cid)
    if not cand:
        return None
    return {
        "id": cand["id"], "name": cand["name"],
        "checklist": _checklist(cand),
        "programs": _match_programs(cand),
        "source": "seed",
    }
