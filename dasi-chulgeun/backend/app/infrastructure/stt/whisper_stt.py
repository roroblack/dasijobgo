# -*- coding: utf-8 -*-
"""infrastructure/stt/whisper_stt — faster-whisper 전사(지연 로드 싱글턴).

CPU·int8 로 base 모델 로드. 오디오 바이트 → 한국어 텍스트. 실패/미설치면 None(상위서 503).
"""
from __future__ import annotations

import io
import os

# Windows에서 HF 캐시 심볼릭 생성 권한(WinError 1314) 회피 → 복사 모드로 다운로드.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from app.config import STT_MODEL

_model = None
_status = "uninit"  # uninit | ready | disabled


def _lazy():
    global _model, _status
    if _status != "uninit":
        return
    try:
        from faster_whisper import WhisperModel
        _model = WhisperModel(STT_MODEL, device="cpu", compute_type="int8")
        _status = "ready"
        print(f"[stt] faster-whisper 로드: {STT_MODEL} (cpu/int8)")
    except Exception as e:  # noqa: BLE001 — 미설치/로드 실패를 숨기지 않고 비활성
        _status = "disabled"
        print(f"[stt] 비활성(폴백): {e}")


def backend_status() -> str:
    _lazy()
    return _status  # ready | disabled


def transcribe(audio_bytes: bytes, language: str = "ko") -> str | None:
    """오디오 바이트 → 전사 텍스트. 비활성/실패면 None."""
    _lazy()
    if _status != "ready" or not audio_bytes:
        return None
    try:
        # 환각·반복 억제 다중 방어:
        #  · compression_ratio_threshold — "엔딩했을 때 엔딩했을 때" 식 반복 세그먼트를 걸러 재디코딩.
        #  · temperature 폴백 — 저신뢰 시 온도 올려 재시도(반복 루프 탈출).
        #  · initial_prompt — 한국어 상담 도메인 어휘로 바이어스(엉뚱한 전사 감소).
        #  · vad_filter + condition_on_previous_text=False — 무음/잡음 및 문맥오염 차단.
        segments, _info = _model.transcribe(
            io.BytesIO(audio_bytes), language=language, beam_size=5,
            vad_filter=True, condition_on_previous_text=False,
            no_speech_threshold=0.6,
            temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            initial_prompt="다음은 중장년 구직자가 직무 경력과 연차, 희망 근무 지역을 한국어로 또박또박 말하는 상담 녹음입니다.",
        )
        # 저신뢰(높은 no_speech / 낮은 avg_logprob) 세그먼트는 버려 환각을 줄인다.
        parts = [s.text.strip() for s in segments
                 if getattr(s, "no_speech_prob", 0) < 0.6 and getattr(s, "avg_logprob", 0) > -1.0]
        return " ".join(p for p in parts if p).strip()
    except Exception as e:  # noqa: BLE001
        print(f"[stt] 전사 실패: {e}")
        return None
