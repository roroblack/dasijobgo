# -*- coding: utf-8 -*-
"""infrastructure/llm/client — LLM 언어 계층(폴백 포함).

RULE §3.1/§3.3: LLM 은 '언어 계층'에만 쓴다(대화 되묻기, 이력서 초안 문장, 피드백 문장).
API 키(ANTHROPIC_API_KEY)가 없거나 SDK 미설치면 **템플릿 기반 생성으로 폴백**한다.
- 폴백은 데모를 계속 돌리기 위한 '필요한' 폴백이며, 결과 meta.source 에 'fallback' 로 드러낸다.
- 결정론 계산(점수·시간·갭)은 절대 이 계층에 맡기지 않는다.

⚠️ 라이브 호출 경로는 키가 있을 때만 시도하며, 실패 시 조용히 삼키지 않고 폴백으로 내려가되
   로그로 사유를 남긴다(RULE §1: 실패를 숨기지 않는다).
"""
from __future__ import annotations

import os

from app.config import (LLM_GGUF_PATH, LLM_MAX_TOKENS, LLM_MODEL, LLM_N_BATCH)


def available() -> bool:
    """라이브 LLM 사용 가능 여부(키 존재로 판단). 실제 호출 성공은 별개."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


# ── 로컬 GGUF(llama.cpp) 백엔드 — 지연 로드 싱글턴 ──────────────
_local_llm = None
_local_tried = False


def local_available() -> bool:
    """로컬 GGUF 경로가 설정·존재하고 llama_cpp 임포트 가능한가."""
    if not (LLM_GGUF_PATH and os.path.isfile(LLM_GGUF_PATH)):
        return False
    try:
        import llama_cpp  # noqa: F401
        return True
    except ImportError:
        return False


def _get_local():
    """Llama 인스턴스(최초 1회 로드). 실패 시 None(숨기지 않고 로그)."""
    global _local_llm, _local_tried
    if _local_llm is not None:
        return _local_llm
    if _local_tried or not local_available():
        return _local_llm
    _local_tried = True
    try:
        from llama_cpp import Llama
        _local_llm = Llama(model_path=LLM_GGUF_PATH, n_ctx=4096, n_batch=LLM_N_BATCH,
                           n_threads=os.cpu_count() or 4, verbose=False)
        print(f"[llm] 로컬 GGUF 로드: {os.path.basename(LLM_GGUF_PATH)}")
    except Exception as e:  # noqa: BLE001 — 사유 드러내고 폴백
        print(f"[llm] 로컬 GGUF 로드 실패 → 폴백: {e}")
        _local_llm = None
    return _local_llm


def _local_complete(system: str, user: str) -> str | None:
    llm = _get_local()
    if llm is None:
        return None
    try:
        r = llm.create_chat_completion(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.5, top_p=0.9, max_tokens=LLM_MAX_TOKENS, repeat_penalty=1.15,
        )
        return r["choices"][0]["message"]["content"].strip()
    except Exception as e:  # noqa: BLE001
        print(f"[llm] 로컬 호출 실패 → 폴백: {e}")
        return None


def _live_complete(system: str, user: str) -> str | None:
    """키가 있을 때만 실제 호출. SDK 미설치/오류면 None 반환(→ 폴백)."""
    if not available():
        return None
    try:
        import anthropic  # 선택적 의존성 — 없으면 폴백
    except ImportError:
        print("[llm] anthropic SDK 미설치 → 템플릿 폴백")
        return None
    try:
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=LLM_MODEL,
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    except Exception as e:  # noqa: BLE001 — 사유를 로그로 드러내고 폴백(숨기지 않음)
        print(f"[llm] 라이브 호출 실패 → 폴백: {e}")
        return None


def complete(system: str, user: str, *, fallback: str) -> tuple[str, str]:
    """(텍스트, source) 반환. 우선순위: 로컬 GGUF → API → 템플릿. source ∈ {'local','live','fallback'}."""
    text = _local_complete(system, user)
    if text:
        return text, "local"
    text = _live_complete(system, user)
    if text:
        return text, "live"
    return fallback, "fallback"
