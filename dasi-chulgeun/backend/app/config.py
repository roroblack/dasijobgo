# -*- coding: utf-8 -*-
"""config — 환경설정 집약. 값은 코드 하드코딩이 아니라 환경변수 우선(기본값은 데모용)."""
from __future__ import annotations

import os

PORT = int(os.environ.get("PORT", "8090"))
HOST = os.environ.get("HOST", "127.0.0.1")

# LLM(언어 계층). 키 없으면 client.py 가 템플릿 폴백. 모델 ID 는 환경변수로 교체 가능.
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-5")

# 로컬 GGUF LLM(llama.cpp). 경로 설정 시 client.py 가 로컬 모델을 우선 사용(예: Gemma-4-E4B/EXAONE-2.4B).
# 미설정이면 API(키 있으면) → 템플릿 폴백. bake-off 결과 반영(reports/final-model-eval-*).
LLM_GGUF_PATH = os.environ.get("LLM_GGUF_PATH", "")
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "320"))
LLM_N_BATCH = int(os.environ.get("LLM_N_BATCH", "64"))  # Gemma-4 대용량 어휘 logits 버퍼 대비 소용량

# RAG 임베딩(sentence-transformers). 저사양 기본 = 소형 한국어 SBERT. 실서버는 BGE-M3/Kanana-emb 권장.
RAG_EMB_MODEL = os.environ.get("RAG_EMB_MODEL", "jhgan/ko-sroberta-multitask")
RAG_TOPK = int(os.environ.get("RAG_TOPK", "2"))
RAG_MIN_SIM = float(os.environ.get("RAG_MIN_SIM", "0.45"))  # 임계값 미만은 주입 안 함(오염 방지 — bake-off §RAG 교훈)

# 화상 면접 링크. 국산 화상 API(구루미 등) 미확보 시 Meet 형식으로 폴백(RULE §3.1).
MEET_BASE = os.environ.get("MEET_BASE", "https://meet.google.com")

# STT(음성 입력) — faster-whisper(CPU). 미설치면 stt 모듈이 비활성(폴백). Gemma4-오디오/Qwen3-ASR은 GPU 스왑 자리.
# 한국어 실마이크 정확도: large-v3(권장·환각/반복 최소) > large-v3-turbo(빠르나 반복 잦음) > medium > small.
# turbo는 디코더가 작아 한국어 반복환각이 잦음 → 기본 large-v3. 속도 우선이면 STT_MODEL=medium, RAM 빠듯하면 small.
STT_MODEL = os.environ.get("STT_MODEL", "large-v3")

APP_NAME = "다시,출근 — 중장년 재취업 실행 에이전트 (프로토타입)"
