#!/usr/bin/env python3
"""Step 1: narrow the 499 into precise regulation / ka_watch probe candidates.

Title-strong-signal filtering (much higher precision than content keyword hit),
with event/promo noise excluded and per-author caps. Emits v3-style records
(spans + script fields) ready for Opus triage + section test.

Run from repo root:
    python3 product/output/test-results/section-tagging-test/scripts/build_probe_candidates.py
"""
import json, re
from collections import defaultdict
from pathlib import Path
# reuse span/event/hint helpers from the sampler
import importlib.util
ROOT = Path(__file__).resolve().parents[5]
spec = importlib.util.spec_from_file_location("mps", Path(__file__).parent / "make_pilot_sample.py")
mps = importlib.util.module_from_spec(spec); spec.loader.exec_module(mps)

SRC = ROOT / "project-management/reference/examples/all-articles(1).json"
OUT = ROOT / "product/output/test-results/section-tagging-test/fixtures/probe-candidates.json"

# regulation: title says regulation/registration; exclude event/promo noise
REG_TITLE = ["备案", "法规", "监管", "药监", "条例", "致敏", "禁用", "限用", "新原料",
             "不良反应", "白名单", "注册", "国家标准", "团体标准", "合规", "安评", "标准发布", "新规"]
NOISE = ["PCHi", "报名", "回顾", "芳典奖", "展会", "峰会", "邀您", "大会", "招聘", "求职"]
KA = ["欧莱雅", "玉兰油", "OLAY", "大宝", "AHC", "凡士林", "施华蔻", "沙宣", "清扬", "露得清",
      "多芬", "力士", "旁氏", "兰蔻", "科颜氏", "赫莲娜", "雅诗兰黛", "海蓝之谜", "倩碧", "SK-II",
      "优色林", "韩束", "红色小象", "珀莱雅", "薇诺娜", "润百颜", "夸迪", "米蓓尔", "BM肌活",
      "佰草集", "丸美", "完美日记", "可复美", "颐莲", "瑷尔博士", "自然堂", "美肤宝", "HBN"]
ING = ["多肽", "胜肽", "PDRN", "核酸", "神经酰胺", "视黄醇", "A醇", "重组胶原", "胶原", "透明质酸",
       "玻尿酸", "烟酰胺", "麦角硫因", "外泌体", "益生菌", "后生元", "发酵", "合成生物", "提取物",
       "原料", "活性物", "成分", "配方", "玻色因", "胜肽"]
CAP = 2


def has(text, vocab):
    return any(re.search(re.escape(k), text, re.IGNORECASE) for k in vocab)


def to_record(a, pool):
    text = (a.get("contentText") or "").strip()
    title = a.get("title") or ""
    trimmed = text[:mps.CONTENT_TRIM]
    seen = title + " " + trimmed
    fh = {
        "competitor_or_supplier": mps.find_hits(title + " " + text[:4000], mps.COMPETITOR_HINTS),
        "customer_or_brand": mps.find_hits(title + " " + text[:4000], mps.CUSTOMER_HINTS),
        "ingredient_technology": mps.find_hits(title + " " + text[:4000], mps.INGREDIENT_HINTS),
        "event": mps.find_hits(title + " " + text[:4000], mps.EVENT_HINTS),
    }
    is_event, event_type = mps.detect_event(seen)
    return {
        "article_id": a["id"], "title": title, "source_name": a["author"],
        "content": trimmed, "content_length": len(text),
        "extraction_status": "success" if len(text) >= 800 else ("partial" if len(text) >= 300 else ("title_only" if text else "empty")),
        "candidate_pool": pool, "fact_hints": fh,
        "spans": mps.split_spans(title, trimmed),
        "company": sorted(set(fh["competitor_or_supplier"] + fh["customer_or_brand"])),
        "ingredient_mentions": fh["ingredient_technology"],
        "is_event": is_event, "event_type": event_type,
    }


def main():
    arts = json.loads(SRC.read_text())["articles"]
    reg, ka = [], []
    pa_reg, pa_ka = defaultdict(int), defaultdict(int)
    seen_ids = set()
    # regulation: title strong signal, no noise, has some body
    for a in sorted(arts, key=lambda x: x["id"]):
        title = a.get("title") or ""
        body = a.get("contentText") or ""
        if has(title, REG_TITLE) and not has(title, NOISE) and len(body) >= 200:
            if pa_reg[a["author"]] < CAP:
                pa_reg[a["author"]] += 1; reg.append(to_record(a, "regulation")); seen_ids.add(a["id"])
    # ka: KA brand in TITLE + ingredient term present, no noise
    for a in sorted(arts, key=lambda x: x["id"]):
        if a["id"] in seen_ids:
            continue
        title = a.get("title") or ""
        body = a.get("contentText") or ""
        if has(title, KA) and has(title + " " + body, ING) and not has(title, NOISE) and len(body) >= 200:
            if pa_ka[a["author"]] < CAP:
                pa_ka[a["author"]] += 1; ka.append(to_record(a, "ka_watch")); seen_ids.add(a["id"])

    out = reg + ka
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"regulation 候选: {len(reg)}   ka_watch 候选: {len(ka)}   合计 {len(out)}")
    print("\n[regulation] 标题:")
    for r in reg:
        print(f"  - {r['title'][:46]}  | {r['source_name']}")
    print("\n[ka_watch] 标题:")
    for r in ka:
        print(f"  - {r['title'][:46]}  | {r['source_name']}")


if __name__ == "__main__":
    main()
