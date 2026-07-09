# -*- coding: utf-8 -*-
"""embed_bench — 한국어 임베딩 모델 검색 성능 실측(모델 1개씩).

우리 도메인(재취업·창업 지원사업/인허가/직무) 소형 검색 프로브로 Recall@1·Recall@3·MRR 측정.
디스크 11.9GB 제약 → 드라이버가 모델 1개 받아 평가 후 캐시 삭제하고 다음으로 넘어감.

⚠️ 정직 고지: 이건 12문서·10질의의 **소형 도메인 프로브**지 공식 MTEB가 아니다. 상대비교 지표로만 해석.
실행(1모델): python embed_bench.py "<model_name>"
"""
from __future__ import annotations

import json
import os
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

# ── 도메인 검색 프로브 (문서 22 · 질의 14). 유사 함정(distractor) + 구어체 질의로 변별력 확보 ──
DOCS = {
    # 자금·지원 (서로 헷갈리는 4종)
    "d1": "신사업창업사관학교는 예비창업자에게 4주 창업교육과 최대 2천만원 사업화 자금을 함께 지원한다.",
    "d2": "희망리턴패키지는 폐업한 소상공인의 재창업 또는 재취업 전환을 사업화 자금과 컨설팅으로 돕는다.",
    "d3": "소상공인 정책자금은 창업 초기의 시설 자금과 운전 자금을 저리로 융자해 준다.",
    "d4": "국민내일배움카드는 직업훈련비를 국비로 지원하며 자격증 취득 과정을 수강할 수 있다.",
    # 재취업 계열 (창업과 구분)
    "d5": "중장년 취업성공수당은 재취업에 성공한 구직자에게 단계별로 현금을 지급한다.",
    "d6": "고령자 계속고용장려금은 정년이 지난 근로자를 계속 고용하는 기업에 지원금을 준다.",
    # 품질·제조 (서로 헷갈리는 4종)
    "d7": "품질검사 대행업은 제조사를 대상으로 품질관리와 검사장비 운용 경력을 살린 무점포 창업이다.",
    "d8": "품질·ISO 교육 강사는 현장 품질관리 경력을 바탕으로 기업에 출강하고 온라인 강의를 한다.",
    "d9": "생산관리 재취업 공고는 중소 제조사가 생산관리 담당 정규직을 채용하는 자리다.",
    "d10": "스마트공장 품질데이터 분석은 제조 데이터로 불량을 예측하는 새로운 직무다.",
    # 안전·자격 (서로 헷갈리는 4종)
    "d11": "산업안전 관리 위탁은 50인 미만 사업장의 안전관리를 대행하며 중대재해처벌법에 대응한다.",
    "d12": "지게차 운전기능사는 물류 현장에서 지게차를 운전하기 위한 국가기술자격이다.",
    "d13": "산업안전기사는 사업장 안전관리자로 선임되기 위해 필요한 국가기술자격이다.",
    "d14": "위험물산업기사는 위험물의 취급과 저장을 관리하기 위한 국가기술자격이다.",
    # 신고·등록 (서로 헷갈리는 3종)
    "d15": "사업자등록은 홈택스에서 개인사업자로 등록하며 과세와 면세 여부를 판단해야 한다.",
    "d16": "식품 영업신고는 식품위생법에 따라 음식 관련 영업 전에 신고하고 위생교육을 이수하는 절차다.",
    "d17": "통신판매업 신고는 온라인으로 상품을 판매할 때 관할 구청에 하는 신고다.",
    # 기타 서비스
    "d18": "상권정보 분석은 소상공인시장진흥공단이 업종별 상권 밀도와 경쟁 현황 데이터를 제공한다.",
    "d19": "중장년 기술창업센터는 만 40세 이상 기술창업자에게 보육 공간과 멘토링을 제공한다.",
    "d20": "온라인 판로지원은 소상공인의 스마트스토어 입점과 판매 교육을 도와준다.",
    "d21": "세무 기장 대행은 소규모 사업자의 부가세와 종합소득세 신고를 대신 처리한다.",
    "d22": "사업계획서 작성 컨설팅은 창업자의 사업계획서를 첨삭하고 멘토링한다.",
}
QUERIES = [
    ("가게 접고 나서 뭐라도 다시 해보려는데 나라에서 도와주는 거 있나요", ["d2"]),
    ("품질관리만 20년 했는데 이 경력으로 사장님 소리 들으려면 뭘 할 수 있죠", ["d7", "d8"]),
    ("가르치는 걸 좋아하는데 내 품질 경력 살려서 강의 같은 거 하고 싶어요", ["d8"]),
    ("창업도 배우면서 초기 자금도 좀 보태주는 교육 없나요", ["d1"]),
    ("지게차 몰려면 무슨 자격증을 따야 하나요", ["d12"]),
    ("사업장 안전관리자로 선임되려면 따야 하는 국가자격", ["d13"]),
    ("작은 공장 안전관리를 통째로 대신 해주는 서비스", ["d11"]),
    ("온라인으로 물건 팔려면 무슨 신고를 해야 하나요", ["d17"]),
    ("밥집 차리려면 위생 관련해서 뭘 신고해야 하죠", ["d16"]),
    ("세금 신고가 너무 귀찮은데 대신 해주는 데 없나요", ["d21"]),
    ("정년 지났는데 계속 일하면 회사가 지원금 받는다던데", ["d6"]),
    ("재취업에 성공하면 나라에서 돈을 준다고 들었어요", ["d5"]),
    ("우리 동네에 같은 장사 몇 집이나 있는지 데이터로 보고 싶어", ["d18"]),
    ("스마트스토어에 상품 올려서 파는 걸 도와주는 지원", ["d20"]),
]


