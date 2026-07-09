# -*- coding: utf-8 -*-
"""infrastructure/data/jobs_repository — 채용공고 저장소.

RULE §3.1: 고용24 직접연동은 기업회원 전용이라 개인·팀은 막힘. data.go.kr 워크넷
데이터셋이 대체경로지만 승인·오프라인 이슈가 있어, 데모는 **시드 데이터셋**으로 폴백한다.
(근거: init_plans/중장년_재취업_실행에이전트_팀공유브리핑.html §04 Evidence Ledger)

⚠️ 아래는 실측 공고가 아니라 데모용 예시 데이터(seed)다. 실서비스는 data.go.kr 연동으로 대체.
응답 meta.source 는 항상 "seed" 로 표기해 실데이터로 오인되지 않게 한다(RULE §1).
"""
from __future__ import annotations

from app.domain.matching import Job

SOURCE = "seed"  # live 연동 시 "live" 로 전환

# 슬롯 키는 domain/scheduling 의 'DAY_HH' 규약을 따른다.
_SEED_JOBS: list[dict] = [
    {
        "job_id": "J001", "company": "한빛정밀", "role": "품질검사 담당",
        "region": "인천 남동구", "required_skills": ["품질관리", "검사장비", "불량분석"],
        "min_years": 5, "senior_friendly": True, "tags": ["정규직", "주5일", "통근25분"],
        "company_slots": ["TUE_14", "THU_15", "FRI_10"], "auto_apply": True,
    },
    {
        "job_id": "J002", "company": "대성전자", "role": "생산관리",
        "region": "인천 부평구", "required_skills": ["생산관리", "불량분석", "공정관리"],
        "min_years": 3, "senior_friendly": True, "tags": ["정규직", "중장년우대"],
        "company_slots": ["MON_11", "WED_14", "THU_16"], "auto_apply": True,
    },
    {
        "job_id": "J003", "company": "서해산업", "role": "품질관리 팀원",
        "region": "인천 서구", "required_skills": ["품질관리", "iso9001"],
        "min_years": 4, "senior_friendly": False, "tags": ["정규직"],
        "company_slots": ["TUE_10", "FRI_15"], "auto_apply": False,  # 연계 안 됨 → 링크 제출
    },
    {
        "job_id": "J004", "company": "동방물류", "role": "물류 현장관리",
        "region": "인천 중구", "required_skills": ["현장관리", "안전관리"],
        "min_years": 2, "senior_friendly": True, "tags": ["정규직", "중장년우대", "교대"],
        "company_slots": ["MON_09", "WED_13"], "auto_apply": True,
    },
    {
        "job_id": "J005", "company": "정우기계", "role": "설비 보전",
        "region": "경기 시흥시", "required_skills": ["설비보전", "전기"],
        "min_years": 6, "senior_friendly": True, "tags": ["정규직"],
        "company_slots": ["THU_10", "FRI_14"], "auto_apply": True,
    },
    {
        "job_id": "J006", "company": "미래식품", "role": "생산라인 관리",
        "region": "인천 남동구", "required_skills": ["생산관리", "위생관리", "haccp"],
        "min_years": 3, "senior_friendly": True, "tags": ["정규직", "중장년우대"],
        "company_slots": ["TUE_14", "WED_15"], "auto_apply": True,
    },
]

# job_id → 원본 dict (라우터에서 회사 슬롯·auto_apply 조회용)
_BY_ID = {j["job_id"]: j for j in _SEED_JOBS}


def all_jobs() -> list[Job]:
    return [
        Job(
            job_id=j["job_id"], company=j["company"], role=j["role"], region=j["region"],
            required_skills=frozenset(s.lower() for s in j["required_skills"]),
            min_years=j["min_years"], senior_friendly=j["senior_friendly"],
            tags=tuple(j["tags"]),
        )
        for j in _SEED_JOBS
    ]


def raw(job_id: str) -> dict | None:
    return _BY_ID.get(job_id)


def company_slots(job_id: str) -> list[str]:
    j = _BY_ID.get(job_id)
    return list(j["company_slots"]) if j else []
