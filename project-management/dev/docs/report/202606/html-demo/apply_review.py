#!/usr/bin/env python3
"""Apply a human-review file to report_content.json (demo reference).

The internal HTML exports a review file (croda-report-review/v1) whose
`suggestions[]` each carry an `edit_type`:

  - delete   : remove the referenced item.                 (deterministic, no AI)
  - replace  : write `value` straight into the target field. (deterministic, no AI)
  - instruct : a semantic comment to be rewritten by the report Agent. (needs AI)

This script applies the two deterministic types directly to a copy of
report_content.json and lists the `instruct` items for the AI Agent to handle.
It never overwrites the source: output goes to <report>.reviewed.json.

Usage:
    python3 apply_review.py review_202606_YYYYMMDD.json [report_content.json] [-o out.json]
"""
import argparse
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"), object_pairs_hook=collections.OrderedDict)


def find_item(data, ref_id):
    for sec in data.get("sections", []):
        for it in sec.get("items", []):
            if it.get("item_id") == ref_id:
                return sec, it
    return None, None


def find_kpi(data, ref_id):
    for k in data.get("kpis", []):
        if k.get("kpi_id") == ref_id:
            return k
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("review")
    ap.add_argument("report", nargs="?", default=str(HERE / "report_content.json"))
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    review = load(args.review)
    data = load(args.report)
    out = Path(args.out) if args.out else Path(args.report).with_suffix(".reviewed.json")

    applied, pending = [], []   # pending = needs the AI Agent

    for s in review.get("suggestions", []):
        et = s.get("edit_type")
        ref = s.get("ref_id")
        rt = s.get("ref_type")
        title = s.get("title", ref)

        if et == "delete":
            if rt == "item":
                sec, it = find_item(data, ref)
                if it:
                    sec["items"].remove(it)
                    applied.append(("delete", title, "item removed"))
                    continue
            pending.append(("delete", title, "target not found / not an item"))

        elif et == "replace":
            field, scope = s.get("field"), s.get("lang_scope", "both")
            vlang = s.get("value_lang") or "zh"
            val = s.get("value", "")
            if rt == "kpi" and field == "value":
                k = find_kpi(data, ref)
                if k:
                    k["value"] = val
                    applied.append(("replace", title, "kpi.value updated"))
                    continue
            elif rt == "item" and field == "summary":
                _, it = find_item(data, ref)
                if it:
                    it.setdefault("summary", collections.OrderedDict())[vlang] = val
                    note = "summary." + vlang + " replaced"
                    applied.append(("replace", title, note))
                    if scope == "both":
                        other = "en" if vlang == "zh" else "zh"
                        pending.append(("translate", title, "summary." + other + " needs AI translation"))
                    continue
            # structured fields (analysis) or anything we can't map deterministically
            pending.append(("replace", title, "field '%s' needs AI to apply" % field))

        else:  # instruct
            pending.append(("instruct", title, s.get("instruction", "")))

    # Manual tags and 其他-X resolutions are review-record only: they are NOT applied
    # to report_content.json and never written to any backend tag/dictionary config
    # (PRD §3/§4/§5). They are kept for later human-driven dictionary iteration.
    manual_tags = review.get("manual_tags", [])
    other_res = review.get("other_resolutions", [])

    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Review: %s" % args.review)
    print("Report: %s  ->  %s" % (args.report, out.name))
    print("\n== Applied directly (no AI): %d ==" % len(applied))
    for kind, title, note in applied:
        print("  [%s] %s — %s" % (kind, title, note))
    print("\n== Routed to AI Agent: %d ==" % len(pending))
    for kind, title, note in pending:
        print("  [%s] %s — %s" % (kind, title, note))

    mt = sum(len(m.get("tags", [])) for m in manual_tags)
    print("\n== Recorded only (NOT applied; no dictionary/backend writes): %d ==" % (mt + len(other_res)))
    for m in manual_tags:
        for tg in m.get("tags", []):
            star = " [suggest-dict]" if tg.get("suggest_dict") else ""
            print("  [manual-tag] %s — %s%s" % (m.get("title"), tg.get("text"), star))
    for o in other_res:
        star = " [suggest-dict]" if o.get("suggest_dict") else ""
        detail = o.get("specify") or o.get("action")
        print("  [pending] %s — %s -> %s%s" % (o.get("title"), o.get("placeholder"), detail, star))
    print("  (kept for later human-driven dictionary iteration; see review-edits record)")

    print("\nNext: re-run `python3 render_report.py` on the reviewed JSON after the "
          "AI Agent resolves the routed items.")


if __name__ == "__main__":
    main()
