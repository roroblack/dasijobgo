# -*- coding: utf-8 -*-
"""RAG 적용 테스트 — 첨부 설계(BGE-M3 임베딩 + 검색 → resume_draft 주입) 실검증.

목적: (1) 논의한 임베딩 모델(BGE-M3)을 실제로 돌려보고,
      (2) RAG로 유사 예시를 주입하면 자소서의 few-shot 오염(예: '22년/물류센터' 베끼기)이
          개선되는지 'RAG 없음 vs 있음'을 같은 생성 모델로 비교한다.

임베딩: BAAI/bge-m3 (첨부 README §4가 지목한 스택) · CPU
검색:   코사인 top-k (소규모 코퍼스라 FAISS 대신 브루트포스 — 동일 결과)
생성:   기존 GGUF(기본 EXAONE-3.5-2.4B, 캐시됨) · llama.cpp
사용:   python run_rag_bakeoff.py            (기본 EXAONE)
        GEN_REPO=<repo> GEN_WANT=Q4_K_M python run_rag_bakeoff.py
"""
from __future__ import annotations
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.abspath(os.path.join(HERE, "..", "..", "output"))
os.makedirs(OUTPUT, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "attached"))
import config, prompts

EMB_MODEL = os.environ.get("EMB_MODEL", "BAAI/bge-m3")
GEN_REPO = os.environ.get("GEN_REPO", "lmstudio-community/EXAONE-3.5-2.4B-Instruct-GGUF")
GEN_WANT = os.environ.get("GEN_WANT", "Q4_K_M")
TOPK = int(os.environ.get("TOPK", "2"))

# ── 소규모 코퍼스: 중장년 합격 자소서 예시(⚠️ 전부 가공된 예시 데이터 seed, 실측 아님) ──
SEED_CORPUS = [
    {"id": "ex_qc", "role": "품질관리/검사",
     "text": ("자동차 부품 제조 현장에서 25년간 품질검사를 담당하며 3차원 측정기와 각종 계측장비를 운용했습니다. "
              "공정 불량률을 데이터로 추적해 재발 방지 표준을 세웠고, 반장으로 팀원 8명의 교대 근무를 조율했습니다. "
              "오랜 현장에서 배운 것은 사고 없이 기준을 지키는 일이며, 그 감각을 새 현장의 품질관리에 그대로 옮기겠습니다.")},
    {"id": "ex_prod", "role": "생산관리",
     "text": ("제조 라인에서 22년간 생산관리를 맡아 40명 규모 라인을 운영하고 무재해 3년을 달성했습니다. "
              "인원과 공정이 얽히는 현장에서 흐름을 끊지 않는 조율이 핵심임을 배웠습니다.")},
    {"id": "ex_logi", "role": "물류/현장관리",
     "text": ("물류센터 현장에서 18년간 입출고와 안전관리를 담당했습니다. 지게차 운용과 재고 정확도 관리로 "
              "오배송을 줄였고, 현장 안전수칙을 작업자 언어로 다시 정리해 사고를 예방했습니다.")},
    {"id": "ex_maint", "role": "설비보전",
     "text": ("생산설비 보전을 20년간 담당하며 예방정비 체계를 세워 비가동 시간을 크게 줄였습니다. "
              "전기·기계 복합 설비의 이상 징후를 조기에 잡아내는 진단 경험이 강점입니다.")},
    {"id": "ex_food", "role": "식품 위생/품질",
     "text": ("식품 제조에서 15년간 위생관리와 HACCP 운영을 담당했습니다. 기록과 점검을 습관화해 "
              "감사 대응력을 높였고, 신입 위생교육 프로그램을 만들어 현장에 정착시켰습니다.")},
]


def embed_and_retrieve(query: str):
    from sentence_transformers import SentenceTransformer
    import numpy as np
    t = time.perf_counter()
    model = SentenceTransformer(EMB_MODEL)
    docs = [c["text"] for c in SEED_CORPUS]
    dv = model.encode(docs, normalize_embeddings=True)
    qv = model.encode([query], normalize_embeddings=True)[0]
    sims = (dv @ qv)
    order = list(np.argsort(-sims))
    top = [(SEED_CORPUS[i]["id"], SEED_CORPUS[i]["role"], float(sims[i]), SEED_CORPUS[i]["text"]) for i in order[:TOPK]]
    return top, round(time.perf_counter() - t, 1), model.get_sentence_embedding_dimension()


