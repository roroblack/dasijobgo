# 작업 이력 (HISTORY.md)

> 프로젝트: **다시,출근** — 중장년 재취업 실행 에이전트 (해커톤 프로토타입)
> 규칙: [RULE.md](RULE.md) · 원본 기획/리서치: [init_plans/](init_plans/)

각 항목은 `날짜 · 분야 · 내용` 형식. 최신이 위.

---

## 2026-07-08 (창업 지원 트랙 새 프로젝트 — dasi-startup/)

- **요청** · dasi-chulgeun 복사 → 첨부한 창업 트랙 목업·계획서(init_plans/startup/) 참고해 새 프로젝트 생성.
- **복사·공유** · robocopy로 `dasi-startup/` 생성(.venv·__pycache__·experiments·finetune 제외). venv·requirements·llm/rag/stt/store 인프라는 dasi-chulgeun 공유(포트 8091, launch.json에 dasi-startup-backend 추가).
- **백엔드(동일 아키텍처, 창업 도메인 교체)** · 재취업 전용(matching/resume/schedule/interview + 관련 domain/data) 제거. 신규 결정론 domain: `fit`(고용24 4축 규칙 점수 → 재취업/창업 성향, 게이팅 아님)·`business_filter`(자본·점포·신체·경력적합·폐업률 규칙 필터/랭킹). 신규 seed data: `business_repository`(업종 후보 5종·근거/위험/지원/상권통계/출처)·`programs_repository`(지원사업). usecase 5종(fit/candidates/market/roadmap/handoff)·라우터 5종. **수익 예측 미제공(Level 4 금지)**·후보 위험 병기·출처 병기 준수. 슬롯/온보딩/stt 공통 재사용. **pytest 5 passed**.
- **프론트(목업 디자인 + START+7 STEP)** · 새 SPA(index/app.js/styles.css). Pretendard+Gowun Batang, 따뜻한 베이지·틸·살구 팔레트, 폰앱 셸. 8화면(시작→경력온보딩→창업슬롯→성향진단/분기→업종후보→상권리스크→준비로드맵→전문가핸드오프). 온보딩 마이크·TTS 재사용, 적합도 바·후보카드(근거/위험/지원)·상권지표+출처·체크리스트+지원사업·인쇄리포트+경계선배너.
- **검증** · 서버 8091 기동, /health·정적 정상. 브라우저에서 **8단계 전 흐름 end-to-end 완주(에러 0)**: fit 70/45%·후보 4장(품질검사 대행업 등, 위험·수익예측금지 표기)·상권(147곳/2곳낮음/62%보통+출처)·로드맵(체크3+지원사업2)·핸드오프(리포트+배너). 스크린샷은 외부 폰트 CDN 차단으로 타임아웃(기능 무관, DOM 검증으로 대체).
- **산출** · `dasi-startup/`(backend+frontend+README+run scripts). 재취업 트랙(8090)과 동시 구동.

## 2026-07-07 (데모 STT 정확도 개선 리서치 — reports/demo-stt-accuracy-boost)

- **질문** · 파인튜닝은 미래 트랙 → "지금 데모" 정확도를 올리는 최선(모델 교체 포함)을 오늘자 웹 리서치로.
- **핵심 발견** · 리턴제로 한국어 벤치(CER%): 리턴제로 자체 5.91(상담 3.51)·CLOVA 7.52·**OpenAI Whisper 11.39(=우리 large-v3)**·Google 11.50. 즉 Whisper가 한국어에 약함, 국산 엔진이 절반. 수치는 테스트셋 종속(낭독 5.6 vs 자유발화·저음질 11~17) — 중장년 즉흥+마이크는 어려운 끝.
- **권고(리포트)** · ①**리턴제로 API**(정확도 2배·가입 무료 10h·간투어 자동제거+키워드부스팅=우리 슬롯추출과 시너지·스트리밍·국내서버=PII 유리·온프렘 옵션) = 데모 즉효 1순위. ②오프라인/무비용 필수면 **한국어 파인튜닝 Whisper 드롭인**(ghost613 등 → CT2 변환 → STT_MODEL 교체, 온디바이스). ③무료 레버(hotwords·VAD 완화) 항상 병행. SenseVoice는 짧은/조용한 오디오 중국어 오출력 결함으로 제외. OpenAI/ElevenLabs/Deepgram은 미국 서버라 PII 유의.
- **산출** · `reports/demo-stt-accuracy-boost-2026-07-07_1231.html`(벤치표·전면비교·우선순위·PII·실행안·출처). 실측 최종검증은 55+ 데이터로(finetune/eval_cer.py 재사용).

