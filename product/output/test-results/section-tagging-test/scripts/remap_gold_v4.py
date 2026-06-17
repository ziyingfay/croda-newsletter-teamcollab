#!/usr/bin/env python3
"""Remap Fable V3 gold to V4 section labels. 26 deterministic + boundary overrides.

V4 has 5 formal sections (industry_brief/热点 is report-agent composed, NOT a tagging label).
4 boundary articles re-judged by Opus 4.8 under V4; 2 roundups remapped to dominant section.
Output: gold-standard/pilot-30-gold-v4.json.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ANN = ROOT / "product/output/test-results/section-tagging-test/gold-standard/pilot-30-annotations.json"
OUT = ROOT / "product/output/test-results/section-tagging-test/gold-standard/pilot-30-gold-v4.json"

REMAP = {
    "technology_innovation": "ingredient_innovation",
    "ingredient_trend": "ingredient_innovation",
    "market_brief": "competitor_watch",  # 兜底；两篇在 ROUNDUP 显式覆盖
    "competitor_watch": "competitor_watch",
    "market_event": "market_event",
    "customer_watch": "ka_watch",
    "exclude": "exclude",
    "needs_review": "needs_review",
}

OPUS_V4 = {
    "XGItt9v6lEIzSYsQmpdhOw": {"primary": "ingredient_innovation", "secondary": ["regulation_policy", "market_event"], "relevance": "relevant",
        "reason": "借4月新原料备案数据解读成分创新趋势；备案为数据底座、SIC大会为尾巴"},
    "fGhwLgCP5oKEOFag0nCouA": {"primary": "ka_watch", "secondary": ["ingredient_innovation", "market_event"], "relevance": "relevant",
        "reason": "下游KA品牌HBN自研抗光老机制与美白复配，涉成分/机制/功效；AAD/SID只是发布场合"},
    "GiSW9lV2lO8p0aUpl7n1rA": {"primary": "exclude", "secondary": [], "relevance": "not_relevant",
        "reason": "渠道/支付监管，无任何原料成分角度，对禾大原料情报无价值"},
    "uEyFfOCHTlZvY-vpSfvz4g": {"primary": "ingredient_innovation", "secondary": ["ka_watch"], "relevance": "relevant",
        "reason": "实质是肌肤长寿前沿技术与新成分趋势/竞品布局；MNC品牌只是承载视角"},
}
ROUNDUP = {
    "C8LlcoNo8dZo_hC3nPi9lw": {"primary": "competitor_watch", "secondary": ["ka_watch"], "relevance": "relevant",
        "reason": "多事件汇编,主导实质=华熙生物原料(PDRN/重组胶原)产能→competitor_watch;行业快讯由报告Agent编排"},
    "-mklrri45Os44-kdHmXpEg": {"primary": "competitor_watch", "secondary": [], "relevance": "relevant",
        "reason": "多事件汇编,主导实质=巴斯夫换帅/格林生物IPO等竞品动态→competitor_watch;行业快讯由报告Agent编排"},
}


def main():
    arts = json.loads(ANN.read_text())["articles"]
    overrides = {**OPUS_V4, **ROUNDUP}
    out = []
    changed = 0
    for a in arts:
        aid = a["id"]
        if aid in overrides:
            o = overrides[aid]
            det = REMAP.get(a["gold_primary"], a["gold_primary"])
            if o["primary"] != det:
                changed += 1
            out.append({"article_id": aid, "i": a["i"], "source": a["source"],
                        "gold_primary_v4": o["primary"], "gold_secondary_v4": o["secondary"],
                        "gold_relevance": o["relevance"],
                        "source_label": "opus48_v4_rejudge" if aid in OPUS_V4 else "roundup_remap",
                        "note": o["reason"], "v3_primary": a["gold_primary"]})
        else:
            out.append({"article_id": aid, "i": a["i"], "source": a["source"],
                        "gold_primary_v4": REMAP.get(a["gold_primary"], a["gold_primary"]),
                        "gold_secondary_v4": [REMAP.get(s, s) for s in a["gold_secondary"]],
                        "gold_relevance": a["gold_relevance"], "source_label": "deterministic_remap",
                        "note": a.get("note", ""), "v3_primary": a["gold_primary"]})
    OUT.write_text(json.dumps({"_about": "V4-remapped gold (model-authored silver, NOT human-verified).",
                               "articles": out}, ensure_ascii=False, indent=2))
    print(f"wrote {OUT.name} ({len(out)} articles; {changed} primary changed by override)")
    print("V4 gold primary dist:", dict(Counter(r["gold_primary_v4"] for r in out)))


if __name__ == "__main__":
    main()
