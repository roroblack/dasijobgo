# 기술 스택 재검토·업데이트 (2026-07-06 기준)

> _작성 시각: 2026-07-06 15:19 (로컬 기준)_

> 대상: `init_plans/다시출근_3대기능축_구현계획.md`(및 .html) 3-1 축별 기술 스택
> 방법: 2026-07 현재 웹 검색으로 각 계층 최신 상태 확인(RULE §1 — 외부 API·모델은 기억이 아니라 검색 근거).
> 주의: 검색은 영어권 소스 중심. **한국어 실품질(WER·자연스러움)은 데모 전 샘플 검증 필수** — 아래는 "현재 후보"이지 실측 결과가 아님.

---

## 0. 먼저 — 스택 무관 설계 이슈 3건 (이전 검토서 유지)

1. **SHAP 제거** — 매칭이 결정론 규칙(가중합)이면 SHAP(ML 설명 도구)은 부적합. 가중치 기여도 표시로 대체. ML 랭커로 갈 때만 SHAP.
2. **WebRTC → MediaRecorder** — 아바타가 사전 렌더 클립이면 실시간 P2P 불필요. `getUserMedia + MediaRecorder`로 녹화면 충분.
3. **Rhubarb 재검토** — 아래 PART 2에서 최신 대안으로 교체 권장.

---

## 1. PART 1 · 진입·서류

| 항목 | 기존 계획 | 2026-07 최신 권장 | 판정 |
|---|---|---|---|
| Frontend | React·TS·반응형 | 유지 (React 19 안정) | ✅ 유지 |
| STT | Web Speech API / 로컬 Whisper | 데모=Web Speech API 유지. 서버 정확도면 **Whisper Large v3 Turbo**(6× 빠름·809M) 또는 한국어 정확도 우선 **Voxtral Transcribe 2**(FLEURS WER 5.9% vs Whisper 7.4%·실시간 스트리밍), CJK 특화 **SenseVoice** | 🔄 업데이트 |
| 이력서 생성 LLM | 로컬 Qwen 2.5 | **Qwen3 계열** 또는 한국어 특화 **EXAONE 4.0(32B, LG)**. 경량~중형이면 충분, API 폴백 유지 | 🔄 버전업 |
| 추천 근거 | SHAP | **제거** → 규칙 가중치 기여도 | ❗ 교체 |
| External | 고용24 data.go.kr 4종·국세청 진위확인 | 유지 (실존 확인·활용신청 필요) | ✅ 유지 |

## 2. PART 2 · 가상 면접 (변화 가장 큼)

| 항목 | 기존 계획 | 2026-07 최신 권장 | 판정 |
|---|---|---|---|
| 녹화 | WebRTC/MediaRecorder | **MediaRecorder + getUserMedia** (WebRTC 제거) | 🔄 축소 |
| 아바타 립싱크 | Rhubarb viseme + Three.js/Lottie 입모양 스위칭 | **오디오→립싱크 영상 모델로 교체.** 사전 렌더=**Wav2Lip**(정확·경량) 또는 **MuseTalk**(latent diffusion·near-photorealistic·실시간 가능). 실시간 대화형=**OpenTalking**(셀프호스팅)·InfiniteTalk. 오디오 기반이라 **한국어 언어 독립** — Rhubarb의 한국어 부정확 문제 해소 | ❗ 교체 |
| TTS | Fish Speech / SBV2(VITS) | **Fish Audio S2**(80+ 언어·클로닝) 또는 **Qwen3-TTS**(2026.1·10언어·3초 클로닝). 경량/저지연=**CosyVoice2-0.5B**(한국어·150ms 스트리밍) 또는 **Kokoro-82M**(초경량). **SBV2는 일본어 중심 → 이들이 한국어에 유리** | 🔄 교체 권장 |
| 꼬리질문 LLM | 경량 Qwen/EXAONE | Qwen3/EXAONE 4.0 유지, API 폴백 | ✅ 버전업 |
| 아바타 API 대안 | HeyGen | 유지 가능. 대안: Synthesia·Hedra 등 | ✅ 유지 |
| 일정 | Google Calendar/Meet | 유지 (Meet 링크는 Calendar conferenceData·Workspace 스코프 확인) | ✅ 유지 |

**핵심**: 기존 "Rhubarb+viseme+2D 스위칭"은 2020년대 초 방식. 2026엔 오디오→토킹헤드(Wav2Lip/MuseTalk/LatentSync)로 오디오만 넣으면 립싱크 영상이 나오고, **언어 독립이라 한국어 문제도 사라짐.** 질문이 사전 고정이므로 배치 렌더면 충분.

## 3. PART 3 · 성장 루프

| 항목 | 기존 계획 | 2026-07 최신 권장 | 판정 |
|---|---|---|---|
| 근거 추출 인코더 | 로컬 KoBERT(2019) | **Kanana-Nano-2.1B-Embedding / Qwen3-Embedding-0.6B / BGE-M3** (아래 §6.3 상세, Korean-MTEB 기준 한국어는 Kanana가 이 셋 중 선두) | ❗ 교체 |
| 경량 LLM | 경량 로컬 LLM·API 폴백 | Qwen3/EXAONE 4.0 | ✅ 버전업 |
| 역량 갭 | 수식 비교(규칙) | 유지 (LLM 아님 — 설계원칙 정합) | ✅ 유지 |
| External | 내일배움카드 훈련과정 API | 유지 (실존 확인) | ✅ 유지 |

## 4. 공통 인프라