def gen_llm():
    from huggingface_hub import list_repo_files, hf_hub_download
    from llama_cpp import Llama
    files = [f for f in list_repo_files(GEN_REPO) if f.lower().endswith(".gguf")]
    fname = next((f for f in files if GEN_WANT.lower() in f.lower()), files[0])
    path = hf_hub_download(GEN_REPO, fname)
    llm = Llama(model_path=path, n_ctx=4096, n_batch=128, n_threads=os.cpu_count() or 4, verbose=False)
    return llm, fname


def resume(llm, job_posting, career, extra):
    g = config.GEN["resume_draft"]
    r = llm.create_chat_completion(
        messages=[{"role": "system", "content": prompts.REGISTRY["resume_draft"][0]},
                  {"role": "user", "content": prompts.build_resume_user(job_posting, career, length="500자 내외", extra_examples=extra)}],
        temperature=float(g["temperature"]), top_p=float(g["top_p"]),
        max_tokens=min(int(g["max_tokens"]), 320), repeat_penalty=1.15,
    )
    return r["choices"][0]["message"]["content"].strip()


def main():
    # example_usage.py 와 동일 입력
    job_posting = "품질관리 담당. 우대: 제조 현장 품질검사 경험, 측정장비 운용, 팀 관리."
    career = "자동차 부품 제조 품질검사 25년, 반장(8명) 경력, 지게차 면허, 3차원 측정기 운용."

    print(f"[emb] {EMB_MODEL} 로드+검색 …", flush=True)
    top, emb_s, dim = embed_and_retrieve(career)
    print(f"[emb] dim={dim} · {emb_s}s · top{TOPK}=" + ", ".join(f"{i}({s:.3f})" for i, _, s, _ in top), flush=True)

    print(f"[gen] {GEN_REPO} 로드 …", flush=True)
    llm, gfile = gen_llm()

    rag_block = "\n\n".join(f"[유사 합격 예시 · {role}]\n{txt}" for _id, role, _s, txt in top)
    t = time.perf_counter(); no_rag = resume(llm, job_posting, career, ""); no_s = round(time.perf_counter() - t, 1)
    t = time.perf_counter(); with_rag = resume(llm, job_posting, career, rag_block); yes_s = round(time.perf_counter() - t, 1)

    meta = {"embed_model": EMB_MODEL, "embed_dim": dim, "gen_repo": GEN_REPO, "gen_file": gfile,
            "topk": TOPK, "retrieved": [{"id": i, "role": r, "score": round(s, 4)} for i, r, s, _ in top]}
    with open(os.path.join(OUTPUT, "rag_resume_compare.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "no_rag": no_rag, "with_rag": with_rag}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT, "rag_resume_compare.md"), "w", encoding="utf-8") as f:
        f.write(f"# RAG 적용 비교 — 자소서(resume_draft)\n\n")
        f.write(f"- 임베딩: `{EMB_MODEL}` (dim {dim}) · 검색 {emb_s}s · 코퍼스 예시 {len(SEED_CORPUS)}건(seed)\n")
        f.write(f"- 생성: `{GEN_REPO}` ({gfile}) · CPU 4bit\n")
        f.write(f"- 검색 top-{TOPK}: " + ", ".join(f"{i} `{r}` (cos {s:.3f})" for i, r, s, _ in top) + "\n\n")
        f.write(f"## ① RAG 없음 (하드코딩 few-shot 1개) · {no_s}s\n\n```\n{no_rag}\n```\n\n")
        f.write(f"## ② RAG 있음 (유사 예시 {TOPK}건 주입) · {yes_s}s\n\n```\n{with_rag}\n```\n\n")
        f.write("> ⚠️ 코퍼스는 가공된 예시(seed). 관전 포인트: ②가 '25년' 등 지원자 실제 사실을 지키고 "
                "엉뚱한 예시(물류센터 등)를 덜 베끼는가.\n")
    print(f"\n[saved] output/rag_resume_compare.md / .json", flush=True)


if __name__ == "__main__":
    main()
