# -*- coding: utf-8 -*-
"""domain/rubric — 면접 답변 → NCS 역량 축 근거추출(결정론).

RULE §3.3: 역량 점수는 LLM이 아니라 **규칙(지표 키워드 매칭 + 정량화 검출)**으로 산출한다.
답변 텍스트에서 축별 근거 문장을 뽑고, 지표 수·수치 유무로 0~100 점을 결정론적으로 계산.
(계획서 PART 3: 답변 분석 → NCS rubric 매핑 → 역량 갭(수식))
"""
from __future__ import annotations

import re

# NCS 기반 역량 축(데모 스코프 5축) + 지표 키워드. 축 key 는 domain/competency·training 매핑과 일치.
RUBRIC: list[dict] = [
    {"key": "domain_expertise", "label": "직무 전문성",
     "indicators": ["품질", "검사", "측정", "공정", "불량", "설비", "생산", "자격", "장비", "기준", "표준", "점검", "보전", "안전"]},
    {"key": "problem_solving", "label": "문제 해결",
     "indicators": ["원인", "분석", "개선", "해결", "재발", "대응", "진단", "방지", "최적화", "데이터"]},
    {"key": "quantify_achievement", "label": "성과를 숫자로 설명", "quantified": True,
     "indicators": ["감소", "향상", "달성", "단축", "절감", "증가", "개선", "성과", "실적"]},
    {"key": "communication", "label": "의사소통",
     "indicators": ["협업", "소통", "조율", "공유", "설명", "교육", "전달", "후배", "협력", "회의"]},
    {"key": "leadership", "label": "리더십",
     "indicators": ["반장", "조장", "리더", "이끌", "관리", "인원", "운영", "책임", "지휘"]},
]

# 정량 성과 판정: 숫자 + 단위(%, 명, 년, 개월, 건, 배 등). 단위 없이 연도만은 약하게 취급.
_QUANT = re.compile(r"\d+(?:\.\d+)?\s*(?:%|퍼센트|명|건|배|원|시간|분|개|톤|억|만)")
_SENT = re.compile(r"[^.!?\n]+")

# 튜닝 지점 집약(RULE §3.2) — 매직 넘버 흩뿌리기 금지. 점수는 '서로 다른 지표 수'(밀도) 기반.
_BASE = 30            # 지표 1개 시작점
_PER = 13             # 서로 다른 지표당 가산
_NO_HIT = 15          # 지표 전무
_QUANT_BASE = 50      # 정량 축: 수치 있을 때 시작점
_QUANT_PER = 12       # 정량 축 지표당 가산
_QUANT_NONUM = 32     # 정량 축: 수치 없을 때 상한(부족 신호)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.findall(text or "") if s.strip()]


def extract(answer_text: str) -> list[dict]:
    """답변 → 축별 {key, label, score(0~100), evidence[문장], hits}. 결정론.

    hits = 답변에 등장한 **서로 다른 지표 키워드 수**(문장 수 아님) → 근거 밀도를 반영.
    정량화 축은 숫자+단위(_QUANT)가 있어야 높은 점수(없으면 '수치 부족' 신호).
    """
    text = answer_text or ""
    sents = _sentences(text)
    out: list[dict] = []
    for ax in RUBRIC:
        matched = [k for k in ax["indicators"] if k in text]  # 서로 다른 지표
        hits = len(matched)
        ev = [s for s in sents if any(k in s for k in ax["indicators"])][:2]
        if ax.get("quantified"):
            num_sents = [s for s in sents if _QUANT.search(s)]
            if num_sents:
                score = min(100, _QUANT_BASE + _QUANT_PER * hits)
                ev = (num_sents[:1] + [s for s in ev if s not in num_sents[:1]])[:2]
            else:
                score = min(_QUANT_NONUM, 18 + 5 * hits)
        else:
            score = min(100, _BASE + _PER * hits) if hits else _NO_HIT
        out.append({"key": ax["key"], "label": ax["label"], "score": int(score),
                    "evidence": ev, "hits": hits})
    return out