## 2026-07-07 (중장년 특화 STT 파인튜닝 파이프라인 — finetune/)

- **동기** · 공개 STT 벤치(리턴제로 CER 8%)는 일반 성인 기준 → 55+ 중장년 발화 오류율은 미지수. AI-Hub 71592 연령필터 데이터로 직접 측정+파인튜닝하자는 결정.
- **전제 확인(중요)** · 워크스페이스에 해당 데이터 **없음**(오디오는 stt_test.wav 1개뿐), GPU 없음. → 데이터는 사용자 AI-Hub 계정으로 다운로드해야(병목), 학습은 무료 Colab T4. 당장 데모 우회는 안 함(사용자 선택: 파인튜닝 대기).
- **`finetune/` 신설** · ①`kspon_normalize.py`(전사표기 정규화·간투어옵션, ✅로컬검증) ②`eval_cer.py`(연령버킷별 CER 하네스, ✅실오디오 end-to-end 동작—large-v3로 stt_test CER 집계) ③`prepare_data.py`(71592→연령필터 manifest, ⚠️SCAFFOLD·파싱로직만 검증) ④`train_lora.py`(Colab T4 PEFT LoRA medium, ⚠️SCAFFOLD) ⑤`to_ctranslate2.py`(어댑터 병합→CT2, ⚠️SCAFFOLD) ⑥`README.md`(크리티컬패스·AI-Hub 다운로드 절차·기대치·리스크).
- **정직 고지** · ✅=로컬 실행 통과, ⚠️=데이터·GPU 부재로 미실행(골격만). 측정 하네스가 파인튜닝 전/후 공용 → "8%→X%" 슬라이드의 도구. 도메인 미스매치(Kspon 녹음≠제품 마이크)·무료 Colab 한계·RTZR 커스텀 대안 비교를 README에 명시.

## 2026-07-07 (STT 정확도 개선 + 상담사 파트별 안내 UX 원복)

- **증상** · turbo 실마이크 전사가 환각·반복("엔딩했을 때 엔딩했을 때…")으로 무용. 지원서도 안 채워짐(전사 쓰레기→슬롯 0).
- **근본원인 3** · ① VAD가 발화 시작음(첫 음절) 앞잘림 → Whisper 환각 유발 ② turbo는 디코더 축소로 한국어 반복환각 잦음 ③ 반복비율/도메인프롬프트 가드 부재.
- **UX 원복(사용자 요구)** · 연속 VAD 자동채움 → **예전 스타일**: 눌러 녹음 → 다 말하고 종료 → 전사 → 현재 파트 채움 → **AI 상담사가 다음 파트를 음성(speak)으로 안내**. `micToggle`+`matchChip` 복구, `S._spokenStep` 가드로 파트당 1회 낭독. 앞잘림 제거가 정확도도 개선.
- **모델·디코딩** · 기본 `large-v3`(turbo→large-v3, 반복환각 최소). `compression_ratio_threshold=2.4`(반복 세그먼트 재디코딩)+`temperature` 폴백+한국어 `initial_prompt`+`log_prob_threshold`. 속도 우선 시 `STT_MODEL=medium`.
- **검증** · 서버 /stt(large-v3): 텍스트·슬롯 정확, 첫 요청 27.4s(캐시로드 포함)·이후 ~15-18s(CPU). 프론트: 마이크 토글 배선·전사 시뮬(품질관리)→매칭→33% 채움→연차 파트 자동 진행·음성 안내. 콘솔 에러 0. (실마이크 환각 개선폭은 실기기 확인 필요.)
- **트레이드오프** · large-v3는 정확하나 CPU라 발화당 ~15-18s. 느리면 medium(≈2배 빠름), RAM 빠듯하면 small.

