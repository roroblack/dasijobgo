"""다시,출근 — Gemma 4 12B 클라이언트

vLLM/Ollama의 OpenAI 호환 엔드포인트를 호출한다.
모델을 bake-off에서 바꾸려면 config.MODEL만 교체(gemma4:12b ↔ gemma4:26b ↔ qwen3.6:27b).
"""

import json
from openai import OpenAI

import config
import prompts

_client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


def _chat(task: str, user_msg: str) -> str:
    """태스크별 system + 파라미터로 1회 생성."""
    system, _ = prompts.REGISTRY[task]
    resp = _client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        **config.GEN[task],
    )
    return resp.choices[0].message.content.strip()


# ── 태스크 함수 ─────────────────────────────────────────────

def onboarding_extract(conversation: str) -> dict:
    """상담 대화 → 구조화 dict. JSON 파싱 실패 시 원문 반환."""
    raw = _chat("onboarding_extract",
                prompts.build_onboarding_user(conversation))
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"_raw": raw, "_error": "JSON 파싱 실패"}


def resume_draft(job_posting: str, applicant_career: str,
                 length: str = "600자 내외",
                 rag_examples: str = "") -> str:
    """자소서 초안.
    job_posting / applicant_career 는 RAG(BGE-M3+FAISS)로 검색해 넘긴 텍스트를 그대로 주입.
    rag_examples = 유사 합격 톤 예시(선택). 없으면 기본 few-shot만 사용.
    """
    return _chat("resume_draft",
                 prompts.build_resume_user(job_posting, applicant_career,
                                           length=length,
                                           extra_examples=rag_examples))


def followup_questions(job_posting: str, qa_history: str) -> str:
    """Q1~Q3 답변 기반 Q4, Q5 생성."""
    return _chat("followup_question",
                 prompts.build_followup_user(job_posting, qa_history))


def interview_feedback(answer_summary: str, competency_analysis: str) -> str:
    """역량 분석(결정론/분류기 산출) 기반 피드백."""
    return _chat("interview_feedback",
                 prompts.build_feedback_user(answer_summary, competency_analysis))


def match_rationale(score_detail: str) -> str:
    """규칙 기반 매칭 점수의 근거 설명."""
    return _chat("match_rationale",
                 prompts.build_match_user(score_detail))


def schedule_phrasing(available_slots: str) -> str:
    """결정론 교집합으로 나온 가능 시간대의 정중한 제안문."""
    return _chat("schedule_phrasing",
                 prompts.build_schedule_user(available_slots))


# ── RAG seam (참고용 인터페이스) ────────────────────────────
# 실제 검색은 별도 모듈에서 BGE-M3 임베딩 + FAISS로 수행하고,
# 그 결과 텍스트를 위 resume_draft(job_posting=..., applicant_career=...)에 주입한다.
#
# def retrieve(query: str, k: int = 4) -> str:
#     vec = bge_m3.encode(query)
#     hits = faiss_index.search(vec, k)
#     return "\n".join(h.text for h in hits)
