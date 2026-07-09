# -*- coding: utf-8 -*-
"""application/schedule_usecase — 면접 일정 자동 확정 + 화상 링크.

교집합·최이른 확정은 domain/scheduling(결정론, LLM 아님). 화상 링크는 국산 API 미확보로
Meet 형식 폴백(RULE §3.1). (목업 STEP 6 대응)
"""
from __future__ import annotations

from app.config import MEET_BASE
from app.domain import scheduling
from app.infrastructure.data import jobs_repository


def _meet_link(job_id: str, slot: str) -> tuple[str, str]:
    """(url, source). 국산 화상 API 연동 시 source='live' 로 전환."""
    token = f"{job_id.lower()}-{slot.lower().replace('_', '')}"
    return f"{MEET_BASE}/{token}", "fallback"


def confirm(job_id: str, candidate_slots: list[str]) -> dict | None:
    company = jobs_repository.company_slots(job_id)
    if not company:
        return None  # 없는 job_id

    common = scheduling.common_slots(candidate_slots, company)
    slot = scheduling.confirm_earliest(candidate_slots, company)

    if not slot:
        # 교집합 없음 — 가짜 확정을 만들지 않는다(RULE §3.2). 대안 슬롯을 제안.
        return {
            "job_id": job_id, "confirmed": False, "slot": None, "slot_label": None,
            "meet_url": None, "meet_source": None,
            "company_slots": company, "common_slots": [],
            "message": "겹치는 시간이 없어요. 회사 가능 시간에서 다시 골라주세요.",
        }

    url, msrc = _meet_link(job_id, slot)
    return {
        "job_id": job_id, "confirmed": True,
        "slot": slot, "slot_label": scheduling.label(slot),
        "meet_url": url, "meet_source": msrc,
        "company_slots": company, "common_slots": common,
        "message": f"{scheduling.label(slot)} 확정 — 양쪽 모두 가능한 가장 이른 시간이에요.",
    }