## 2026-07-07 (실시간 음성 온보딩 — VAD 발화단위 + 하이브리드 슬롯)

- **RAM 확보** · 요청대로 워킹셋 트리밍(`EmptyWorkingSet`, 앱 종료 없이 페이지아웃) + 사용자가 VS Code 종료 → 가용 RAM 1.7GB→**6.56GB**(small STT + 2B LLM 동시 여유).
- **백엔드(하이브리드 규칙 층)** · `domain/slots.py`(이미 존재, 세션 초반 산출) = 전사 텍스트 → 핵심 슬롯(jobKind·skills·years·region·certs)만 규칙 추출, 잡담은 사전에 없으면 버림. `/stt`가 `{text, slots}` 반환. 단위테스트 추가 → `pytest 12/12`.
- **프론트(VAD 발화단위)** · 온보딩 마이크 = 연속 청취. Web Audio `AnalyserNode`로 RMS 측정, **말 멈춤(침묵 800ms) = 발화 끝** → 그 문장만 `MediaRecorder`로 잘라 `/stt` 전송(webm 헤더 온전). 받은 슬롯을 `applyVoice`가 프로필+실시간 지원서(ctx)에 반영, 3핵심(직무·연수·지역) 다 채우면 자동 진행. 무마이크 폴백.
- **검증** · 라이브 `/stt`: text+slots(`jobKind 품질관리·검사·years 25`). 프리뷰(무마이크): VAD 함수 로드·마이크 폴백·`applyVoice` 시뮬레이션 → 지원서 100%→완성 화면 자동 진행. **콘솔 에러 0**. (실마이크 발화 캡처는 실기기 필요.)
- **STT 모델 상향** · small 인식률 부족(사용자 피드백) → 기본 **large-v3-turbo**(정확도 large급/속도 6배, ~1.5GB, RAM 여유에 들어감). 라이브 `/stt` 검증: 텍스트·슬롯 정확, 첫 요청 15.8s(캐시 로드 포함)·이후 발화당 ~10-12s(CPU). 느리면 `STT_MODEL=medium`, RAM 빠듯하면 small/base로 낮춤(env 한 줄).
- **잔여** · 하이브리드의 **LLM 정제 층**(발화 종료 후 로컬 LLM으로 슬롯 재정제)은 미착수 — 현재는 규칙 즉시 층만. 다음 후보.

## 2026-07-07 (STT 품질 수정 — base→small + VAD)

- **증상** · 실마이크 전사가 반복·환각("롯만들 롯만들…")으로 깨짐 → 원인=Whisper **base의 한국어 한계 + 그리디 디코딩**.
- **수정** · `STT_MODEL` 기본 base→**small**(한국어 정확도↑). `transcribe`에 **VAD(무음·잡음 제거)+beam_size=5+condition_on_previous_text=False+no_speech 필터**로 반복·환각 억제. 저신뢰 세그먼트(avg_logprob<-1.0·no_speech>0.6) 폐기.
- **부수 수정** · Windows HF 캐시 심볼릭 권한(WinError 1314)로 small 다운로드 실패 → `HF_HUB_DISABLE_SYMLINKS=1`(복사 모드). `onnxruntime`(VAD) 설치.
- **검증** · small 로드·전사 정상("…25년 했습니다"), `pytest 11/11`, 서버 재기동 후 **라이브 `/stt` HTTP ok·source=local**. (실마이크 잡음 대응은 small+VAD가 base보다 크게 개선. 여전히 부족하면 medium은 RAM 부담.)

## 2026-07-07 (STT 아키텍처 확인 + 현황 리포트)

- **확인** · STT 전사는 **서버측 faster-whisper**(프론트는 녹음·업로드만). 브라우저와 동일한 **webm/opus**를 서버로 보내 전사 성공("…품질 관리를 25년 했습니다") → "(안 들렸어요)"는 디코딩 버그가 아니라 **짧/무음 녹음** 시 빈 전사 폴백임을 실측 확인. 마이크 핸들러에 **짧음 가드**(blob<2.5KB → "너무 짧아요") 추가, `index.html` 스크립트 `?v=` 갱신.
- **리포트** · 대시보드형 HTML `reports/impl-status-2026-07-07_0932.html` 생성(①~⑤ 반영: NCS 근거추출·STT·TTS·마이크·웹캠 = 실제/부분, PART2 22→~48). 파일명에 시각 포함(규칙).

