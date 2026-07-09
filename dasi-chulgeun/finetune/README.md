# 중장년 특화 STT 파인튜닝 파이프라인

목적: 공개 STT 벤치(리턴제로 CER 8% 등)는 **일반 성인 발화** 기준 → **55+ 중장년 발화**에서의 실제 오류율을
직접 측정하고, 그 갭을 **Whisper LoRA 파인튜닝**으로 줄인다. (AI-Hub dataSetSn=71592 연령필터 데이터 사용)

## 크리티컬 패스(가장 긴 막대부터)
```
① [USER] AI-Hub 71592 승인·다운로드·압축해제        ← 지금 바로 시작(승인 대기+수십GB, 나는 대신 못 받음)
② [나]   prepare_data.py  → 연령필터 manifest(train/eval)
③ [나]   eval_cer.py      → 베이스라인 "일반 8% → 55+ X%" 실측(large-v3, medium)
④ [USER+나] train_lora.py → 무료 Colab T4에서 LoRA 학습(medium)
⑤ [나]   to_ctranslate2.py→ 병합+CT2 변환 → STT_MODEL 로 지정
⑥ [나]   eval_cer.py 재측정 → 파인튜닝 전/후 CER 비교(개선 증명)
```

## 파일 상태
| 파일 | 상태 | 비고 |
|---|---|---|
| `kspon_normalize.py` | ✅ 검증됨(로컬 자기검증 통과) | 전사표기 → 순수텍스트, 간투어 제거 옵션 |
| `eval_cer.py` | ✅ 검증됨(실오디오 end-to-end 동작) | 연령버킷별 CER, 파인튜닝 전/후 공용 하네스 |
| `prepare_data.py` | ⚠️ SCAFFOLD·미검증 | 실 71592 파일 레이아웃에 '확인 지점 ①②③' 맞출 것 |
| `train_lora.py` | ⚠️ SCAFFOLD·미검증 | Colab T4 전용(로컬 GPU 없음). PEFT LoRA medium |
| `to_ctranslate2.py` | ⚠️ SCAFFOLD·미검증 | 어댑터 병합 → faster-whisper용 CT2 |

> 정직 고지(RULE §1): ✅는 로컬에서 실제로 돌려 통과, ⚠️는 데이터·GPU 부재로 **아직 미실행**. 골격만 완성.

## ① 데이터 다운로드 (지금 사용자님이 할 일)
1. https://aihub.or.kr 로그인 → 데이터셋 검색 `71592` (또는 URL `?dataSetSn=71592`).
2. 활용 신청 → **승인 대기**(길면 하루 이상). 승인돼야 다운로드 버튼 활성.
3. AI-Hub 다운로더로 받고 압축 해제 → 루트 경로 확보(예: `D:/data/71592`).
4. **라벨 파일 하나를 열어** 전사·나이 필드의 실제 키 이름을 확인 → `prepare_data.py`의
   `_TEXT_KEYS/_AGE_KEYS`와 '확인 지점 ②③'(오디오 경로 규칙)만 맞추면 됨.

## ②③ 전처리 + 베이스라인 측정 (데이터 오면 로컬 CPU로 가능)
```bash
cd dasi-chulgeun
# 55+ 만 뽑아 평가셋, 45+ 전체를 학습셋(예시 — 실제는 train/eval 화자 겹치지 않게 분리)
.venv/Scripts/python.exe finetune/prepare_data.py --root D:/data/71592 --min-age 55 --out finetune/manifest_eval.jsonl
.venv/Scripts/python.exe finetune/prepare_data.py --root D:/data/71592 --min-age 45 --out finetune/manifest_train.jsonl
# 베이스라인 CER(현재 STT_MODEL=large-v3). medium도 STT_MODEL=medium 로 한 번 더.
.venv/Scripts/python.exe -m finetune.eval_cer --manifest finetune/manifest_eval.jsonl
```
→ 여기서 나오는 **55+ CER 숫자가 이 프로젝트의 핵심 슬라이드**("일반 8% vs 우리 타깃 X%").

## ④ Colab 학습 (무료 T4)
1. `manifest_*.jsonl` + 오디오를 Google Drive 업로드(또는 Colab에 zip 업로드).
2. Colab 새 노트북(런타임=T4 GPU):
   ```
   !pip install -q transformers datasets peft accelerate bitsandbytes jiwer soundfile librosa ctranslate2
   # train_lora.py 업로드 후
   !python train_lora.py --train manifest_train.jsonl --eval manifest_eval.jsonl --epochs 3
   ```
3. 무료 한계(세션 12h·불안정) → **1차는 서브셋(3~8천 발화)·2~3 epoch**. 개선 확인 후 스케일업.

## ⑤⑥ 변환 + 백엔드 반영 + 재측정
```bash
python finetune/to_ctranslate2.py --adapter whisper-medium-ko-senior-lora --ct2 whisper-medium-ko-senior-ct2
# 백엔드에 꽂기(config.py는 env 우선):
setx STT_MODEL "C:/.../whisper-medium-ko-senior-ct2"   # 또는 실행 셸에서 export
# 서버 재시작 후 동일 하네스로 재측정 → 전/후 비교
.venv/Scripts/python.exe -m finetune.eval_cer --manifest finetune/manifest_eval.jsonl
```

## 정직한 기대치 · 리스크
- **일정**: ①승인·다운로드(하루+) → ②③④⑤⑥(수일). **오늘의 데모 정확도는 이걸로 안 올라간다** —
  사용자님이 "당장 우회 없이 파인튜닝 대기"를 택했으므로, **데모 시점엔 large-v3 그대로**임을 인지할 것.
- **도메인 미스매치**: KsponSpeech 녹음조건 ≠ 우리 브라우저 webm/opus 마이크. eval셋은 가능한 한
  제품 유사 오디오를 섞어야 실제 개선이 측정됨(안 그러면 KsponSpeech에만 과적합).
- **무료 Colab**: 끊김·시간제한 → 큰 스케일은 유료 GPU 필요. 1차는 서브셋으로 '개선 신호'만 확인.
- **대안 비교**: ③ 측정 후 DIY 파인튜닝 vs **RTZR 도메인 커스텀/API**를 비용·CER로 나란히 비교 권장
  (RTZR는 키워드 부스팅·간투어 제거를 학습 없이 제공 → 노력 대비 나을 수 있음).
