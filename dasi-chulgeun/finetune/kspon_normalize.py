# -*- coding: utf-8 -*-
"""kspon_normalize — AI-Hub KsponSpeech(71592 계열) 전사 표기를 학습/평가용 순수 텍스트로 정규화.

KsponSpeech 전사 규약(요지):
  · 이중전사  (철자전사)/(발음전사)   예: (그래서)/(그래가지고)  → 하나를 택함
  · 잡음 태그  b/ n/ l/ o/ u/          숨소리·잡음·웃음·기타·불명 → 제거
  · 기호       +(반복) *(불확실) /(구분)  → 제거
  · 간투어     음 어 아 그 뭐 등        → drop_fillers 옵션으로 제거(선택)

references:
  - KsponSpeech 데이터 규약(AI-Hub) / speechbrain·HF의 kspon 레시피와 동일 관례.
  - 평가 CER의 '정답'은 여기서 나온 정규화 문자열을 기준으로 삼는다(전처리 일관성 = 공정성).

주의: 실제 71592 라벨 파일을 받으면 표기 세부(태그 문자셋)를 한 번 확인해 아래 상수를 맞출 것.
"""
from __future__ import annotations

import re

# (철자전사)/(발음전사) → 그룹1(철자) 또는 그룹2(발음) 선택
_DUAL = re.compile(r"\(([^)]*)\)\s*/\s*\(([^)]*)\)")
# 잡음/특수 태그: b/ n/ l/ o/ u/ (앞에 공백 또는 문두)
_NOISE = re.compile(r"(?:^|(?<=\s))[bnlou]\s*/")
# 남는 특수기호
_SYM = re.compile(r"[+*/\\]")
# 간투어(선행 연구·RTZR '간투어 제거'와 동일 취지). 단독 토큰일 때만 제거.
_FILLERS = {"음", "어", "아", "에", "그", "저", "뭐", "이제", "그러니까", "인제", "막", "좀"}
_MULTISPACE = re.compile(r"\s+")


def normalize(text: str, *, pron: bool = False, drop_fillers: bool = False) -> str:
    """KsponSpeech 전사 1줄 → 정규화 텍스트.

    pron=False → 철자전사 채택(숫자/영어를 글자로), True → 발음전사.
    drop_fillers=True → 간투어 단독 토큰 제거(간투어 자동 제거 모델을 학습할 때 타깃에 사용).
    """
    if not text:
        return ""
    s = _DUAL.sub(lambda m: m.group(2 if pron else 1), text)
    s = _NOISE.sub(" ", s)
    s = _SYM.sub(" ", s)
    s = _MULTISPACE.sub(" ", s).strip()
    if drop_fillers and s:
        s = " ".join(w for w in s.split() if w not in _FILLERS)
        s = _MULTISPACE.sub(" ", s).strip()
    return s


if __name__ == "__main__":  # 간이 자기검증(로컬, 데이터 없이 규약만 검증)
    cases = [
        ("(그래서)/(그래가지고) b/ 품질관리를 (10)/(십) 년 했어요",
         "그래서 품질관리를 10 년 했어요"),
        ("음 그 n/ 지게차 자격증도 +있고", "음 그 지게차 자격증도 있고"),
    ]
    for raw, exp in cases:
        got = normalize(raw)
        print(("OK " if got == exp else "XX ") + repr(got))
        assert got == exp, f"expected {exp!r}, got {got!r}"
    # 간투어 제거 변형
    print("drop_fillers:", repr(normalize("음 그 지게차 자격증도 있고", drop_fillers=True)))
    print("pron:", repr(normalize("(10)/(십) 년", pron=True)))
    print("all ok")
