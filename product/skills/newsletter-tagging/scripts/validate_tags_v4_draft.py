#!/usr/bin/env python3
"""Validate Croda Beauty newsletter-tagging V4 (DRAFT, 2026-06-17) output + metrics.

V4 final: AI outputs ONLY relevance + section.sections (flat EQUAL multi-label) + evidence
(+ optional report_guidance). NO descriptive tags (those are script-generated on the article
record). Sections equal, no primary/secondary. exclude/needs_review are mutually-exclusive
system states (sections must be exactly [exclude] / [needs_review]). No confidence.
Evidence = trigger_span_id pointer; pass --article to cross-check ids exist in spans.

Usage:
    python3 validate_tags_v4_draft.py out.json --article 待打标.json
    python3 validate_tags_v4_draft.py out.json --metrics-json
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

SCHEMA_VERSION = "newsletter-tagging/croda-beauty-v4"
FORMAL = {"competitor_watch", "ingredient_innovation", "ka_watch", "market_event", "regulation_policy"}
SECTION_LABELS = FORMAL | {"exclude", "needs_review"}
REQUIRED_TOP = {"schema_version", "article_id", "relevance", "tagging_decision", "section", "review_reasons", "tag_audit"}
TOP_FIELDS = REQUIRED_TOP | {"url", "source_key", "source_name", "report_guidance"}
RELEVANCE = {"relevant", "not_relevant", "unclear"}
DECISIONS = {"tagged", "excluded", "needs_review"}
REVIEW_REASONS = {"insufficient_content", "title_body_conflict", "ambiguous_relevance", "human_requested"}
# descriptive tags must NOT appear in AI output (script-generated, not here)
BANNED_TOP = {"tags", "evidence_records", "suggested_new_tags", "company", "ingredient_mentions",
              "ingredient_technology", "functional_claim", "product_application", "primary_story_type",
              "value_chain_stage", "entity_role", "is_event", "event_type"}
SPAN_RE = re.compile(r"^s[0-9]+$")
CONF_RE = re.compile(r"confidence", re.IGNORECASE)


def find_conf(o, path=""):
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and CONF_RE.search(k):
                hits.append(f"{path}.{k}".lstrip("."))
            hits += find_conf(v, f"{path}.{k}".lstrip("."))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            hits += find_conf(v, f"{path}[{i}]")
    return hits


def chk_span(v, where, prefix, errors, valid):
    if not isinstance(v, str) or not SPAN_RE.match(v):
        errors.append(f"{prefix}.{where} must be a span id like 's3'; got {v!r}")
        return
    if valid is not None and v not in valid:
        errors.append(f"{prefix}.{where} cites {v!r} not in article spans")


def validate_item(item, idx, spans_by_id):
    p = f"[{idx}]"
    errors, warnings = [], []
    if not isinstance(item, dict):
        return [f"{p} not an object"], warnings
    for k in find_conf(item):
        errors.append(f"{p} confidence is banned in V4 (key: {k})")
    for f in sorted(set(item) & BANNED_TOP):
        errors.append(f"{p} field '{f}' must NOT be in AI output (script-generated / removed in V4)")
    for f in sorted(set(item) - TOP_FIELDS - BANNED_TOP):
        errors.append(f"{p} unknown top-level field: {f}")
    for f in sorted(REQUIRED_TOP - set(item)):
        errors.append(f"{p} missing top-level: {f}")

    if item.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{p} schema_version must be {SCHEMA_VERSION}")
    aid = item.get("article_id")
    if not isinstance(aid, str) or not aid:
        errors.append(f"{p} article_id must be non-empty string")
    if item.get("relevance") not in RELEVANCE:
        errors.append(f"{p} relevance invalid: {item.get('relevance')!r}")
    decision = item.get("tagging_decision")
    if decision not in DECISIONS:
        errors.append(f"{p} tagging_decision invalid: {decision!r}")
    rg = item.get("report_guidance")
    if rg is not None and (not isinstance(rg, str) or not rg.strip()):
        errors.append(f"{p} report_guidance must be a non-empty string when present")

    valid = spans_by_id.get(aid) if spans_by_id is not None else None
    if spans_by_id is not None and isinstance(aid, str) and aid not in spans_by_id:
        warnings.append(f"{p} no spans for {aid}; span ids unchecked")

    sec = item.get("section")
    sections = []
    if not isinstance(sec, dict):
        errors.append(f"{p}.section must be an object")
    else:
        for k in ("sections", "evidence"):
            if k not in sec:
                errors.append(f"{p}.section missing {k}")
        sections = sec.get("sections")
        if not isinstance(sections, list) or not sections:
            errors.append(f"{p}.section.sections must be a non-empty array")
            sections = []
        else:
            if len(sections) != len(set(sections)):
                errors.append(f"{p}.section.sections has duplicates")
            for s in sections:
                if s not in SECTION_LABELS:
                    errors.append(f"{p}.section.sections invalid label: {s!r}")
            # exclude/needs_review must be alone
            if ("exclude" in sections or "needs_review" in sections) and len(sections) > 1:
                errors.append(f"{p}.section.sections: exclude/needs_review must appear alone, not mixed with formal sections")
        ev = sec.get("evidence")
        if not isinstance(ev, list) or not ev:
            errors.append(f"{p}.section.evidence must be a non-empty array")
        else:
            ev_sections = set()
            for j, e in enumerate(ev):
                ep = f"{p}.section.evidence[{j}]"
                if not isinstance(e, dict):
                    errors.append(f"{ep} must be object"); continue
                es = e.get("section")
                if es not in SECTION_LABELS:
                    errors.append(f"{ep}.section invalid: {es!r}")
                else:
                    ev_sections.add(es)
                    if sections and es not in sections:
                        errors.append(f"{ep}.section {es!r} not in section.sections")
                chk_span(e.get("trigger_span_id"), "trigger_span_id", ep, errors, valid)
                ib = e.get("inferred_because")
                if not isinstance(ib, str) or not ib.strip():
                    errors.append(f"{ep}.inferred_because must be non-empty")
                elif len(ib) > 60:
                    errors.append(f"{ep}.inferred_because must be <=60 chars")
                if "evidence_text" in e:
                    errors.append(f"{ep} uses evidence_text; V4 wants trigger_span_id pointer")
            # every section should have >=1 evidence
            for s in sections:
                if s not in ev_sections:
                    warnings.append(f"{p} section {s} has no evidence entry")

    # decision <-> sections consistency
    rr = item.get("review_reasons") if isinstance(item.get("review_reasons"), list) else []
    if decision == "tagged":
        if any(s not in FORMAL for s in sections):
            errors.append(f"{p} tagged requires all sections to be formal (no exclude/needs_review)")
    elif decision == "excluded":
        if sections != ["exclude"]:
            errors.append(f"{p} excluded requires sections == ['exclude']")
        if item.get("relevance") == "relevant":
            warnings.append(f"{p} excluded but relevance=relevant (check)")
    elif decision == "needs_review":
        if sections != ["needs_review"]:
            errors.append(f"{p} needs_review requires sections == ['needs_review']")
        if not rr:
            errors.append(f"{p} needs_review requires review_reasons")
    if item.get("relevance") == "not_relevant" and decision != "excluded":
        errors.append(f"{p} relevance=not_relevant requires tagging_decision=excluded")

    ta = item.get("tag_audit")
    if not isinstance(ta, dict):
        errors.append(f"{p} tag_audit must be object")
    else:
        for k in ("tagger", "tagged_at", "dictionary_version", "prompt_version"):
            if k not in ta:
                errors.append(f"{p} tag_audit missing {k}")
    return errors, warnings


def load_spans(path):
    payload = json.loads(Path(path).read_text())
    recs = payload["articles"] if isinstance(payload, dict) and "articles" in payload else (payload if isinstance(payload, list) else [payload])
    out = {}
    for r in recs:
        if isinstance(r, dict):
            aid = r.get("article_id") or r.get("id")
            sp = r.get("spans")
            out[aid] = {s["id"] for s in sp if isinstance(s, dict) and "id" in s} if isinstance(sp, list) else set()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--article")
    ap.add_argument("--metrics-json", action="store_true")
    a = ap.parse_args()
    try:
        payload = json.loads(Path(a.json_path).read_text())
    except Exception as exc:
        print(f"ERROR: load failed: {exc}", file=sys.stderr); return 2
    spans = load_spans(a.article) if a.article else None
    items = payload if isinstance(payload, list) else [payload]
    errors, warnings = [], []
    for i, it in enumerate(items):
        e, w = validate_item(it, i, spans)
        errors += e; warnings += w
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if a.metrics_json:
        # section frequency (multi-label → count each membership)
        freq = Counter()
        multi = 0
        for it in items:
            if isinstance(it, dict) and isinstance(it.get("section"), dict):
                ss = it["section"].get("sections") or []
                freq.update(ss)
                if len([s for s in ss if s in FORMAL]) > 1:
                    multi += 1
        rg = sum(1 for it in items if isinstance(it, dict) and it.get("report_guidance"))
        print(json.dumps({"n": len(items), "section_membership_freq": dict(freq),
                          "multi_section_articles": multi, "report_guidance_used": rg,
                          "schema_failed": bool(errors)}, ensure_ascii=False, indent=2))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(items)} V4 result(s)" + ("" if spans is not None else " (spans NOT checked)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
