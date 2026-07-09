"""다시,출근 — Gemma 4 12B 생성 설정

로컬 서빙(vLLM 또는 Ollama)의 OpenAI 호환 엔드포인트를 사용한다.
개발은 Ollama(무료 티어/노트북, 자동 4bit), 데모는 vLLM(A100 크레딧, bf16 풀컨텍스트).
"""

# ── 엔드포인트 ──────────────────────────────────────────────
# vLLM   : http://localhost:8000/v1   (MODEL = "google/gemma-4-12B-it")
# Ollama : http://localhost:11434/v1  (MODEL = "gemma4:12b")
BASE_URL = "http://localhost:11434/v1"   # 개발 기본값(Ollama)
API_KEY  = "EMPTY"                        # 로컬 서버는 인증 없음(더미)
MODEL    = "gemma4:12b"                    # 데모 vLLM면 "google/gemma-4-12B-it"

# ── 태스크별 생성 파라미터 ──────────────────────────────────
# temperature ↓ = 결정적. 추출/규칙성은 낮게, 생성은 중간.
# frequency_penalty: 한국어 반복 억제용(0.2~0.4 권장). 값은 bake-off에서 튜닝.
# 참고: Gemma 계열 기본 권장은 temp=1.0/top_p=0.95/top_k=64 이지만,
#       실무 태스크는 아래처럼 태스크별로 낮춰서 안정성을 확보한다.
GEN = {
    "onboarding_extract": dict(temperature=0.1, top_p=0.9,  max_tokens=1024, frequency_penalty=0.0),
    "resume_draft":       dict(temperature=0.6, top_p=0.9,  max_tokens=1200, frequency_penalty=0.3),
    "followup_question":  dict(temperature=0.7, top_p=0.95, max_tokens=400,  frequency_penalty=0.4),
    "interview_feedback": dict(temperature=0.4, top_p=0.9,  max_tokens=900,  frequency_penalty=0.3),
    "match_rationale":    dict(temperature=0.3, top_p=0.9,  max_tokens=500,  frequency_penalty=0.2),
    "schedule_phrasing":  dict(temperature=0.3, top_p=0.9,  max_tokens=400,  frequency_penalty=0.2),
}