## 2026-07-07 (미구현 채우기 ②③ — STT(faster-whisper) + TTS(브라우저))

- **판정(RULE §1)** · Qwen3-TTS는 **로컬 CPU 실사용 불가**(최적화 Talker가 DashScope 클라우드 전용·transformers 경로는 너무 느림), Gemma4-오디오/Qwen3-ASR도 무GPU CPU엔 비현실 → 검색 확인 후 **되는 것**으로 구현: STT=faster-whisper, TTS=브라우저 speechSynthesis. 신경망 TTS·Qwen-ASR은 GPU/클라우드 스왑 자리로 명시.
- **② STT(백엔드·실모델)** · `infrastructure/stt/`(faster-whisper base, CPU/int8, 지연 싱글턴, env-gated) + `POST /stt`(오디오 업로드→전사). 검증: Windows SAPI(Heami)로 한국어 wav 생성 → 전사 *"안녕하세요. 저는 자동차 부품 공장에서 품질 관리를 25년 했습니다."*(원문 일치, 이십오년→25년). TestClient HTTP 200·source=local. `python-multipart`·`httpx` 추가. `pytest 11/11` 유지.
- **③ TTS(프론트·브라우저)** · STEP 8 아바타가 질문을 `speechSynthesis`(한국어 음성)로 발화. 무설치·무GPU.
- **④ 마이크 배선(프론트)** · STEP 1 온보딩 마이크 = 실동작 — `getUserMedia`+`MediaRecorder`로 녹음 → `/stt` 전사 → 전사 텍스트로 칩 자동 매칭(연수는 근접값). 장치 없으면 "마이크 못 씀" 폴백.
- **⑤ 웹캠 녹화(프론트)** · STEP 7 실제 카메라 미리보기+장치상태(getUserMedia), STEP 8 셀프뷰 라이브 영상 + `MediaRecorder` 답변 녹화(스트림 재사용). 장치 없으면 "장치 없음" 폴백 + 이모지 셀프뷰.
- **검증(브라우저)** · 캐시 이슈로 `index.html` 스크립트에 `?v=` 추가. 프리뷰(무장치) 실측: 마이크 버튼 배선됨·폴백 문구 표시, 프리뷰 카메라 "⚠️ 장치 없음" 폴백, 면접 셀프뷰 이모지 유지·녹화 미시작(정상)·**TTS 발화 동작**, **콘솔 에러 0**. 실장치 캡처는 실기기 필요(프리뷰엔 카메라·마이크 없음) — `/stt` 백엔드는 실오디오로 별도 검증됨.
- **대시보드** · `STT 음성 입력`→실제(faster-whisper), `웹캠 녹화`→**실제(MediaRecorder)**, `TTS·아바타·립싱크`→부분(브라우저 TTS·라이브 셀프뷰; 립싱크·신경망 TTS는 GPU 잔존).

## 2026-07-07 (미구현 채우기 ① — 역량 근거추출 NCS rubric)

- **백엔드**(결정론) · `domain/rubric.py` 신규 — 면접 답변 텍스트 → NCS 5축(직무전문성·문제해결·성과정량화·의사소통·리더십) **지표 밀도 기반 점수 + 근거 문장 추출**. 정량화 축은 숫자+단위(_QUANT) 있어야 고득점(없으면 '수치 부족' 신호). `interview_usecase.analyze_answer()` = rubric → competency 등급 → 최약축 → 훈련. 엔드포인트 `POST /interview/analyze-answer`(AnswerReq) 추가. 이전엔 프론트가 신호값을 하드코딩했으나 이제 **실제 답변에서 결정론적으로 산출**(RULE §3.3).
- **검증** · 단위 2건 추가 → `pytest 11/11`. 실측: 근거 풍부 답변(직무 82·문제해결 95·의사소통 43=최약축→커뮤니케이션 훈련) vs 빈약 답변(문제해결 15=최약축) 차등 산출. app import OK.
- **대시보드 반영** · `역량 근거추출(NCS rubric)` 미구현 → **실제(결정론)**. (규칙/키워드 루브릭 5축 — 학습형 NCS 분류기/KoBERT는 후순위 업그레이드.)

