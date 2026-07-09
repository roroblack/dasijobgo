# 다시,출근 — 중장년 창업 지원 트랙 (프로토타입)

재취업 파이프라인과 **동일 아키텍처**(음성 온보딩 → AI 후보 생성 → 규칙 기반 검증 → 사람 핸드오프)를
**창업 도메인**에 적용한 확장 트랙의 동작 프로토타입. 화면·순서는 창업 트랙 목업·계획서
(`../init_plans/startup/*`) 기준. **AI는 후보·근거·위험까지, 결정과 확신은 사람의 몫.**

> 원본 기획: [`../init_plans/startup/`](../init_plans/startup/) · 작업 규칙: [`../RULE.md`](../RULE.md)
> 형제 프로젝트(재취업 트랙): [`../dasi-chulgeun/`](../dasi-chulgeun/) — 코드·인프라 재사용률 ~40%

## 빠른 실행

```powershell
.\run_all.ps1        # Windows PowerShell (venv 는 ../dasi-chulgeun/.venv 공유)
```
```bash
./run_all.sh         # bash
```
브라우저 **http://127.0.0.1:8091** → START + 7 STEP 흐름 체험. 상단 바로 글자 크기(15/17/20px) 조절.
재취업 트랙(8090)과 **동시 구동 가능**. API 문서: `/docs`.

## 흐름 (START + 7 STEP)

| 화면 | STEP | 백엔드 | 성격 |
|---|---|---|---|
| 시작 | START | — | 상담사 동행 + 완주 리워드 |
| 경력 온보딩 | 1 | `/onboarding` (+`/stt`) | 공통 재사용(음성 온보딩) |
| 창업 정보 보충 | 2 | (프론트 슬롯) | 자본·점포·신체 조건 |
| 성향 진단 + 분기 | 3 | `/fit` | 고용24 4축 규칙 점수(게이팅 아님) |
| 업종 후보 카드 | 4 | `/candidates` | **킬러** · 근거·위험·지원 3요소 병기 |
| 상권·리스크 | 5 | `/market/{id}` | 공공데이터 수치 + 출처 병기 |
| 준비 로드맵 | 6 | `/roadmap/{id}` | 체크리스트 + 지원사업 규칙 매칭 |
| 전문가 핸드오프 | 7 | `/handoff` | 인쇄 리포트 + 상담 예약 |

## 설계 원칙 (RULE.md·계획서 반영)

- **결정론 vs 언어계층 분리**: 적합도 4축(`domain/fit`)·후보 필터/랭킹(`domain/business_filter`)은
  순수 함수(결정론). LLM 은 핸드오프 요약 문장 등 **언어 계층**에만. 판정은 규칙, 서사는 LLM.
- **AI 관여 상한(Level 4 금지)**: **수익 예측을 하지 않는다**(`market_usecase.no_revenue_forecast`).
  "월 얼마 법니다"는 반환하지 않고 판단에 필요한 사실·출처만 제공.
- **장밋빛 카드 금지**: 모든 후보 카드에 위험 요인 필수 병기.
- **출처 병기(§1)**: 모든 수치는 `seed`(예시) 표기 + 출처 필드. 실서비스는 소진공 상가정보·국세통계·
  기업마당 API 로 대체. 응답 봉투 `{ok,data,meta,error}`, `meta.source ∈ {live, seed, rule, fallback}`.

## 구조 (클린 아키텍처)

```
dasi-startup/
  backend/app/
    domain/          fit(적합도 4축)·business_filter(후보 필터/랭킹)·slots (순수 함수, 결정론)
    application/     fit·candidates·market·roadmap·handoff·onboarding usecase
    infrastructure/  data(business·programs seed)·llm(폴백)·rag·stt·store(memory)
    interfaces/http/ 라우터 + {ok,data,meta,error} 봉투
  frontend/          의존성 없는 정적 SPA (START+7STEP, 목업 디자인, 글자크기 접근성)
  tests/             domain 결정론 단위 테스트
```
> venv·requirements·llm/rag/stt 인프라는 `../dasi-chulgeun` 과 동일(공유). 도메인·데이터·라우터·프론트만 창업용으로 교체.

## API 요약

| 메서드 | 경로 | 설명 | source |
|---|---|---|---|
| GET | `/health` | 상태 + 소스 표기 | live |
| POST | `/onboarding` | 대화 온보딩 → 프로필 | live/fallback |
| POST | `/fit` | 4축 점수 → 재취업/창업 성향 | rule |
| POST | `/candidates` | 경력·제약 → 업종 후보(근거·위험·지원) | seed |
| GET | `/market/{id}` | 후보 상권·리스크 + 출처(수익예측 미제공) | seed |
| GET | `/roadmap/{id}` | 준비 체크리스트 + 지원사업 매칭 | seed |
| POST | `/handoff` | 전문가 핸드오프 리포트 | live/fallback |
| POST | `/stt` | 음성 전사 + 슬롯(공통) | local |

## 테스트

```bash
cd backend && ../../dasi-chulgeun/.venv/Scripts/python -m pytest -q   # 5 passed
```
적합도 4축·후보 필터(제약 제외/랭킹)가 상수 하드코딩이 아님을 단위로 검증.