def _enc(model, texts, is_query, name):
    """모델별 관례 반영: e5계열은 query:/passage: 프리픽스, 그 외는 모델 자체 프롬프트→없으면 raw."""
    nl = name.lower()
    if "e5" in nl:
        pref = "query: " if is_query else "passage: "
        return model.encode([pref + t for t in texts], normalize_embeddings=True)
    try:
        return model.encode(texts, prompt_name=("query" if is_query else "document"),
                            normalize_embeddings=True)
    except Exception:
        return model.encode(texts, normalize_embeddings=True)


def run(name: str) -> dict:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    t0 = time.time()
    model = SentenceTransformer(name, device="cpu", trust_remote_code=True)
    load_s = time.time() - t0

    doc_ids = list(DOCS.keys())
    t1 = time.time()
    D = np.asarray(_enc(model, [DOCS[i] for i in doc_ids], False, name))
    Q = np.asarray(_enc(model, [q for q, _ in QUERIES], True, name))
    enc_s = time.time() - t1

    sims = Q @ D.T  # 정규화됨 → 코사인
    r1 = r3 = 0
    mrr = 0.0
    for qi, (_, gold) in enumerate(QUERIES):
        order = np.argsort(-sims[qi])
        ranked = [doc_ids[j] for j in order]
        rank = next((k + 1 for k, d in enumerate(ranked) if d in gold), 999)
        if rank == 1:
            r1 += 1
        if rank <= 3:
            r3 += 1
        mrr += 1.0 / rank
    n = len(QUERIES)
    return {"model": name, "dim": int(D.shape[1]), "params_note": "",
            "recall@1": round(r1 / n, 3), "recall@3": round(r3 / n, 3),
            "mrr": round(mrr / n, 3), "load_s": round(load_s, 1),
            "encode_s": round(enc_s, 2), "error": None}


if __name__ == "__main__":
    name = sys.argv[1]
    try:
        print(json.dumps(run(name), ensure_ascii=False))
    except Exception as e:  # noqa: BLE001 — 실패(게이트/OOM 등)도 결과로 기록
        print(json.dumps({"model": name, "error": f"{type(e).__name__}: {e}"[:300]}, ensure_ascii=False))