## 2026-07-06 (통합 — 로컬 LLM(Gemma-4-E4B) + RAG 백엔드 배선)

- **백엔드 통합** · 첨부 생성 모듈을 실제 백엔드에 배선. `llm/client.py`에 **로컬 GGUF(llama.cpp) 백엔드 추가**(우선순위 local→API→템플릿, 지연 싱글턴). `infrastructure/rag/` 신규(임베딩 코사인 검색 + **유사도 임계값**으로 오염 방지). `resume_usecase`가 RAG 예시를 "문체 참고(사실 베끼기 금지)"로 주입 + 응답에 `rag` 메타. `config.py`에 `LLM_GGUF_PATH·RAG_EMB_MODEL·RAG_MIN_SIM` env. 전부 **env-gated**(미설정/미설치 시 폴백, 데모 지속).
- **실동작 검증** · `integration_test.py full`로 실제 usecase 호출: **Gemma-4-E4B(GGUF) source=local · 54.1s**, RAG top-2(ex_qc 0.597) 주입, 자소서 **오염 0·25년 정확** 생성. RAG-only 경로(fast)도 확인. `pytest 9/9` 유지. (임베딩은 노트북 RAM 때문에 ko-sroberta, 실서버는 BGE-M3/Kanana-emb 권장.)
- **리포트** · 대시보드형 HTML 리포트 `reports/impl-status-llm-rag-2026-07-06_1810.html` 생성(구현 현황 시각화 — LLM 문장 생성·RAG 임베딩 검색이 seed→실제로 전환 반영) + visualize 위젯 인라인 렌더. 산출물 `output/integration_{rag,full}.json`.

## 2026-07-06 (문서 — 구현계획서 스택 갱신)

- **문서** · `init_plans/다시출근_3대기능축_구현계획서.html`의 기술 스택을 확정 결정으로 갱신(리포트 `reports/tech-stack-update-2026-07-06_1519.md`·bake-off 실측 반영): SHAP 제거(규칙 매칭) · Rhubarb→Wav2Lip/MuseTalk · KoBERT→Kanana-2.1B-emb/BGE-M3 · Qwen2.5→EXAONE-3.5-2.4B/Kanana/Gemma-4-E4B · SBV2→Fish Audio S2/CosyVoice2 · WebRTC→MediaRecorder · 공통 인프라에 llama.cpp·국산 API(Solar Pro 2/HyperCLOVA X) 추가 · "2026-07 실측" 문구(2B 4bit 무GPU 노트북 구동). 아키텍처 트리·PART2 파이프라인 문구도 동기화. (.md 원본은 미변경 — 요청 대상이 HTML)

## 2026-07-06 (실험 — 저용량 로컬 모델 bake-off)

