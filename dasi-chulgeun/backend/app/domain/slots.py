# -*- coding: utf-8 -*-
"""domain/slots — 전사 텍스트 → 온보딩 핵심 슬롯 추출(결정론).

VAD 발화 전사에서 '잡다한 말(음·그러니까·저는 이제)'은 무시하고, 사전에 있는
직무·연수·지역·자격만 뽑는다. LLM 아님(하이브리드의 '규칙=즉시' 단계).
"""
from __future__ import annotations

import re

# 직무 키워드 → (표시 직무, 스킬셋). 프론트 온보딩 칩과 정합.
_JOB = [
    (("품질", "검사", "큐씨", "qc"), "품질관리·검사", ["품질관리", "검사장비", "불량분석"]),
    (("생산", "공정", "라인"), "생산관리", ["생산관리", "공정관리", "불량분석"]),
    (("물류", "현장", "지게차", "입출고", "창고"), "물류·현장", ["현장관리", "안전관리"]),
    (("설비", "보전", "전기", "정비", "기계"), "설비보전", ["설비보전", "전기"]),
]
# 지역: 더 구체적인 표기를 먼저(부분일치 우선순위).
_REGION = ["인천 남동구", "인천 부평구", "경기 시흥시", "남동구", "부평구", "시흥",
           "부천", "인천", "안산", "수원", "서울", "경기"]
_CERT = ["지게차", "품질경영기사", "품질기사", "전기기능사", "용접", "한식조리",
         "컴퓨터활용", "운전면허", "산업안전", "위험물"]

_YEARS = re.compile(r"(\d{1,2})\s*년")


def extract(text: str) -> dict:
    """텍스트 → {jobKind, skills, years, region, certs} 중 발견된 것만. 못 찾으면 키 없음."""
    raw = text or ""
    t = raw.replace(" ", "")
    low = t.lower()
    out: dict = {}

    for keys, jobkind, skills in _JOB:
        if any(k in low for k in keys):
            out["jobKind"] = jobkind
            out["skills"] = list(skills)
            break

    m = _YEARS.search(t)
    if m:
        y = int(m.group(1))
        if 0 < y <= 60:  # 상식 범위(오인식 방어)
            out["years"] = y

    for r in _REGION:
        if r.replace(" ", "") in t:
            out["region"] = r
            break

    certs = [c for c in _CERT if c in t]
    if certs:
        out["certs"] = certs

    return out
