#!/usr/bin/env python3
"""Round-3 scoring: Group A (section only) vs Group B (section + open tags), Opus 4.8.

Gold = pilot-30-gold-v4.json (model silver). Computes: section accuracy each vs gold,
A-vs-B agreement, relevance, report_guidance usage, B tag stats + open-vocab fragmentation,
output-size cost proxy.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
B = ROOT / "product/output/test-results/section-tagging-test"


def load(p):
    d = json.loads((B / p).read_text())
    items = d if isinstance(d, list) else d.get("articles", [])
    return {x["article_id"]: x for x in items}


def prim(x):
    return (x.get("section") or {}).get("primary_section")


def sec(x):
    return (x.get("section") or {}).get("secondary_sections") or []


A = load("runs/A-opus48-v4.json")
Bg = load("runs/B-opus48-v4.json")
gold = {g["article_id"]: g for g in json.loads((B / "gold-standard/pilot-30-gold-v4.json").read_text())["articles"]}
inp = {r["article_id"]: r for r in json.loads((B / "fixtures/pilot-30-input-v3.json").read_text())}
ids = [i for i in inp if i in A and i in Bg and i in gold]
n = len(ids)

print("=" * 66)
print(f"ROUND 3  Group A (section only) vs Group B (section+open tags)  n={n}")
print("(gold = V4 model silver; Opus is both tagger and gold author → 自洽性, not 真值)")
print("=" * 66)

# section accuracy vs gold
accA = sum(1 for i in ids if prim(A[i]) == gold[i]["gold_primary_v4"])
accB = sum(1 for i in ids if prim(Bg[i]) == gold[i]["gold_primary_v4"])
top2A = sum(1 for i in ids if gold[i]["gold_primary_v4"] in [prim(A[i])] + sec(A[i]))
top2B = sum(1 for i in ids if gold[i]["gold_primary_v4"] in [prim(Bg[i])] + sec(Bg[i]))
print(f"\n## primary_section accuracy vs V4 gold (Goal 1 — 标签是否拖累栏目)")
print(f"  A (仅判栏目)      {accA}/{n} = {accA/n:.0%}   top-2 {top2A/n:.0%}")
print(f"  B (栏目+开放标签) {accB}/{n} = {accB/n:.0%}   top-2 {top2B/n:.0%}")
print(f"  → 差异 {abs(accA-accB)} 篇（<3 篇视为无显著差异）")

# A vs B agreement
agree = sum(1 for i in ids if prim(A[i]) == prim(Bg[i]))
print(f"\n## A vs B 主栏目一致 {agree}/{n} = {agree/n:.0%}")
disagree = [(i, prim(A[i]), prim(Bg[i])) for i in ids if prim(A[i]) != prim(Bg[i])]
for i, pa, pb in disagree:
    g = gold[i]["gold_primary_v4"]
    print(f"   - {i[:12]:<12} A={pa:<22} B={pb:<22} gold={g:<22} {inp[i]['source_name']}")

# relevance
relA = sum(1 for i in ids if A[i].get("relevance") == gold[i]["gold_relevance"])
relB = sum(1 for i in ids if Bg[i].get("relevance") == gold[i]["gold_relevance"])
print(f"\n## relevance vs gold:  A {relA}/{n}={relA/n:.0%}   B {relB}/{n}={relB/n:.0%}")
# wrongly dropped (gold relevant but excluded)
def wrong_drop(run):
    return sum(1 for i in ids if gold[i]["gold_relevance"] == "relevant" and run[i].get("relevance") == "not_relevant")
print(f"   错杀有用(贵): A {wrong_drop(A)}  B {wrong_drop(Bg)}")

# needs_review / quarantine
qA = sum(1 for i in ids if prim(A[i]) == "needs_review")
qB = sum(1 for i in ids if prim(Bg[i]) == "needs_review")
print(f"\n## 隔离(needs_review)率:  A {qA}/{n}  B {qB}/{n}  (应很低)")

# report_guidance usage
rgA = sum(1 for i in ids if A[i].get("report_guidance"))
rgB = sum(1 for i in ids if Bg[i].get("report_guidance"))
print(f"\n## report_guidance 使用(可选,应低): A {rgA}/{n}  B {rgB}/{n}")

# section distribution
print(f"\n## primary_section 分布")
da, db, dg = Counter(prim(A[i]) for i in ids), Counter(prim(Bg[i]) for i in ids), Counter(gold[i]["gold_primary_v4"] for i in ids)
labs = sorted(set(da)|set(db)|set(dg), key=lambda x:-(dg[x]))
print(f"  {'section':<24} gold  A   B")
for l in labs:
    print(f"  {str(l):<24} {dg[l]:>3} {da[l]:>3} {db[l]:>3}")

# B tag stats + open-vocab fragmentation
print(f"\n## B 开放标签情况 (Goal 2)")
ing = Counter()
roles = Counter()
ntags = 0
for i in ids:
    t = Bg[i].get("tags") or {}
    for v in t.get("ingredient_technology", []):
        ing[v] += 1
    for v in t.get("entity_role", []):
        roles[v] += 1
    ntags += sum(len(t.get(f, [])) for f in ("primary_story_type","ingredient_technology","functional_claim","product_application"))
print(f"  平均标签/篇(4字段): {ntags/n:.1f}")
print(f"  ingredient_technology 去重后 {len(ing)} 个不同值(开放词碎片化观察); 高频: {dict(ing.most_common(8))}")
print(f"  entity_role 取值分布: {dict(roles)}")

# output size proxy
def avgchars(run):
    return sum(len(json.dumps(run[i], ensure_ascii=False)) for i in ids)/n
print(f"\n## 输出体量(字符/篇, 成本代理):  A {avgchars(A):.0f}   B {avgchars(Bg):.0f}")
