#!/usr/bin/env python3
"""Build the pilot-30 stratified sample (v2 + v3 input packages).

Deterministic: sorts by md5(article id) within each stratum, per-author caps.
v3 package adds spans (sentence split) + script fields (company, ingredient_mentions,
is_event/event_type) for the V3/V4 C+D pipeline.

Run from repo root:
    python3 product/output/test-results/section-tagging-test/scripts/make_pilot_sample.py
"""
import json, hashlib, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "project-management/reference/examples/all-articles(1).json"
OUT_DIR = ROOT / "product/output/test-results/section-tagging-test/fixtures"

STRATA = [
    ("success", lambda n: n >= 800, 18, 2),
    ("partial", lambda n: 300 <= n < 800, 5, 2),
    ("title_only", lambda n: 0 < n < 300, 4, 2),
    ("empty", lambda n: n == 0, 3, 2),
]
CONTENT_TRIM = 2500

COMPETITOR_HINTS = ["BASF", "巴斯夫", "Symrise", "德之馨", "Lubrizol", "路博润", "Ashland",
    "亚什兰", "Evonik", "赢创", "辉文", "唯铂莱", "Viablife", "聚源", "JLand", "克琴",
    "帝斯曼", "DSM", "奇华顿", "Givaudan", "IFF", "斯泰兰", "Clariant", "科莱恩", "禾大", "Croda"]
CUSTOMER_HINTS = ["欧莱雅", "珀莱雅", "薇诺娜", "自然堂", "雅诗兰黛", "兰蔻", "资生堂", "SK-II",
    "玉兰油", "OLAY", "多芬", "联合利华", "宝洁", "上美", "华熙生物", "贝泰妮", "韩束", "丸美",
    "毛戈平", "林清轩"]
INGREDIENT_HINTS = ["PDRN", "多肽", "胜肽", "peptide", "胶原", "collagen", "神经酰胺", "ceramide",
    "视黄醇", "A醇", "retinol", "透明质酸", "玻尿酸", "hyaluronic", "烟酰胺", "麦角硫因", "外泌体",
    "exosome", "防晒剂", "sunscreen", "发酵", "合成生物", "微生态", "microbiome", "益生菌",
    "重组胶原", "植物提取", "AI", "人工智能"]
EVENT_HINTS = ["PCHi", "in-cosmetics", "展会", "峰会", "研讨会", "发布会", "论坛", "直播",
    "报名", "盛典", "大会", "颁奖", "圆满落幕", "邀请函", "展位"]

SENT_SPLIT_RE = re.compile(r"[^。！？；!?;\n]+[。！？；!?;\n]?")
EVENT_TYPE_RULES = [
    ("expo", ["PCHi", "in-cosmetics", "ICIC", "展会", "展位", "博览会"]),
    ("webinar", ["WeMeet", "网络研讨", "直播"]),
    ("forum", ["论坛", "研讨会", "峰会", "大会", "沙龙"]),
    ("award", ["芳典奖", "获奖", "颁奖", "盛典", "奖"]),
    ("launch_event", ["发布会", "全球首发", "新品发布"]),
    ("other", ["报名", "预告", "邀请", "圆满落幕", "回顾"]),
]


def find_hits(text, vocab):
    return [t for t in vocab if re.search(re.escape(t), text, re.IGNORECASE)]


def split_spans(title, content):
    spans = []
    if title:
        spans.append({"id": "s0", "text": title.strip()})
    idx = 1
    for m in SENT_SPLIT_RE.finditer(content or ""):
        seg = m.group(0).strip()
        if len(seg) < 2:
            continue
        spans.append({"id": f"s{idx}", "text": seg})
        idx += 1
    return spans


def detect_event(text):
    for etype, kws in EVENT_TYPE_RULES:
        if any(re.search(re.escape(k), text, re.IGNORECASE) for k in kws):
            return True, etype
    return False, None


def main():
    data = json.loads(SRC.read_text())
    articles = data["articles"]
    picked, picked_ids = [], set()
    for name, pred, quota, cap in STRATA:
        pool = [a for a in articles if pred(len(a.get("contentText") or ""))]
        pool.sort(key=lambda a: hashlib.md5(a["id"].encode()).hexdigest())
        per_author = defaultdict(int)
        taken = 0
        for a in pool:
            if taken >= quota:
                break
            if per_author[a["author"]] >= cap or a["id"] in picked_ids:
                continue
            per_author[a["author"]] += 1
            picked_ids.add(a["id"])
            a["_stratum"] = name
            picked.append(a)
            taken += 1

    out, out_v3 = [], []
    for a in picked:
        text = (a.get("contentText") or "").strip()
        title = a.get("title") or ""
        trimmed = text[:CONTENT_TRIM]
        hint_text = title + " " + text[:4000]
        seen_text = title + " " + trimmed
        fact_hints = {
            "competitor_or_supplier": find_hits(hint_text, COMPETITOR_HINTS),
            "customer_or_brand": find_hits(hint_text, CUSTOMER_HINTS),
            "ingredient_technology": find_hits(hint_text, INGREDIENT_HINTS),
            "event": find_hits(hint_text, EVENT_HINTS),
        }
        record = {
            "article_id": a["id"], "title": title, "source_name": a["author"],
            "content": trimmed, "content_truncated": len(text) > CONTENT_TRIM,
            "content_length": len(text), "extraction_status": a["_stratum"],
            "url": a.get("url"), "fact_hints": fact_hints,
        }
        out.append(record)
        is_event, event_type = detect_event(seen_text)
        v3 = dict(record)
        v3["spans"] = split_spans(title, trimmed)
        v3["company"] = sorted(set(fact_hints["competitor_or_supplier"] + fact_hints["customer_or_brand"]))
        v3["ingredient_mentions"] = fact_hints["ingredient_technology"]
        v3["is_event"] = is_event
        v3["event_type"] = event_type
        out_v3.append(v3)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "pilot-30-input.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    (OUT_DIR / "pilot-30-input-v3.json").write_text(json.dumps(out_v3, ensure_ascii=False, indent=2))
    print(f"wrote {len(out)} articles (v2 + v3)")
    for name, *_ in STRATA:
        print(f"  {name}: {sum(1 for r in out if r['extraction_status']==name)}")
    print("ids:", " ".join(r["article_id"][:10] for r in out_v3))


if __name__ == "__main__":
    main()
