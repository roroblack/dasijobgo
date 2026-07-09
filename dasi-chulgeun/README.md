# 다시,출근 — 중장년 재취업 실행 에이전트 (프로토타입)

일자리를 **추천**하는 데서 멈추지 않고, 취업까지 가는 **실행 루프**(상담 → 대화 온보딩 → 매칭 → 지원 → **AI 아바타 면접** → 피드백·결과 대기 → 실면접 일정 → 교육 → 재지원)를 끝까지 밀어주는 에이전트의 동작 프로토타입. 화면·순서는 목업 개편본(`../init_plans/*_화면흐름_목업.html`) 기준.

> 기획·리서치 원본은 [`../init_plans/`](../init_plans/) 참고. 작업 규칙은 [`../RULE.md`](../RULE.md).

## 빠른 실행

```powershell
# dasi-chulgeun 폴더에서 (Windows PowerShell)
.\run_all.ps1
```
```bash
# 또는 (bash)
./run_all.sh
```
브라우저에서 **http://127.0.0.1:8090** → 12화면 플로우 체험(시작→온보딩→…→AI 아바타 면접→재지원 루프). 상단 툴바로 **글자 크기(16/18/21px, 기본 18px)** 조절(중장년 접근성). API 문서: `/docs`.

수동 실행:
```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r backend/requirements.txt   # (bash: .venv/bin/python)
cd backend && ..\.venv\Scripts\python -m uvicorn app.main:app --port 8090
```

## 설계 원칙 (RULE.md 반영)

- **결정론 vs 언어계층 분리(§3.3)**: 적합도·일정 교집합·역량 갭은 `app/domain/` 순수 함수가 계산. LLM 은 대화·이력서 문장·피드백 문장 등 **언어 계층**에만.
- **하드코딩·폴백 최소화(§3)**: 계산 가능한 값은 상수로 박지 않음. 폴백은 외부 의존성 부재 시에만 쓰고 응답 `meta.source` 로 드러냄.
  - `llm` : 키(`ANTHROPIC_API_KEY`) 없으면 템플릿 **fallback**
  - `jobs`/`training` : data.go.kr 미연동이라 **seed** (고용24 직접연동은 기업회원 전용 — 근거: 브리핑 §04)
  - 화상 링크 : 국산 API 미확보 → Meet 형식 **fallback**
- **응답 봉투(§4)**: 모든 API 는 `{ok, data, meta, error}`, `meta.source ∈ {live, seed, fallback}`.

## 구조 (클린 아키텍처)

```
dasi-chulgeun/
  backend/app/
    domain/          매칭·일정·역량갭 (순수 함수, 결정론)
    application/     usecase (도메인 + 인프라 오케스트레이션)
    infrastructure/  data(seed)·llm(폴백)·store(memory)
    interfaces/http/ 라우터 + {ok,data,meta,error} 봉투
    schemas/         pydantic 요청 스키마
  frontend/          의존성 없는 정적 SPA (12화면 플로우 + 글자크기 접근성)
  tests/             domain 결정론 단위 테스트
```

## API 요약

| 메서드 | 경로 | 설명 | source |
|---|---|---|---|
| GET | `/health` | 상태 + 소스 표기 | live |
| POST | `/onboarding` | 대화 온보딩 → 프로필 | live/fallback |
| POST | `/matching` | 프로필 → 적합도 순위 | seed |
| POST | `/resume` | 회사별 맞춤 이력서 + 4종 안내 | live/fallback |
| POST | `/schedule/confirm` | 가능시간 교집합 → 확정 + 링크 | live |
| POST | `/interview/questions` | 회사 정보 → 면접 질문 Q1~5 (Q1~3 규칙, Q4~5 LLM 꼬리질문) | live/fallback |
| POST | `/interview/analyze` | 역량 갭 + 훈련 추천 (STEP 9 연습 피드백 등급화·STEP 10 교육 매핑) | live/fallback |

## 테스트

```bash
cd backend && ..\.venv\Scripts\python -m pytest -q
```
결정론 로직(점수·교집합·등급)이 상수 하드코딩이 아님을 단위로 검증.

## 라이브 LLM (선택)

`backend/requirements.txt` 의 `anthropic` 주석을 풀어 설치하고 `ANTHROPIC_API_KEY` 를 설정하면
온보딩 멘트·이력서 문장·피드백 요약이 템플릿 폴백 대신 실제 생성으로 전환됩니다(응답 `source: live`).