- **실험** · 사용자 첨부 `files.zip`(생성 클라이언트: prompts/config/client/example_usage, 의도 모델 Gemma4 12B)을 이 노트북(무GPU·여유 RAM 2.7GB·디스크 12GB)에서 최소급 모델로 실동작 확인. `dasi-chulgeun/experiments/`에 러너·산출물, `reports/bakeoff-qwen05b-2026-07-06.md`에 리포트.
- **방법** · 12B 서빙 불가 → 첨부 `prompts.REGISTRY`+`config.GEN` 그대로 재사용하고 서빙만 로컬 transformers(`Qwen2.5-0.5B-Instruct`, 494M, bf16, CPU)로 대체. mock 6태스크 실행.
- **결과(1차·폐기)** · 편의로 구형 `Qwen2.5-0.5B`를 써서 품질 바닥(사용자 지적). 파이프라인만 확인됨.
- **재실행(정식)** · 논의한 한국어 특화 소형 모델로 재측정. 무GPU·여유 RAM 2GB라 **4bit GGUF + llama.cpp(CPU)**로 구동. `run_gguf_bakeoff.py`로 **Kanana-Nano-2.1B**(ch00n GGUF)·**EXAONE-3.5-2.4B**(lmstudio-community GGUF) 6태스크 비교. 리포트 `reports/bakeoff-korean-2b-2026-07-06.md`.
- **결과(2B)** · 둘 다 CPU ~6–9 tok/s로 노트북 실사용권, 자소서·꼬리질문·피드백 모두 정상 품질. 이번 1회 런에선 **EXAONE가 사실 충실도 근소 우위**(자소서 경력 25년 정확, Kanana는 few-shot의 22년/물류센터를 베낌). 공통 약점=few-shot 오염 → 첨부 RESUME_FEWSHOT 3~5개 확충이 선행 과제. temperature>0·mock 1건이라 확정 아님, 10건×blind 채점 필요.
- **확장(5-way + RAG)** · Qwen3.5-4B·Gemma-4-E4B(QAT) 추가 실행(4bit GGUF). 결과 전부 `output/*.md`, 종합 리포트 `reports/bakeoff-korean-2026-07-06_1711.md`(구 2건 리포트 대체·삭제). 품질 최상=**Gemma-E4B**(단 5.15GB·RAM 압박, n_batch=64로 구동)·차상 Qwen3.5-4B(느림), 가성비 최상=**EXAONE-2.4B**. Gemma는 262k 어휘 때문에 logits 버퍼 OOM→n_batch 축소로 해결.
- **RAG 실측** · `run_rag_bakeoff.py`로 임베딩 검색(BGE-M3 목표였으나 여유 RAM~3.4GB에서 OOM→소형 `ko-sroberta`로 대체)→resume_draft 주입, RAG 없음/있음 비교(EXAONE 고정). 검색은 정상(QC 예시 top1 cos0.769). **RAG가 핵심 QC 사실은 구체화했으나, 약한 2순위(물류 0.535)·근거불명 "무재해 3년"이 새로 유입 → 오염원만 이동, 완전해결 아님.** 교훈: 유사도 임계값·top-1·"톤 전용" 주입 설계 필요. 실하드웨어선 BGE-M3/Kanana-emb 권장.

## 2026-07-06 (개편 4차 — 반응형: 작은 화면 = 모바일 목업)

- **요청** · 작은 화면/모바일이 되면 자동으로 모바일 목업처럼 보이게(계획서 0-1 "PART 1·3 반응형 동시 대응").
- **프론트** · 820px 브레이크포인트로 **한 코드베이스 반응형** 구현. 넓은 화면=데스크탑(창 프레임+사이드바+맥락 패널), 좁은 화면=모바일 폰 앱: 창바·사이드바·masthead 숨김 → **모바일 앱바(뒤로+화면 제목+진행 N/12)** + 진행바 표시, `.app` 1열, 맞춤 안내/실시간 지원서(ctx)는 본문 아래로 쌓아 노출(모바일 목업의 body 내 배치 재현), 그리드(benefit/match/two-col/interview) 1열, CTA 전폭. 앱바 제목·진행은 `renderChrome`에서 화면별 세팅, 모바일 뒤로가기 `#mback`=데스크탑과 동일 history 스택.
- **검증** · 375px(모바일): 창바·사이드바·masthead 숨김·앱바 표시, 제목/진행 화면별 갱신(내 이야기 2/12 → 나에게 맞는 일자리 4/12), ctx가 본문 아래 스택, match 그리드 1열, 모바일 뒤로가기 동작. 1280px(데스크탑): 창바·사이드바·masthead 복귀. **콘솔 에러 0**.

## 2026-07-06 (개편 3차 — 데스크탑 PC 목업 GUI 재현)

