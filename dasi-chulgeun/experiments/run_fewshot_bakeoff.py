# -*- coding: utf-8 -*-
"""가이드 형식 정렬 효과 측정 — 자소서 few-shot 오염 개선 검증.

같은 모델·같은 입력으로 자소서를 두 번 생성:
  OLD = 원본 프롬프트(물류센터 단일 few-shot, 원본 system)
  NEW = 고용24 가이드 정렬 프롬프트(마스킹된 다중 예시 + '예시 사실 베끼지 말 것' 규칙)
오염 지표(물류/22년/무재해/40명 등 old-fewshot 사실 유입, 25년 정확 유지)를 비교.
대상: EXAONE-3.5-2.4B, Kanana-2.1B (둘 다 캐시됨).
"""
from __future__ import annotations
import json, os, sys, time, gc
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.abspath(os.path.join(HERE, "..", "..", "output"))
os.makedirs(OUTPUT, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "attached"))
import config, prompts  # NEW = 정렬된 현재 prompts

MODELS = [
    ("lmstudio-community/EXAONE-3.5-2.4B-Instruct-GGUF", "exaone", "Q4_K_M"),
    ("ch00n/kanana-nano-2.1b-instruct-Q4_K_M-GGUF", "kanana", "Q4_K_M"),
]
JD = "품질관리 담당. 우대: 제조 현장 품질검사 경험, 측정장비 운용, 팀 관리."
CAREER = "자동차 부품 제조 품질검사 25년, 반장(8명) 경력, 지게차 면허, 3차원 측정기 운용."

# ── OLD(원본) 프롬프트 — 정렬 전 상태를 그대로 재현 ──
OLD_SYSTEM = """당신은 40~50대 중장년 구직자의 재취업을 돕는 서류 작성 전문가입니다.
반드시 지키세요:
1. [지원자 경력]에 있는 사실만 사용합니다. 없는 경력·수치·자격을 지어내지 않습니다.
2. [채용공고]의 직무·우대사항에 맞춰 관련 경력을 앞세워 재배치합니다.
3. 톤: 과장과 미사여구를 피하고, 오랜 실무에서 나오는 신뢰감과 구체성을 살립니다.
4. 중장년의 강점(책임감, 위기 대응, 조직 안정화, 후배 육성)을 자연스럽게 녹이되
   나이를 직접 언급하지 않습니다.
5. 요청 분량·형식을 지킵니다. 불릿 남발 없이 문단으로 씁니다.
출력은 자기소개서 본문만. 설명·머리말 없이."""
OLD_FEWSHOT = """[예시 입력]
채용공고: 물류센터 현장관리자. 우대: 현장 안전관리 경험, 다수 인원 관리.
지원자 경력: 제조공장 생산관리 22년, 40명 규모 라인 관리, 무재해 3년 달성.
[예시 출력]
22년간 제조 현장에서 생산관리를 맡으며 최대 40명 규모의 라인을 운영했습니다.
인원과 공정이 얽히는 현장에서 가장 중요한 것은 사고 없이 흐름을 유지하는 일이라
배웠고, 안전 수칙을 현장 언어로 다시 정리해 3년 연속 무재해를 이뤘습니다.
쌓아온 현장 감각을 물류센터 안전관리에 그대로 옮겨 쓰겠습니다."""

def old_user():
    return f"""{OLD_FEWSHOT}

[채용공고]
{JD}

[지원자 경력]
{CAREER}

위 경력 사실만으로, 이 공고에 맞춘 자기소개서를 500자 내외로 작성하세요."""

# old-fewshot 사실이 유입되면 오염(품질관리 지원자에겐 물류/22년/무재해/40명은 남의 사실)
LEAK = ["물류", "22년", "무재해", "40명", "생산관리"]

def flags(text: str) -> dict:
    return {**{k: text.count(k) for k in LEAK}, "25년_정확": ("25년" in text)}


def gen(llm, system, user):
    g = config.GEN["resume_draft"]
    ts = time.perf_counter()
    r = llm.create_chat_completion(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=float(g["temperature"]), top_p=float(g["top_p"]),
        max_tokens=min(int(g["max_tokens"]), 320), repeat_penalty=1.15,
    )
    return r["choices"][0]["message"]["content"].strip(), round(time.perf_counter() - ts, 1)


def load(repo, want):
    from huggingface_hub import list_repo_files, hf_hub_download
    from llama_cpp import Llama
    files = [f for f in list_repo_files(repo) if f.lower().endswith(".gguf")]
    fname = next((f for f in files if want.lower() in f.lower()), files[0])
    return Llama(model_path=hf_hub_download(repo, fname), n_ctx=4096, n_batch=128,
                 n_threads=os.cpu_count() or 4, verbose=False)


def main():
    results = []
    new_user = prompts.build_resume_user(JD, CAREER, length="500자 내외")  # NEW 정렬 프롬프트
    for repo, tag, want in MODELS:
        print(f"[load] {tag}", flush=True)
        llm = load(repo, want)
        old_txt, old_s = gen(llm, OLD_SYSTEM, old_user())
        new_txt, new_s = gen(llm, prompts.RESUME_SYSTEM, new_user)
        of, nf = flags(old_txt), flags(new_txt)
        print(f"\n##### {tag} — OLD leak={ {k:of[k] for k in LEAK if of[k]} } 25년={of['25년_정확']}", flush=True)
        print(old_txt, flush=True)
        print(f"\n##### {tag} — NEW leak={ {k:nf[k] for k in LEAK if nf[k]} } 25년={nf['25년_정확']}", flush=True)
        print(new_txt, flush=True)
        results.append({"model": tag, "old": {"text": old_txt, "sec": old_s, "flags": of},
                        "new": {"text": new_txt, "sec": new_s, "flags": nf}})
        del llm; gc.collect()

    with open(os.path.join(OUTPUT, "fewshot_align_compare.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT, "fewshot_align_compare.md"), "w", encoding="utf-8") as f:
        f.write("# 가이드 형식 정렬 전/후 자소서 비교 (few-shot 오염)\n\n")
        f.write("- OLD = 원본(물류센터 단일 few-shot) · NEW = 고용24 가이드 정렬(마스킹 다중 예시 + '예시 사실 베끼지 말 것' 규칙)\n")
        f.write("- 오염 지표: 물류/22년/무재해/40명/생산관리 유입 횟수(품질관리 지원자에겐 남의 사실) · 25년=본인 경력 유지\n\n")
        for r in results:
            f.write(f"## {r['model']}\n\n")
            for key in ["old", "new"]:
                d = r[key]; lk = {k: v for k, v in d["flags"].items() if k in LEAK and v}
                tag = "① OLD(정렬 전)" if key == "old" else "② NEW(정렬 후)"
                f.write(f"### {tag} · {d['sec']}s · 오염={lk or '없음'} · 25년유지={d['flags']['25년_정확']}\n\n```\n{d['text']}\n```\n\n")
    print("\n[saved] output/fewshot_align_compare.md / .json", flush=True)


if __name__ == "__main__":
    main()
