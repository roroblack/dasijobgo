# -*- coding: utf-8 -*-
"""infrastructure/rag — 임베딩 검색(RAG). resume 생성 시 '문체·구성 참고' 예시를 주입.

RULE §3.1: sentence-transformers 미설치·모델 미로드면 조용히 빈 결과([])로 폴백(생성은 계속).
bake-off 교훈 반영: 유사도 임계값(config.RAG_MIN_SIM) 미만은 주입 안 함(few-shot 오염 방지).
⚠️ 코퍼스는 가공된 예시(seed).
"""
from .retriever import retrieve, corpus_size, backend_status  # noqa: F401
