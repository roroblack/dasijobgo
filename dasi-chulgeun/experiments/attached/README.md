# 다시,출근 — Gemma 4 12B 실사용 세팅

Gemma 4 12B(Apache 2.0, 통합 멀티모달, 16GB에서 Q4 구동)를 실제 파이프라인에 붙이는 최소 세트.
온보딩·자소서·꼬리질문·피드백·매칭근거·일정 6개 태스크를 하나의 서빙 + 태스크별 프롬프트로 처리한다.

## 파일

| 파일 | 역할 |
|---|---|
| `config.py` | 엔드포인트 + 태스크별 생성 파라미터(temperature 등) |
| `prompts.py` | 태스크별 한국어 system 프롬프트 + user 메시지 빌더(+few-shot) |
| `client.py` | OpenAI 호환 호출 래퍼 + 태스크 함수 + RAG seam |
| `example_usage.py` | mock 데이터로 6개 태스크 실행 데모 |

## 1. 서빙 — 두 갈래

### 개발(무료 티어/노트북): Ollama — 자동 4bit, 한 줄
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:12b        # 정확한 태그는 ollama.com/library/gemma4 확인
ollama serve                  # http://localhost:11434/v1
```
→ 16GB VRAM(무료 Colab T4)이나 통합메모리 16GB 맥에서 구동. `config.py` 기본값이 이쪽.

### 데모(A100 크레딧): vLLM — bf16, 풀컨텍스트, 고처리량
```bash
pip install vllm openai
vllm serve google/gemma-4-12B-it \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype bfloat16
# → http://localhost:8000/v1
```
그 다음 `config.py`에서:
```python
BASE_URL = "http://localhost:8000/v1"
MODEL    = "google/gemma-4-12B-it"
```
> 16GB에서 vLLM으로 돌리려면 4bit 양자화: `--quantization bitsandbytes --load-format bitsandbytes`.
> 개발은 Ollama, 상시 데모는 크레딧 A100 vLLM으로 분리하는 걸 권장(무료 티어는 세션 끊김 리스크).

## 2. 실행
```bash
pip install openai
python example_usage.py
```

## 3. 파라미터 근거 (config.GEN)

| 태스크 | temp | 이유 |
|---|---|---|
| onboarding_extract | 0.1 | JSON 추출 — 결정적, 지어내기 금지 |
| resume_draft | 0.6 | 생성이지만 사실 기반 — 과한 창의성 억제 |
| followup_question | 0.7 | 답변별로 달라져야 함 — 다양성 필요 |
| interview_feedback | 0.4 | 일관되고 신중하게 |
| match_rationale | 0.3 | 규칙 산출 점수를 설명만 — 낮게 |
| schedule_phrasing | 0.3 | 정해진 시간대 안에서만 — 낮게 |

`frequency_penalty` 0.2~0.4는 한국어 반복 억제용. 값은 bake-off에서 조정.
Gemma 기본 권장(temp 1.0/top_p 0.95/top_k 64)은 실무 태스크엔 과해서 위처럼 낮춤.

## 4. RAG 결합 지점

`resume_draft(job_posting, applicant_career)`의 두 인자는 **BGE-M3 임베딩 + FAISS 검색으로
뽑아 넘긴 텍스트**를 그대로 받는다. 검색 자체는 CPU에서 도는 별도 모듈이고, 이 클라이언트는
검색 결과를 프롬프트에 주입하는 역할만 한다(`client.py` 하단 seam 주석 참고).
→ 자소서 품질은 모델 체급보다 **주입되는 공고 JD·경력 조각의 질**이 더 좌우한다.

## 5. bake-off 스왑

모델 비교는 `config.MODEL` 한 줄만 바꾸면 된다(프롬프트·코드 그대로):
```python
MODEL = "gemma4:12b"      # 무료 티어 후보
MODEL = "gemma4:26b"      # 균형 후보
MODEL = "qwen3.6:27b"     # 한국어 유력 후보
```
같은 10개 프롬프트를 세 모델에 돌려 팀원 3명이 blind 채점(자연스러움 / 구체성 / 중장년 톤).
채점 축에 **"12B가 26B/Qwen 대비 손실률"**을 넣어, 손실이 작으면 12B(무료 티어) 확정.

## 6. 주의

- 온보딩 추출은 JSON 강제지만 모델이 가끔 깨뜨린다 → `client.onboarding_extract`가
  코드펜스 제거 후 파싱, 실패 시 `_raw`로 원문 반환. 운영에선 재시도 1회 로직 추가 권장.
- 자소서 few-shot은 지금 1개(`prompts.RESUME_FEWSHOT`) → **중장년 재취업 예시 3~5개로 늘리면
  톤이 확 안정**된다. 이게 파인튜닝보다 먼저 할 일.
- Gemma 4 12B는 오디오 입력 네이티브지만 전용 STT만큼 정확한지는 미검증 → STT 확정 전
  별도 벤치 필요(음성 이력서 입력 태스크).