- **분석** · 사용자가 데스크탑 목업 `init_plans/중장년_재취업_실행에이전트_화면흐름_목업_PC.html` 추가 제공. "목업 GUI 그대로 나오게" 요청 → 프론트를 폰 프레임에서 **데스크탑 웹 레이아웃**으로 전면 재구성.
- **프론트**(3파일 재작성) · PC 목업 CSS·컴포넌트를 그대로 이식: **브라우저 창 프레임(win-bar+주소창) + 좌측 사이드바 내비 + 넓은 메인 + 우측 맥락 패널(with-ctx)**. 화면별 컴포넌트도 목업대로 — benefit-grid(2열)·match-grid(2열)·resume-doc·interview 분할(stage+qpanel+qlist)·two-col 피드백·sched slotgrid·reco. 주소창은 화면별 경로(`dasi-chulgeun.kr/onboarding` 등), 사이드바 내비는 화면별 활성 항목·🎥녹화중 표시. 기본 17px(15/17/20 토글). 인터랙션용으로 창 프레임에 뒤로가기(history 스택)만 추가.
- **동일 유지** · 백엔드 무변경. 12스텝 인터랙티브 플로우·결정론/LLM 경계·seed 라벨 그대로. 온보딩은 목업 채팅+실시간 지원서(우측 ctx) 형태로, 입력은 선택 칩.
- **참고** · PC 목업이 접은 STEP 1.5(이력서 확인)·STEP 7(장치 테스트)은 플로우 완결성 위해 **데스크탑 디자인 언어로 유지**(목업엔 없는 화면).
- **검증** · 서버 재기동(index 200, title=데스크탑). 브라우저 DOM 주행으로 시작→온보딩(ctx 100%)→확인→매칭(4카드)→장바구니→맞춤이력서(ctx 4종)→제출→면접준비→아바타 면접(Q1~5 진행)→피드백(2패널·3바·대기 2건)→일정(월11시 확정)→교육(최약축 성과정량화→훈련)→재지원 루프 + 뒤로가기 전 구간 동작, **콘솔 에러 0**. (스크린샷 캡처 툴은 간헐 타임아웃 — 앱은 정상)

## 2026-07-05 (개편 2차 — 목업 개편본 반영)

- **구조** · 코드 폴더명을 한글 `프로그램/` → 영문 **`dasi-chulgeun/`** 으로 변경(사용자 요청: 파일·폴더명에 한글 금지). `.claude/launch.json`·런처·README·plans 경로 참조 동기화. `.venv` 는 재생성 없이 직접 python.exe 호출로 동작 확인(activate 스크립트 내부 경로만 구경로로 남으나 미사용 경로).
- **계획** · `dasi-chulgeun/plans/2026-07-05-flow-revamp.md` 작성(목표·영향 파일·결정론/LLM 경계·단계·검증).
- **분석** · 갱신된 목업(`init_plans/*_화면흐름_목업.html`, 개편본)과 `다시출근_3대기능축_구현계획.md`, 직전 대화 피드백을 반영해 플로우를 재구성. 핵심: **STEP 8 = AI 아바타 면접**(Q1~5 순차 재생), **STEP 6(실면접 일정)을 STEP 9 이후로 이동**, 고용24 = **링크 직접 제출**(승인 대기 아님).
- **백엔드**(add-only) · `POST /interview/questions` 신규 — 회사 정보 기반 면접 질문 Q1~5 생성. Q1~3 규칙 조립(결정론), **Q4~5 는 LLM 꼬리질문(언어계층)→키 없으면 템플릿 폴백**(RULE §3.3). `interview_usecase.generate_questions()` + `QuestionsReq` 스키마. 없는 job_id → 404.
- **프론트** · 3파일 재작성. 정수 STEP → **문자열 키 12화면 시퀀스**(시작→1→1.5→2→3→4→5→7→8→9→6→10). 신규 화면: 시작(정부지원 3종)·STEP 1.5(중간 이력서 확인)·STEP 7(카메라·소리+AI면접준비)·STEP 8(아바타 면접)·STEP 9(연습 피드백+결과 대기)·STEP 10(교육 추천 루프). STEP 1 에 이력서 업로드 옵션+실시간 미리보기, STEP 3 하단 통합 이력서 확인+저장/프린트, STEP 5 회원사/고용24 분기.
- **접근성** · 글자 크기 조절 툴바(가-/가/가+ = 16/18/21px, **기본 18px**). 폰 내부 rem 기반이라 토글이 전체 확대(중장년 가독성, 계획서 0-2 반영).
- **RULE §1 준수** · 아바타·음질(연습 피드백)·합불·정부지원 금액 등 실측 없는 데모값은 화면에 **`seed` 배지**로 표기. 매칭 점수·일정 교집합·역량 등급만 백엔드 결정론(live) 표기.
- **검증** · `pytest` 9/9 유지. `urllib`(UTF-8)로 신규 `/interview/questions`(질문 5개·Q4~5 폴백·404) + 매칭(한빛정밀 100%)·일정(교집합 최이른 확정)·분석(최약축→훈련) 실측. 브라우저로 **12화면 전 구간 자동 주행 + 루프백**(콘솔 에러 0), 글자크기 토글(18→21→18) 동작 확인. STEP 6 교집합 없을 때 가짜 확정 안 만들고 정직하게 재선택 유도(RULE §3.2) 확인.

