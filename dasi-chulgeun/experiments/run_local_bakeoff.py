# -*- coding: utf-8 -*-
"""로컬 저용량 테스트 러너 — 첨부 모듈(prompts.py·config.py)을 그대로 재사용.

첨부 client.py 는 Ollama/vLLM OpenAI 엔드포인트가 필요한데 이 노트북(무GPU·저RAM)엔
그 12B 서빙을 못 올린다. 그래서 '가장 가벼운' 생성 모델을 transformers 로 직접 띄우고,
attached/prompts.py 의 태스크별 system + build_user, config.py 의 GEN 파라미터를 그대로 적용해
example_usage.py 의 mock 6태스크를 돌린다. => 프롬프트 설계·파이프라인을 실검증(모델 체급은 별개).
"""
from __future__ import annotations
import json, os, sys, time, gc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "attached"))
import config, prompts  # 첨부 파일 재사용

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"   # 이 사양에서 도는 최소급 한국어 가능 instruct
CAP_NEW_TOKENS = 320                       # CPU·저RAM 고려해 상한(첨부 config max_tokens 는 더 큼)

# example_usage.py 와 동일한 mock 입력
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


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(os.cpu_count() or 4)

    t0 = time.perf_counter()
    print(f"[load] {MODEL_ID} …", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True,
    )
    model.eval()
    load_s = time.perf_counter() - t0
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[load] done in {load_s:.1f}s · params={n_params/1e6:.0f}M", flush=True)

    results = []
    for task, user_msg in TASKS:
        system = prompts.REGISTRY[task][0]
        g = config.GEN[task]
        temp = float(g["temperature"])
        rep = round(1.1 + 0.25 * float(g.get("frequency_penalty", 0.0)), 3)  # freq_penalty 근사
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                      return_tensors="pt", return_dict=True)
        input_ids = enc["input_ids"]
        gen_kw = dict(
            max_new_tokens=min(int(g["max_tokens"]), CAP_NEW_TOKENS),
            repetition_penalty=rep, pad_token_id=tok.eos_token_id,
        )
        if temp <= 0.05:
            gen_kw.update(do_sample=False)
        else:
            gen_kw.update(do_sample=True, temperature=temp, top_p=float(g["top_p"]))
        ts = time.perf_counter()
        with __import__("torch").inference_mode():
            out = model.generate(**enc, **gen_kw)
        dt = time.perf_counter() - ts
        new_ids = out[0][input_ids.shape[1]:]
        text = tok.decode(new_ids, skip_special_tokens=True).strip()
        n_new = int(new_ids.shape[0])
        tps = n_new / dt if dt > 0 else 0
        print(f"\n===== {task} · {dt:.1f}s · {n_new}tok · {tps:.1f} tok/s =====", flush=True)
        print(text, flush=True)
        results.append({
            "task": task, "seconds": round(dt, 2), "new_tokens": n_new,
            "tokens_per_sec": round(tps, 2), "temperature": temp,
            "repetition_penalty": rep, "output": text,
        })

    meta = {
        "model": MODEL_ID, "params_million": round(n_params / 1e6),
        "device": "cpu", "dtype": "bfloat16", "threads": torch.get_num_threads(),
        "load_seconds": round(load_s, 1), "cap_new_tokens": CAP_NEW_TOKENS,
        "note": "저용량 스탠드인(0.5B). 의도 모델은 Gemma4 12B — 품질 아닌 파이프라인·플로어 품질 확인용.",
    }
    out_json = os.path.join(HERE, "bakeoff_outputs.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "results": results}, f, ensure_ascii=False, indent=2)

    out_md = os.path.join(HERE, "bakeoff_outputs.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# 로컬 저용량 실행 결과 — {MODEL_ID}\n\n")
        f.write(f"- 장치: CPU({meta['threads']}스레드), dtype bfloat16, 파라미터 ~{meta['params_million']}M\n")
        f.write(f"- 로드 {meta['load_seconds']}s · 생성 상한 {CAP_NEW_TOKENS} tok\n")
        f.write(f"- ⚠️ {meta['note']}\n\n")
        for r in results:
            f.write(f"## {r['task']}  ·  {r['seconds']}s · {r['new_tokens']}tok · {r['tokens_per_sec']} tok/s\n\n")
            f.write("```\n" + r["output"] + "\n```\n\n")
    print(f"\n[saved] {out_json}\n[saved] {out_md}", flush=True)
    del model; gc.collect()


if __name__ == "__main__":
    main()
