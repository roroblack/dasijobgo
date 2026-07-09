# -*- coding: utf-8 -*-
"""domain/scheduling — 면접 일정 확정(결정론).

RULE §3.3: LLM 협상이 아니라 **가능 시간 교집합**을 규칙으로 계산한다.
슬롯은 문자열 키(예: 'TUE_14', 'THU_15')로 취급 — 요일_시(24h). 양측 교집합에서
'가장 이른' 슬롯을 확정. 이른 순서는 요일·시각 기준 결정론.
"""
from __future__ import annotations

# 요일 정렬 기준(월=0). 슬롯 키의 접두사와 매칭.
_DAY_ORDER = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}


def _slot_sort_key(slot: str) -> tuple[int, int]:
    """'TUE_14' → (1, 14). 형식 불명 슬롯은 뒤로 밀되 예외를 삼키지 않고 큰 값 부여."""
    parts = slot.upper().split("_")
    day = _DAY_ORDER.get(parts[0], 99)
    try:
        hour = int(parts[1]) if len(parts) > 1 else 99
    except ValueError:
        hour = 99
    return (day, hour)


def common_slots(candidate: list[str], company: list[str]) -> list[str]:
    """양측 모두 가능한 슬롯을 이른 순으로."""
    inter = {s.upper() for s in candidate} & {s.upper() for s in company}
    return sorted(inter, key=_slot_sort_key)


def confirm_earliest(candidate: list[str], company: list[str]) -> str | None:
    """교집합 중 가장 이른 슬롯 1개. 교집합이 없으면 None(폴백은 상위 계층 책임)."""
    slots = common_slots(candidate, company)
    return slots[0] if slots else None


# 표시용 라벨(한국어). 데모 UI 가독성 목적의 매핑 — 계산이 아니라 표현이므로 여기 두는 게 적절.
_DAY_KR = {"MON": "월", "TUE": "화", "WED": "수", "THU": "목", "FRI": "금", "SAT": "토", "SUN": "일"}


def label(slot: str) -> str:
    """'TUE_14' → '화요일 오후 2시'."""
    if not slot:
        return ""
    parts = slot.upper().split("_")
    day = _DAY_KR.get(parts[0], parts[0])
    try:
        hour = int(parts[1])
    except (ValueError, IndexError):
        return f"{day}요일"
    ampm = "오전" if hour < 12 else "오후"
    h12 = hour if hour <= 12 else hour - 12
    return f"{day}요일 {ampm} {h12}시"
