# -*- coding: utf-8 -*-
"""GGUF(4bit) 로컬 러너 — 논의된 한국어 소형 모델용. 첨부 prompts/config 재사용.

무GPU·여유 RAM 2GB 환경이라 2.1~2.4B는 4bit GGUF로만 구동 가능.
사용: python run_gguf_bakeoff.py <REPO_ID> <TAG> [FILE_SUBSTR=Q4_K_M]
"""
from __future__ import annotations
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.abspath(os.path.join(HERE, "..", "..", "output"))  # 저장소 루트/output
os.makedirs(OUTPUT, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "attached"))
import config, prompts  # 첨부 재사용

REPO = sys.argv[1]
TAG = sys.argv[2]
WANT = sys.argv[3] if len(sys.argv) > 3 else "Q4_K_M"
CAP = int(os.environ.get("CAP", "320"))

conversation = """
상담사: 어떤 일을 오래 하셨어요?
구직자: 자동차 부품 공장에서 품질검사를 한 25년 했어요. 반장까지 했고요.
상담사: 자격증이나 다룰 줄 아는 장비는요?
구직자: 지게차 면허 있고, 측정기 다루는 건 다 해봤습니다. 경기 남부 쪽에서 일하고 싶어요.
"""
job_posting = "품질관리 담당. 우대: 제조 현장 품질검사 경험, 측정장비 운용, 팀 관리."
career = "자동차 부품 제조 품질검사 25년, 반장(8명) 경력, 지게차 면허, 3차원 측정기 운용."
qa = """
Q1. 지원 동기? → 오래 한 품질검사 경험을 계속 살리고 싶어서.
Q2. 강점? → 불량 원인을 데이터로 찾아 재발을 막은 경험이 많다.
Q3. 팀 관리 경험? → 반장으로 8명을 이끌며 교대 근무를 조율했다.
"""
answer_summary = "불량 재발 방지 경험을 구체적 수치 없이 설명함. 팀 관리는 간단히 언급."
competency = "직무역량: 상(구체 사례 있음) / 전달력: 중(수치·결과 부족) / 리더십: 정보 부족."
score = "종합 82점. 직무 일치 92(품질검사 25년), 지역 100(경기남부), 근무형태 60(교대 가능)."
slots = "6/12(목) 14:00~16:00, 6/13(금) 10:00~11:00 (지원자·기업 공통 가능)"
TASKS = [
    ("onboarding_extract", prompts.build_onboarding_user(conversation)),
    ("resume_draft",       prompts.build_resume_user(job_posting, career, length="500자 내외")),
    ("followup_question",  prompts.build_followup_user(job_posting, qa)),
    ("interview_feedback", prompts.build_feedback_user(answer_summary, competency)),
    ("match_rationale",    prompts.build_match_user(score)),
    ("schedule_phrasing",  prompts.build_schedule_user(slots)),
]


def pick_file():
    from huggingface_hub import list_repo_files
    files = [f for f in list_repo_files(REPO) if f.lower().endswith(".gguf")]
    for f in files:
        if WANT.lower() in f.lower():
            return f
    for f in files:
        if "q4" in f.lower():
            return f
    return files[0]


def main():
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama
    fname = pick_file()
    print(f"[dl] {REPO} :: {fname}", flush=True)
    path = hf_hub_download(REPO, fname)
    t0 = time.perf_counter()
    llm = Llama(model_path=path,
                n_ctx=int(os.environ.get("N_CTX", "4096")),
                n_batch=int(os.environ.get("N_BATCH", "512")),
                n_threads=os.cpu_count() or 4, verbose=False)
    print(f"[load] {time.perf_counter()-t0:.1f}s", flush=True)

    results = []
    for task, user_msg in TASKS:
        system = prompts.REGISTRY[task][0]
        g = config.GEN[task]
        rep = round(1.1 + 0.2 * float(g.get("frequency_penalty", 0.0)), 3)
        ts = time.perf_counter()
        r = llm.create_chat_completion(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}],
            temperature=float(g["temperature"]), top_p=float(g["top_p"]),
            max_tokens=min(int(g["max_tokens"]), CAP), repeat_penalty=rep,
        )
        dt = time.perf_counter() - ts
        text = r["choices"][0]["message"]["content"].strip()
        n_new = r.get("usage", {}).get("completion_tokens", 0)
        tps = n_new / dt if dt > 0 else 0
        print(f"\n===== {task} · {dt:.1f}s · {n_new}tok · {tps:.1f} tok/s =====\n{text}", flush=True)
        results.append({"task": task, "seconds": round(dt, 2), "new_tokens": n_new,
                        "tokens_per_sec": round(tps, 2), "output": text})

    meta = {"model_repo": REPO, "gguf_file": fname, "tag": TAG,
            "device": "cpu", "quant": WANT, "cap_new_tokens": CAP}
    with open(os.path.join(OUTPUT, f"bakeoff_{TAG}.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "results": results}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT, f"bakeoff_{TAG}.md"), "w", encoding="utf-8") as f:
        f.write(f"# {TAG} — {REPO} ({fname})\n\n")
        tot = sum(r["seconds"] for r in results)
        f.write(f"- 4bit GGUF · CPU · 6태스크 합계 {tot:.1f}s\n\n")
        for r in results:
            f.write(f"## {r['task']} · {r['seconds']}s · {r['new_tokens']}tok · {r['tokens_per_sec']} tok/s\n\n```\n{r['output']}\n```\n\n")
    print(f"\n[saved] output/bakeoff_{TAG}.json / .md", flush=True)


if __name__ == "__main__":
    main()
