# -*- coding: utf-8 -*-
"""train_lora — [SCAFFOLD·미검증] Whisper LoRA 파인튜닝(무료 Colab T4용). 중장년(45+/55+) 전사 특화.

⚠️ 로컬엔 GPU가 없어 실행·검증 못 함. Colab(T4)에서 돌린다. 아래는 HF Transformers + PEFT(LoRA)
   표준 레시피를 우리 manifest(prepare_data.py 출력)에 맞춘 것. 데이터가 오면 그대로 Colab에 올려 실행.

왜 medium+LoRA인가: T4(16GB)에서 large 풀파인튜닝은 빠듯 → 8bit+LoRA로 medium을 타깃(속도·정확도 균형).
   작은 모델일수록 어려운 발화에서 이득이 커, medium 특화가 large 일반본을 넘길 여지가 있다.

Colab 선행: pip install -q transformers datasets peft accelerate bitsandbytes jiwer soundfile librosa
무료 Colab 한계: 세션 12h·불안정 → 우선 '서브셋(예: 3~8천 발화)·2~3 epoch'로 1차 LoRA. 스케일은 이후.
"""
from __future__ import annotations

import argparse

BASE_MODEL = "openai/whisper-medium"   # 필요시 -small(더 가벼움) / -large-v3(유료 GPU)


def main(manifest_train: str, manifest_eval: str, out_dir: str, epochs: int, base: str):
    import torch
    from datasets import Audio, load_dataset
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (Seq2SeqTrainer, Seq2SeqTrainingArguments,
                              WhisperForConditionalGeneration, WhisperProcessor)

    processor = WhisperProcessor.from_pretrained(base, language="korean", task="transcribe")

    # manifest(JSONL {audio,ref,age}) → HF dataset, 16kHz 리샘플
    ds = load_dataset("json", data_files={"train": manifest_train, "eval": manifest_eval})
    ds = ds.cast_column("audio", Audio(sampling_rate=16000))

    def prep(batch):
        a = batch["audio"]
        batch["input_features"] = processor.feature_extractor(
            a["array"], sampling_rate=16000).input_features[0]
        batch["labels"] = processor.tokenizer(batch["ref"]).input_ids
        return batch
    ds = ds.map(prep, remove_columns=ds["train"].column_names, num_proc=1)

    # 8bit 로드 + LoRA(어텐션 q/v) — T4 메모리 절약
    model = WhisperForConditionalGeneration.from_pretrained(base, load_in_8bit=True, device_map="auto")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05, bias="none"))
    model.print_trainable_parameters()

    # Whisper 데이터 콜레이터(패딩) — 표준 구현
    import dataclasses

    @dataclasses.dataclass
    class Collator:
        proc: object

        def __call__(self, feats):
            inp = [{"input_features": f["input_features"]} for f in feats]
            batch = self.proc.feature_extractor.pad(inp, return_tensors="pt")
            labs = self.proc.tokenizer.pad([{"input_ids": f["labels"]} for f in feats], return_tensors="pt")
            lab = labs["input_ids"].masked_fill(labs.attention_mask.ne(1), -100)
            if (lab[:, 0] == self.proc.tokenizer.bos_token_id).all().cpu().item():
                lab = lab[:, 1:]
            batch["labels"] = lab
            return batch

    args = Seq2SeqTrainingArguments(
        output_dir=out_dir, per_device_train_batch_size=8, gradient_accumulation_steps=2,
        learning_rate=1e-3, warmup_steps=50, num_train_epochs=epochs, fp16=True,
        per_device_eval_batch_size=8, generation_max_length=225, logging_steps=25,
        save_strategy="epoch", eval_strategy="epoch", remove_unused_columns=False,
        label_names=["labels"], report_to=[])
    trainer = Seq2SeqTrainer(model=model, args=args, train_dataset=ds["train"],
                             eval_dataset=ds["eval"], data_collator=Collator(processor),
                             tokenizer=processor.feature_extractor)
    model.config.use_cache = False
    trainer.train()
    model.save_pretrained(out_dir)         # LoRA 어댑터 저장 → to_ctranslate2.py 로 병합·변환
    processor.save_pretrained(out_dir)
    print(f"[done] LoRA 어댑터 저장: {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="manifest_train.jsonl")
    ap.add_argument("--eval", default="manifest_eval.jsonl")
    ap.add_argument("--out", default="whisper-medium-ko-senior-lora")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--base", default=BASE_MODEL)
    a = ap.parse_args()
    main(a.train, a.eval, a.out, a.epochs, a.base)
