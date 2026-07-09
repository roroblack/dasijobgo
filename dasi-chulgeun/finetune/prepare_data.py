# -*- coding: utf-8 -*-
"""prepare_data — [SCAFFOLD·미검증] AI-Hub 71592 라벨 → 연령필터 → 정규화 → 학습/평가 manifest.

⚠️ 이 스크립트는 실제 71592 파일이 로컬에 없어 아직 실행·검증하지 못했다(RULE §1: 미검증 명시).
   데이터를 받은 뒤 아래 '확인 지점'을 실제 파일에 맞춰 조정할 것. 로직 골격은 완성되어 있다.

AI-Hub 음성 데이터 통상 구조(데이터셋마다 다름 — 반드시 실제 파일로 확인):
   root/
     .../*.wav          (또는 .pcm)
     .../*.json         (전사+화자 메타)  또는  라벨.csv 하나
   JSON 예(키 이름은 데이터셋별 상이): {"전사정보"|"transcription": "...",
                                       "화자정보"|"speaker": {"연령"|"age": "50대"|57, ...}}

출력: manifest JSONL 각 줄 {"audio","ref","age"} — eval_cer.py / train_lora.py 공용 입력.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from kspon_normalize import normalize

# ── 확인 지점 ①: 전사·나이 필드 후보 키(실제 JSON 보고 맞출 것) ──
_TEXT_KEYS = ["transcription", "전사정보", "text", "발화문", "orgtext", "AnnotationText"]
_AGE_KEYS = ["age", "연령", "나이", "ageGroup", "연령대"]
_SPEAKER_KEYS = ["speaker", "화자정보", "speakerInfo", "metadata"]
_RANGE = re.compile(r"(\d{2})\s*대")   # "50대" → 50


def _dig(obj, keys):
    """중첩 dict에서 후보 키 중 처음 걸리는 값(1단계 + speaker 하위 탐색)."""
    if not isinstance(obj, dict):
        return None
    for k in keys:
        if k in obj and obj[k] not in (None, ""):
            return obj[k]
    for sk in _SPEAKER_KEYS:
        if isinstance(obj.get(sk), dict):
            for k in keys:
                v = obj[sk].get(k)
                if v not in (None, ""):
                    return v
    return None


def _to_age(v) -> int | None:
    """정수 나이 또는 '50대' 범위표기 → 정수(범위는 하한값). 파싱 실패 None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v)
    m = _RANGE.search(s)
    if m:
        return int(m.group(1))          # "50대" → 50
    m = re.search(r"\d{1,3}", s)
    return int(m.group()) if m else None


def build(root: str, out: str, min_age: int, pron: bool, drop_fillers: bool) -> dict:
    root_p = Path(root)
    n_total = n_kept = 0
    buckets: dict[str, int] = {}
    with Path(out).open("w", encoding="utf-8") as f:
        # ── 확인 지점 ②: 라벨이 개별 json인지, 단일 csv/json인지에 따라 이 순회를 조정 ──
        for jp in root_p.rglob("*.json"):
            try:
                obj = json.loads(jp.read_text(encoding="utf-8"))
            except Exception:
                continue
            n_total += 1
            raw_text = _dig(obj, _TEXT_KEYS)
            age = _to_age(_dig(obj, _AGE_KEYS))
            if not raw_text or age is None or age < min_age:
                continue
            # ── 확인 지점 ③: 오디오 경로 규칙(보통 같은 stem의 .wav/.pcm) ──
            wav = jp.with_suffix(".wav")
            if not wav.exists():
                pcm = jp.with_suffix(".pcm")
                if not pcm.exists():
                    continue
                wav = pcm
            ref = normalize(str(raw_text), pron=pron, drop_fillers=drop_fillers)
            if not ref:
                continue
            b = "55+" if age >= 55 else "45-54" if age >= 45 else "under45"
            buckets[b] = buckets.get(b, 0) + 1
            n_kept += 1
            f.write(json.dumps({"audio": str(wav), "ref": ref, "age": age}, ensure_ascii=False) + "\n")
    return {"scanned": n_total, "kept": n_kept, "buckets": buckets, "out": out}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="AI-Hub 71592 → 연령필터 manifest")
    ap.add_argument("--root", required=True, help="압축 해제한 71592 데이터 루트")
    ap.add_argument("--out", default="manifest_train.jsonl")
    ap.add_argument("--min-age", type=int, default=45, help="이 나이 이상만(중장년 45+, 55+는 55)")
    ap.add_argument("--pron", action="store_true", help="발음전사 채택(기본은 철자전사)")
    ap.add_argument("--drop-fillers", action="store_true", help="간투어 제거(간투어 자동제거 학습용 타깃)")
    a = ap.parse_args()
    print(json.dumps(build(a.root, a.out, a.min_age, a.pron, a.drop_fillers), ensure_ascii=False, indent=2))
