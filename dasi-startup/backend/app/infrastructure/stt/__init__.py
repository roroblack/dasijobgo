# -*- coding: utf-8 -*-
"""infrastructure/stt — 음성 입력(STT). faster-whisper(CPU) 실모델.

RULE §3.1: faster-whisper 미설치 시 조용히 비활성(생성 계층과 무관하게 폴백).
계획서 "음성인식모델 따로" 취지 — 브라우저 Web Speech API가 아니라 서버측 실모델.
Gemma4-오디오/Qwen3-ASR은 GPU/클라우드일 때 여기서 스왑.
"""
from .whisper_stt import backend_status, transcribe  # noqa: F401
