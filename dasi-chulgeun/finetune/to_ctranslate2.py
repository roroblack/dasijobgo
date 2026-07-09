# -*- coding: utf-8 -*-
"""to_ctranslate2 — [SCAFFOLD·미검증] LoRA 어댑터 병합 → CTranslate2 변환(faster-whisper 백엔드용).

⚠️ GPU/데이터 없어 미검증. 학습 산출(LoRA 어댑터)을 우리 백엔드(whisper_stt.py, faster-whisper=CT2)에
   그대로 꽂기 위한 마지막 단계. Colab 또는 로컬(CPU도 변환은 가능)에서 실행.

흐름:  base + LoRA어댑터  →(병합)→  일반 HF 모델  →(ct2 변환·int8)→  faster-whisper 로드 가능 디렉토리
Colab 선행:  pip install -q ctranslate2 transformers peft
백엔드 반영:  STT_MODEL=/path/to/ct2_out  (config.py 는 이미 env 우선) → 서버 재시작 → eval_cer 재측정
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def merge(base: str, adapter: str, merged_dir: str):
    from peft import PeftModel
    from transformers import WhisperForConditionalGeneration, WhisperProcessor
    model = WhisperForConditionalGeneration.from_pretrained(base)
    model = PeftModel.from_pretrained(model, adapter)
    model = model.merge_and_unload()          # LoRA 가중치를 base에 흡수
    Path(merged_dir).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(merged_dir)
    WhisperProcessor.from_pretrained(adapter).save_pretrained(merged_dir)
    print(f"[merge] 병합 모델 저장: {merged_dir}")


def to_ct2(merged_dir: str, ct2_dir: str):
    # ct2-transformers-converter CLI (ctranslate2 패키지 제공)
    cmd = ["ct2-transformers-converter", "--model", merged_dir,
           "--output_dir", ct2_dir, "--quantization", "int8", "--force"]
    subprocess.run(cmd, check=True)
    print(f"[ct2] 변환 완료: {ct2_dir}  → STT_MODEL 로 지정")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="openai/whisper-medium")
    ap.add_argument("--adapter", default="whisper-medium-ko-senior-lora")
    ap.add_argument("--merged", default="_merged")
    ap.add_argument("--ct2", default="whisper-medium-ko-senior-ct2")
    a = ap.parse_args()
    merge(a.base, a.adapter, a.merged)
    to_ct2(a.merged, a.ct2)