- 로컬 LLM 서빙: **Ollama / vLLM** 유지. 2026 오픈소스 상위(DeepSeek V4·GLM-5.1·Kimi K2.6·Qwen3.5)는 대형이라 데모엔 과함 — 경량~중형(EXAONE 4.0 32B·Qwen3 중형)이 현실적.
- PostgreSQL·SQLAlchemy·Docker·object storage(녹화) 유지.

## 5. 한 줄 요약

- **교체(❗)**: SHAP 제거 · Rhubarb→Wav2Lip/MuseTalk · KoBERT→BGE-M3
- **버전/모델 갱신(🔄)**: Qwen2.5→Qwen3/EXAONE4.0 · SBV2→Fish Audio S2/Qwen3-TTS/CosyVoice2 · WebRTC→MediaRecorder · Whisper→v3 Turbo/Voxtral
- **유지(✅)**: React·TS·FastAPI·Pydantic·공공 API 3종·Google Calendar·역량 갭 규칙

## 6. LLM·임베딩 모델 후보 (2026-07 추가 갱신)

우리 태스크(이력서 문장·꼬리질문·피드백 요약)는 **짧고 정형**이라 경량 4~8B로 충분. 임베딩은 별도 경량 모델.

### 6.1 오프라인(로컬) 생성 LLM
- **Gemma 4 E4B** (Google, 2026-04 · 유효 4.5B/임베딩 포함 8B · 128K · 멀티모달 · 엣지/모바일 타깃 · LiteRT 온디바이스) — "가벼운 거로 구동" 취지에 정확히 부합. 다국어(140+)지만 한국어 미세 뉘앙스는 국산 특화가 유리할 수 있음.
- **Qwen3 4B/8B** — 2026 로컬 종합 상위 평가, 한국어 포함. 8GB램 Q4로 구동.
- **EXAONE 4.0(LG) / Kanana(Kakao)** — 한국어 특화 경량.
- 권장: 하드웨어 빠듯 → **Gemma 4 E4B 또는 Qwen3 4B**, 한국어 품질 우선 → **EXAONE/Kanana 경량** + 품질 민감 텍스트만 API 폴백.

### 6.2 API 생성 LLM (고품질/폴백 경로)
- 해외: **Claude Haiku 4.5**(저비용·빠름) 또는 **Sonnet 5**(품질), **GPT-5 계열**, 최상위 **Opus 4.8**. ※ "Sonnet 4.5·Claude 4.6"은 현재 라인업 명칭 아님 — 현행은 **Sonnet 5 / Haiku 4.5 / Opus 4.8 / Fable 5**.
- **국산 API (권장)**:
  - **Upstage Solar Pro 2** ⭐ — Artificial Analysis 프론티어로 인정된 **유일 국산**(31B)·비용효율·한국인 대상 성능. 국산 API 1순위.
  - **Naver HyperCLOVA X** (CLOVA Studio / 네이버클라우드) — Think(추론)/Dash(경량)/Seed(무료 오픈). 기업·한국어 최적.
  - LG EXAONE·SKT A.X·NC Varco도 후보.

### 6.3 임베딩 — 근거 추출(PART 3, KoBERT 대체) · Korean-MTEB 2026 순위
- **Kanana-Nano-2.1B-Embedding**(kakaocorp) — Korean-MTEB **6위**, 2.1B로 Llama3.2 3B·Qwen2.5 3B를 한국어에서 상회. **한국어 우선이면 1순위.**
- **Qwen3-Embedding-0.6B** — 10위, 초경량·다국어·instruction-aware·가변 차원.
- **BGE-M3** — 11위지만 **dense+sparse+multi-vector 단일 아키텍처 + 8K 컨텍스트**로 긴 정책문서·하이브리드 검색 강점. 범용 기본값으로 유지 가치.
- 권장: 한국어 정확도=**Kanana-Nano** / 초경량=**Qwen3-Emb-0.6B** / 긴 문서·하이브리드=**BGE-M3**. 셋 다 셀프호스팅.

## 출처 (2026-07 검색)
- 오픈소스 LLM 2026: benchlm.ai, huggingface blog (EXAONE 4.0 32B·Qwen3.5·DeepSeek V4)
- TTS 2026: neosophie.com, siliconflow (Qwen3-TTS·Fish Audio S2·CosyVoice2·Kokoro·Chatterbox)
- 립싱크/아바타 2026: pixazo.ai, atlascloud.ai, lipsync.com (MuseTalk·Wav2Lip·LatentSync·OpenTalking)
- STT 2026: northflank, weesperneonflow (Whisper v3 Turbo·Voxtral Transcribe 2·SenseVoice)
- 임베딩 2026 / Korean-MTEB: huggingface(Qwen3-Embedding-0.6B·kanana-nano-2.1b-embedding), OnAnd0n/ko-embedding-leaderboard, bentoml (BGE-M3)
- Gemma 4 E4B: huggingface(google/gemma-4-E4B·litert-lm), llm-stats.com, lmstudio.ai
- 국산 LLM/API 2026: marktechpost, koreaherald, clova.ai(HyperCLOVA X), Upstage Solar Pro 2, benchlm.ai(Korean LLM leaderboard)
- Claude 현행 라인업: 세션 시스템 정보 (Sonnet 5·Haiku 4.5·Opus 4.8·Fable 5)
- 공공 API: data.go.kr (워크넷 채용정보 3038225·국세청 진위확인 15081808·내일배움카드 훈련과정 15109032)
