"""다시,출근 — Gemma 4 12B 동작 예시 (서버 먼저 띄운 뒤 실행)

    ollama serve &            # 또는 vLLM
    ollama pull gemma4:12b
    python example_usage.py
"""

import client

# ── 1) 온보딩: 대화 → 구조화 ───────────────────────────────
conversation = """
상담사: 어떤 일을 오래 하셨어요?
구직자: 자동차 부품 공장에서 품질검사를 한 25년 했어요. 반장까지 했고요.
상담사: 자격증이나 다룰 줄 아는 장비는요?
구직자: 지게차 면허 있고, 측정기 다루는 건 다 해봤습니다. 경기 남부 쪽에서 일하고 싶어요.
"""
print("── 온보딩 추출 ──")
print(client.onboarding_extract(conversation))

# ── 2) 자소서 초안 (RAG로 넘어온 텍스트라고 가정) ──────────
job_posting = "품질관리 담당. 우대: 제조 현장 품질검사 경험, 측정장비 운용, 팀 관리."
career = "자동차 부품 제조 품질검사 25년, 반장(8명) 경력, 지게차 면허, 3차원 측정기 운용."
print("\n── 자소서 초안 ──")
print(client.resume_draft(job_posting, career, length="500자 내외"))

# ── 3) 꼬리질문 Q4~Q5 ──────────────────────────────────────
qa = """
Q1. 지원 동기? → 오래 한 품질검사 경험을 계속 살리고 싶어서.
Q2. 강점? → 불량 원인을 데이터로 찾아 재발을 막은 경험이 많다.
Q3. 팀 관리 경험? → 반장으로 8명을 이끌며 교대 근무를 조율했다.
"""
print("\n── 꼬리질문 ──")
print(client.followup_questions(job_posting, qa))

# ── 4) 피드백 (역량 분석은 분류기 산출이라고 가정) ─────────
answer_summary = "불량 재발 방지 경험을 구체적 수치 없이 설명함. 팀 관리는 간단히 언급."
competency = "직무역량: 상(구체 사례 있음) / 전달력: 중(수치·결과 부족) / 리더십: 정보 부족."
print("\n── 피드백 ──")
print(client.interview_feedback(answer_summary, competency))

# ── 5) 매칭 근거 ───────────────────────────────────────────
score = "종합 82점. 직무 일치 92(품질검사 25년), 지역 100(경기남부), 근무형태 60(교대 가능)."
print("\n── 매칭 근거 ──")
print(client.match_rationale(score))

# ── 6) 일정 제안 ───────────────────────────────────────────
slots = "6/12(목) 14:00~16:00, 6/13(금) 10:00~11:00 (지원자·기업 공통 가능)"
print("\n── 일정 제안 ──")
print(client.schedule_phrasing(slots))
