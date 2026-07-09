# -*- coding: utf-8 -*-
"""infrastructure/rag/retriever — 소규모 코사인 검색(인메모리).

지원자 경력 쿼리 → 유사 '합격 자소서 톤 예시' top-k(임계값 이상)만 반환.
실서버는 BGE-M3/Kanana-emb + FAISS/pgvector + reranker 로 대체(config.RAG_EMB_MODEL).
⚠️ 아래 코퍼스는 전부 가공된 예시(seed) — 사실 소스가 아니라 '문체·구성 참고'용.
"""
from __future__ import annotations

from app.config import RAG_EMB_MODEL, RAG_MIN_SIM, RAG_TOPK

# competency 계열 태그 → 유사 직무 톤 예시(seed). 마스킹(○○)으로 사실 베끼기 최소화.
_CORPUS: list[dict] = [
    {"id": "ex_qc", "role": "품질관리·검사",
     "text": "○○년간 품질검사를 담당하며 공정 데이터로 불량 원인을 추적하고 재발 방지 표준을 세웠습니다. 정밀 측정 장비로 기준을 지켰고 팀을 조율해 안정적으로 운영했습니다."},
    {"id": "ex_prod", "role": "생산관리",
     "text": "○○년간 제조 라인에서 생산관리를 맡아 인원과 공정을 조율했습니다. 사고 없이 흐름을 유지하는 것이 핵심임을 배웠고 안전 수칙을 현장 언어로 정리해 이어갔습니다."},
    {"id": "ex_logi", "role": "물류·현장관리",
     "text": "○○년간 입출고와 안전관리를 담당하며 재고 정확도를 높이고 오배송을 줄였습니다. 현장 안전수칙을 작업자 언어로 정리해 사고를 예방했습니다."},
    {"id": "ex_maint", "role": "설비보전",
     "text": "○○년간 설비 보전을 담당하며 예방정비 체계를 세워 비가동 시간을 줄였습니다. 이상 징후를 조기에 잡아내는 진단 경험이 강점입니다."},
    {"id": "ex_food", "role": "식품 위생/품질",
     "text": "○○년간 위생관리와 HACCP 운영을 담당했습니다. 기록과 점검을 습관화해 감사 대응력을 높이고 신입 위생교육을 정착시켰습니다."},
]

_model = None
_doc_vecs = None
_status = "uninit"  # uninit | ready | disabled


def _lazy():
    """임베더·문서벡터 최초 1회 준비. 미설치/실패면 disabled(생성은 계속)."""
    global _model, _doc_vecs, _status
    if _status != "uninit":
        return
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(RAG_EMB_MODEL)
        _doc_vecs = _model.encode([c["text"] for c in _CORPUS], normalize_embeddings=True)
        _status = "ready"
        print(f"[rag] 임베더 로드: {RAG_EMB_MODEL} · 코퍼스 {len(_CORPUS)}건")
    except Exception as e:  # noqa: BLE001 — 미설치/OOM 등. 숨기지 않고 비활성.
        _status = "disabled"
        print(f"[rag] 비활성(폴백): {e}")


def backend_status() -> str:
    _lazy()
    return _status  # ready | disabled


def corpus_size() -> int:
    return len(_CORPUS)


def retrieve(query: str, topk: int | None = None, min_sim: float | None = None) -> list[dict]:
    """유사 예시 top-k(임계값 이상). 각 항목 {id, role, sim, text}. 비활성이면 []."""
    _lazy()
    if _status != "ready" or not query:
        return []
    topk = RAG_TOPK if topk is None else topk
    min_sim = RAG_MIN_SIM if min_sim is None else min_sim
    import numpy as np
    qv = _model.encode([query], normalize_embeddings=True)[0]
    sims = _doc_vecs @ qv
    order = list(np.argsort(-sims))[:topk]
    out = []
    for i in order:
        s = float(sims[i])
        if s < min_sim:  # 임계값 미만은 주입 안 함(오염 방지)
            continue
        c = _CORPUS[i]
        out.append({"id": c["id"], "role": c["role"], "sim": round(s, 4), "text": c["text"]})
    return out
