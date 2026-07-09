# -*- coding: utf-8 -*-
"""tests/test_domain — 결정론 로직 단위 검증(RULE §2: 변경 후 실제 동작 확인).

domain 은 순수 함수이므로 외부 의존 없이 검증 가능. 계산이 상수 하드코딩이 아님을 보증.
실행: backend/ 에서  python -m pytest -q
"""
from __future__ import annotations

from app.domain import competency, rubric, scheduling, slots
from app.domain.matching import Job, Profile, fit_score, rank


def _job(**kw) -> Job:
    base = dict(job_id="J", company="C", role="R", region="인천 남동구",
                required_skills=frozenset({"품질관리", "검사장비"}), min_years=5,
                senior_friendly=True, tags=())
    base.update(kw)
    return Job(**base)


def test_fit_perfect_is_100():
    p = Profile.of(15, ["품질관리", "검사장비"], "인천 남동구")
    assert fit_score(p, _job()) == 100


def test_fit_monotonic_with_skill_overlap():
    job = _job()
    p_full = Profile.of(15, ["품질관리", "검사장비"], "인천 남동구")
    p_half = Profile.of(15, ["품질관리"], "인천 남동구")
    assert fit_score(p_full, job) > fit_score(p_half, job)


def test_experience_shortfall_lowers_score():
    job = _job(min_years=10)
    p_low = Profile.of(2, ["품질관리", "검사장비"], "인천 남동구")
    p_high = Profile.of(10, ["품질관리", "검사장비"], "인천 남동구")
    assert fit_score(p_high, job) > fit_score(p_low, job)


def test_rank_is_descending_and_stable():
    p = Profile.of(15, ["품질관리", "검사장비"], "인천 남동구")
    jobs = [_job(job_id="A", required_skills=frozenset({"품질관리"})),
            _job(job_id="B")]
    ranked = rank(p, jobs)
    scores = [s for _, s, _ in ranked]
    assert scores == sorted(scores, reverse=True)


def test_scheduling_intersection_earliest():
    cand = ["THU_15", "TUE_14", "FRI_10"]
    comp = ["TUE_14", "THU_15"]
    assert scheduling.common_slots(cand, comp) == ["TUE_14", "THU_15"]  # 이른 순
    assert scheduling.confirm_earliest(cand, comp) == "TUE_14"


def test_scheduling_no_overlap_returns_none():
    assert scheduling.confirm_earliest(["MON_09"], ["FRI_17"]) is None


def test_scheduling_label():
    assert scheduling.label("TUE_14") == "화요일 오후 2시"
    assert scheduling.label("MON_09") == "월요일 오전 9시"


def test_competency_grades_and_weakest():
    res = competency.evaluate({
        "domain_expertise": ("직무 전문성", 88),
        "communication": ("의사소통", 60),
        "quantify_achievement": ("성과를 숫자로", 35),
    })
    grades = {r.key: r.grade for r in res}
    assert grades == {"domain_expertise": "strong", "communication": "ok",
                      "quantify_achievement": "gap"}
    assert competency.weakest(res).key == "quantify_achievement"


def test_competency_clamps_out_of_range():
    res = competency.evaluate({"x": ("X", 250), "y": ("Y", -5)})
    scores = {r.key: r.score for r in res}
    assert scores == {"x": 100, "y": 0}


def test_rubric_density_and_evidence():
    rich = "품질검사를 하며 불량 원인을 데이터로 분석해 재발 방지 표준을 세웠습니다."
    poor = "품질 일을 오래 했습니다."
    def score(text, key):
        return next(r for r in rubric.extract(text) if r["key"] == key)
    # 지표 밀도가 높은 답변이 더 높은 점수 + 근거 문장 존재
    assert score(rich, "domain_expertise")["score"] > score(poor, "domain_expertise")["score"]
    assert score(rich, "problem_solving")["evidence"]  # 근거 문장 추출됨


def test_rubric_quantify_needs_numbers():
    with_num = "불량률을 3%에서 0.8%로 낮췄고 처리 시간을 20% 단축했습니다."
    without = "성과를 많이 냈고 개선도 했습니다."
    q = lambda t: next(r for r in rubric.extract(t) if r["key"] == "quantify_achievement")["score"]
    # 정량화 축은 수치가 있어야 높은 점수(없으면 '수치 부족' 신호)
    assert q(with_num) >= 50 > q(without)


def test_slots_keep_core_drop_filler():
    s = slots.extract("음 그러니까 제가 이제 지게차 면허도 있고 물류 현장에서 일했어요 부천에서 25년")
    assert s.get("jobKind") == "물류·현장"
    assert s.get("region") == "부천"
    assert s.get("years") == 25
    assert "지게차" in s.get("certs", [])
    # 잡담만이면 빈 슬롯(사전에 없으면 버려짐)
    assert slots.extract("음 어 그러니까 뭐 그냥 이제") == {}
