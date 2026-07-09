# -*- coding: utf-8 -*-
"""백엔드 통합 검증 — resume_usecase.build_resume 를 실제 코드 경로로 호출.

  python integration_test.py rag      # 빠름: RAG 검색만(LLM 템플릿 폴백), import·배선 확인
  python integration_test.py full      # Gemma-4-E4B GGUF + RAG 실동작(느림)
"""
from __future__ import annotations
import json, os, sys, time
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MODE = sys.argv[1] if len(sys.argv) > 1 else "rag"

# 전체 모드면 config import 전에 LLM_GGUF_PATH 를 세팅해야 한다.
if MODE == "full":
    from huggingface_hub import hf_hub_download
    os.environ["LLM_GGUF_PATH"] = hf_hub_download(
        "google/gemma-4-E4B-it-qat-q4_0-gguf", "gemma-4-E4B_q4_0-it.gguf")
    os.environ.setdefault("LLM_N_BATCH", "64")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "backend")))

from app.application import resume_usecase  # noqa: E402
from app.infrastructure import rag  # noqa: E402

print(f"[mode] {MODE} · rag_backend={rag.backend_status()} · corpus={rag.corpus_size()}", flush=True)
t = time.perf_counter()
r = resume_usecase.build_resume("J001", 25, ["품질관리", "검사장비", "불량분석"], "인천 남동구")
dt = round(time.perf_counter() - t, 1)

out = {"seconds": dt, "source": r["_source"], "rag": r["rag"],
       "company": r["company"], "resume_body": r["resume_body"]}
print(json.dumps(out, ensure_ascii=False, indent=2), flush=True)

with open(os.path.join(HERE, "..", "..", "output", f"integration_{MODE}.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"[saved] output/integration_{MODE}.json", flush=True)
