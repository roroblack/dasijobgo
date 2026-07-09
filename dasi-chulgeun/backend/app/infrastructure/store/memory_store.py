# -*- coding: utf-8 -*-
"""infrastructure/store/memory_store — 인메모리 세션 저장소.

RULE §3.1: DB 미설정 시 memory 폴백(GAJIMA 패턴 계승). 프로토타입은 프로세스 메모리에
세션을 유지한다. 재시작 시 초기화됨 — 데모 목적상 충분(실서비스는 DB 로 대체).
스레드 안전을 위해 간단한 Lock 사용.
"""
from __future__ import annotations

import threading

_LOCK = threading.Lock()
_SESSIONS: dict[str, dict] = {}


def get(session_id: str) -> dict:
    """세션 조회(없으면 빈 세션 생성). 항상 dict 반환."""
    with _LOCK:
        return _SESSIONS.setdefault(session_id, {"profile": None, "cart": [], "confirmed": {}})


def update(session_id: str, **fields) -> dict:
    with _LOCK:
        s = _SESSIONS.setdefault(session_id, {"profile": None, "cart": [], "confirmed": {}})
        s.update(fields)
        return dict(s)


def reset(session_id: str) -> None:
    with _LOCK:
        _SESSIONS.pop(session_id, None)


def count() -> int:
    with _LOCK:
        return len(_SESSIONS)