## 2026-07-05

- **구조** · 프로젝트 루트 초기화. `init_plans/`(기존 기획·리서치 자료 이동), `dasi-chulgeun/`(코드; 최초 `프로그램/`으로 만들었다가 이후 영문명으로 변경), `reports/`(버그·작업 리포트), `release/`(릴리스 패키지) 생성.
- **문서** · `RULE.md` 작성 — §1 할루시네이션 방지, §2 AI 하네스 룰, §3 하드코딩·폴백 최소화, §4 응답 봉투, §5 이력관리. (`SKN32-2nd_GAJIMA_Dev/RULE.md` §1·§3 계승·보강)
- **문서** · `HISTORY.md` 작성(본 파일).
- **분석** · 기존 자료에서 제품 정의 확정: 10단계 실행 루프(대화 온보딩 → 실시간 매칭 → 장바구니 → 회사별 맞춤 이력서 → 확인 후 제출 → 면접 일정 자동확정 → 전날 준비·모의면접 → 화상 면접 → 피드백·역량 갭 → 재지원). 기술 실현성: data.go.kr 대체경로, 결정론적 일정로직 + LLM 언어계층, 화상 API 폴백. (근거: `init_plans/*_팀공유브리핑.html`, `*_화면흐름_목업.html`)
- **결정** · 기술 스택은 참조 프로젝트 `SKN32-2nd_GAJIMA_Dev` 를 따라 **클린 아키텍처 FastAPI 백엔드 + 의존성 없는 정적 프론트**. `{ok,data,meta,error}` 봉투, 미설정 시 seed/fallback 패턴.
- **백엔드** · FastAPI 클린 아키텍처 구현 — `domain/`(매칭·일정·역량갭 결정론 로직), `application/`(usecase), `infrastructure/`(seed 데이터·LLM 템플릿 폴백), `interfaces/http/`(라우터+envelope), `schemas/`.
- **프론트** · 목업 스타일 기반 10단계 인터랙티브 플로우 SPA. 백엔드 API 연동으로 루프 시연.
- **검증** · 런처(`run_all.ps1`/`.sh`) + README + `.claude/launch.json` 작성.
  - `pytest` 결정론 로직 **9/9 통과**(점수·교집합·등급이 상수 하드코딩 아님을 단위 검증).
  - uvicorn(:8090) 부팅, 6개 엔드포인트 UTF-8 실측(한빛정밀 적합도 100%, 최이른 슬롯 TUE_14 확정, 최약 역량→훈련 매핑 정확). 봉투/`meta.source` 정상.
  - 브라우저로 **10단계 플로우 전 구간 통과**(콘솔 에러 0). 온보딩→매칭→장바구니→이력서→제출→일정확정→준비→화상→피드백→재지원 루프 동작 확인.
  - RULE §1 준수: STEP10 재지원 문구를 실제 적합도 상승 여부에 따라 분기(이미 100%면 '유지'로 정직 표기).
- **주의** · PowerShell 5.1 `Invoke-RestMethod` 는 한글 바디를 cp949 로 깨뜨림 → API 실측은 stdlib urllib(UTF-8) 로 수행할 것(백엔드 결함 아님).
