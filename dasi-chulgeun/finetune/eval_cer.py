# -*- coding: utf-8 -*-
"""eval_cer — 연령대별 CER(문자오류율) 측정. "일반 8% → 중장년 X%"를 직접 재는 도구.

이게 이 프로젝트의 핵심 실험이다: 모든 공개 STT 벤치는 일반 성인 기준 → 55+ 발화에서의 숫자는
검색으로 안 나온다. 확보한 연령필터 데이터로 여기서 직접 측정한다(파인튜닝 전/후 동일 하네스).

manifest(JSONL) 한 줄 = {"audio": "경로.wav", "ref": "정답전사", "age": 57}
  · ref 는 kspon_normalize.normalize() 를 통과시킨 정규화 문자열을 권장(전처리 일관성).

CER = 편집거리(문자) / 정답 문자수.  공백 포함/제외 둘 다 출력(한국어 관례상 제외본을 주로 본다).
대량(수천 발화)이면 jiwer/rapidfuzz 로 가속 가능하나, 여기선 의존성 0의 순수 파이썬으로 둔다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _lev(a: str, b: str) -> int:
    """문자 단위 Levenshtein 편집거리(순수 파이썬)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(ref: str, hyp: str, *, ignore_space: bool = True) -> tuple[int, int]:
    """(편집거리, 정답길이) 반환. CER = 편집거리/정답길이."""
    if ignore_space:
        ref = ref.replace(" ", "")
        hyp = hyp.replace(" ", "")
    return _lev(ref, hyp), max(len(ref), 1)


def _bucket(age: int | None) -> str:
    if age is None:
        return "unknown"
    if age < 45:
        return "under45"
    if age <= 54:
        return "45-54"
    return "55+"


def evaluate(manifest: str, transcribe_fn) -> dict:
    """manifest 각 줄을 transcribe_fn(audio_path)->str 로 전사하고 연령버킷별 CER 집계."""
    agg: dict[str, list[int]] = {}
    rows = []
    for line in Path(manifest).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        hyp = transcribe_fn(r["audio"]) or ""
        edits, n = cer(r["ref"], hyp)
        b = _bucket(r.get("age"))
        agg.setdefault(b, [0, 0])
        agg[b][0] += edits
        agg[b][1] += n
        agg.setdefault("ALL", [0, 0])
        agg["ALL"][0] += edits
        agg["ALL"][1] += n
        rows.append({"age": r.get("age"), "bucket": b, "cer": round(edits / n, 4),
                     "ref": r["ref"], "hyp": hyp})
    summary = {b: {"cer": round(e / max(t, 1), 4), "chars": t} for b, (e, t) in agg.items()}
    return {"summary": summary, "rows": rows}


def _demo_transcribe_backend(audio_path: str) -> str:
    """백엔드 whisper_stt 를 그대로 사용(현재 STT_MODEL 로 측정). 파인튜닝 후엔 STT_MODEL만 바꿔 재측정."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
    from app.infrastructure.stt import whisper_stt  # noqa: E402
    from finetune.kspon_normalize import normalize  # noqa: E402
    return normalize(whisper_stt.transcribe(Path(audio_path).read_bytes()) or "")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="연령대별 CER 측정")
    ap.add_argument("--manifest", help="JSONL: {audio, ref, age} 줄들")
    ap.add_argument("--selftest", action="store_true", help="CER 함수 자기검증(데이터 불필요)")
    args = ap.parse_args()

    if args.selftest:
        # CER 함수가 정확한지 데이터 없이 검증
        assert cer("품질관리", "품질관리") == (0, 4)          # 완전일치 → 0
        assert cer("품질관리", "품질간리")[0] == 1          # 관→간 1글자 치환
        assert cer("십년", "10년")[0] == 2                   # 십(1자)→10(2자): 치환1+삽입1
        e, n = cer("자동차 부품 공장", "자동차 부품 강장")  # 공→강 1치환, 공백무시 8자
        print(f"selftest CER 예시: {e}/{n} = {e/n:.3f}")
        print("CER 함수 자기검증 통과")
    elif args.manifest:
        out = evaluate(args.manifest, _demo_transcribe_backend)
        print(json.dumps(out["summary"], ensure_ascii=False, indent=2))
    else:
        ap.print_help()
