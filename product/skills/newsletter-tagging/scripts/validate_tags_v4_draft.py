#!/usr/bin/env python3
"""Validate Croda Beauty newsletter-tagging V4 (DRAFT) output + batch metrics.

V4 (croda-beauty-2026-06-12-v4-draft). Differences vs V3 validator:
- 5 formal sections: competitor_watch / ingredient_innovation / ka_watch / market_event /
  regulation_policy (+ exclude / needs_review). NO industry_brief/market_brief (report-agent
  composed downstream), NO ingredient_trend/technology_innovation/customer_watch.
- optional `report_guidance` (single string).
- group B emits open-vocabulary tags + entity_role; pass --open-tags to skip picklist
  enforcement on tag values (structure/spans/no-confidence still checked).
- evidence = trigger_span_id pointers; no confidence anywhere; event_news banned in story_type.

Usage:
    python3 validate_tags_v4_draft.py out.json --article pilot-30-input-v3.json            # group A
    python3 validate_tags_v4_draft.py out.json --article pilot-30-input-v3.json --open-tags # group B
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "newsletter-tagging/croda-beauty-v4"
OPEN_FIELDS = {"ingredient_technology", "product_application", "functional_claim"}
SECTION_FORMAL = {"competitor_watch", "ingredient_innovation", "ka_watch", "market_event", "regulation_policy"}
SECTION_LABELS = SECTION_FORMAL | {"exclude", "needs_review"}

ALLOWED = {
    "primary_story_type": {"corporate_move", "product_launch_or_update", "technology_process_innovation",
                            "research_science", "regulation_policy", "market_consumer_insight", "other"},
    "product_application": {"skincare", "sun_care", "hair_care", "body_personal_care", "baby_care",
                             "teen_age_care", "men_care", "fragrance_perfume"},
    "ingredient_technology": {"peptides", "pdrn_nucleotides", "ceramides", "retinoids", "retinol_alternatives",
                               "recombinant_collagen", "hyaluronic_acid", "niacinamide", "vitamin_c",
                               "probiotics_postbiotics", "exosomes", "growth_factors", "plant_botanical_extracts",
                               "marine_blue_biotech_actives", "ergothioneine", "longevity_telomere_actives",
                               "acids_exfoliants", "base_functional_raw", "encapsulation_delivery", "sustained_release",
                               "synthetic_biology", "fermentation_biotech", "sustainability_chemistry",
                               "ai_rd_formulation", "neurocosmetics_tech", "dual_targeting_delivery",
                               "microfluidics", "stem_cell"},
    "functional_claim": {"anti_aging", "whitening_brightening", "moisturizing", "barrier_repair",
                          "soothing_sensitive_skin", "acne_oil_control", "sun_protection", "firming_lifting",
                          "microbiome_balance", "hair_scalp_care", "hair_strands", "enhance_penetration",
                          "emotion_wellbeing", "anti_glycation", "blue_light_protection", "anti_pollution"},
}
ARRAY_TAG_FIELDS = {"primary_story_type", "product_application", "ingredient_technology", "functional_claim", "entity_role"}
SINGLE_TAG_FIELDS = {"value_chain_stage"}
TAG_FIELDS = ARRAY_TAG_FIELDS | SINGLE_TAG_FIELDS
SCRIPT_FIELDS_FORBIDDEN_IN_TAGS = {"company", "is_event", "event_type", "ingredient_mentions"}

REQUIRED_TOP = {"schema_version", "article_id", "relevance", "tagging_decision", "section",
                "evidence_records", "suggested_new_tags", "review_reasons", "tag_audit"}
TOP_FIELDS = REQUIRED_TOP | {"url", "source_key", "source_name", "tags", "report_guidance"}
RELEVANCE = {"relevant", "not_relevant", "unclear"}
DECISIONS = {"tagged", "excluded", "no_matching_tag", "needs_review"}
REVIEW_REASONS = {"insufficient_content", "title_body_conflict", "ambiguous_relevance",
                  "suggested_new_taxonomy_label", "no_matching_closed_label", "human_requested"}
OTHER_RE = re.compile(r"^other:[a-z0-9_]+$")
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
        errors.append(f"{prefix}.{where} must be a span id like 's3'; got {v!r}"); return
    if valid is not None and v not in valid:
        errors.append(f"{prefix}.{where} cites {v!r} not in article spans")


def validate_item(item, idx, spans_by_id, open_tags):
    p = f"[{idx}]"; errors = []; warnings = []
    if not isinstance(item, dict):
        return [f"{p} not an object"], warnings
    for k in find_conf(item):
        errors.append(f"{p} confidence is banned in V4 (key: {k})")
    for f in sorted(set(item) - TOP_FIELDS):
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

    # section
    sec = item.get("section")
    primary = None
    if not isinstance(sec, dict):
        errors.append(f"{p}.section must be an object")
    else:
        for k in ("primary_section", "secondary_sections", "evidence"):
            if k not in sec:
                errors.append(f"{p}.section missing {k}")
        primary = sec.get("primary_section")
        if primary not in SECTION_LABELS:
            errors.append(f"{p}.section.primary_section invalid: {primary!r}")
        secs = sec.get("secondary_sections")
        if not isinstance(secs, list):
            errors.append(f"{p}.section.secondary_sections must be array")
        else:
            for s in secs:
                if s not in SECTION_FORMAL:
                    errors.append(f"{p}.section.secondary_sections invalid: {s!r} (only 5 formal; no exclude/needs_review/brief)")
            if primary in secs:
                errors.append(f"{p}.section.secondary_sections repeats primary")
        ev = sec.get("evidence")
        if not isinstance(ev, dict):
            errors.append(f"{p}.section.evidence must be object")
        else:
            chk_span(ev.get("trigger_span_id"), "section.evidence.trigger_span_id", p, errors, valid)
            ib = ev.get("inferred_because")
            if not isinstance(ib, str) or not ib.strip():
                errors.append(f"{p}.section.evidence.inferred_because must be non-empty")
            elif len(ib) > 60:
                errors.append(f"{p}.section.evidence.inferred_because must be <=60 chars")

    # review reasons / decision-section consistency
    rr = item.get("review_reasons")
    rr = rr if isinstance(rr, list) else []
    if decision == "needs_review":
        if primary != "needs_review":
            errors.append(f"{p} needs_review decision requires section.primary_section=needs_review")
        if not rr:
            errors.append(f"{p} needs_review requires review_reasons")
    if decision == "excluded" and primary != "exclude":
        errors.append(f"{p} excluded decision requires section.primary_section=exclude")
    if decision == "no_matching_tag" and not rr:
        errors.append(f"{p} no_matching_tag requires review_reasons")
    if item.get("relevance") == "not_relevant" and decision != "excluded":
        errors.append(f"{p} relevance=not_relevant requires tagging_decision=excluded")
    if decision == "tagged" and primary not in SECTION_FORMAL:
        errors.append(f"{p} tagged requires a formal primary_section, got {primary!r}")

    # evidence_records
    ev_keys = set()
    evr = item.get("evidence_records")
    if not isinstance(evr, list):
        errors.append(f"{p}.evidence_records must be array")
    else:
        for i, e in enumerate(evr):
            ep = f"{p}.evidence_records[{i}]"
            if not isinstance(e, dict):
                errors.append(f"{ep} must be object"); continue
            for k in ("field", "label", "trigger_span_id"):
                if k not in e:
                    errors.append(f"{ep} missing {k}")
            if "evidence_text" in e:
                errors.append(f"{ep} uses evidence_text; V4 wants trigger_span_id pointer")
            if isinstance(e.get("field"), str) and isinstance(e.get("label"), str):
                ev_keys.add((e["field"], e["label"]))
            chk_span(e.get("trigger_span_id"), "trigger_span_id", ep, errors, valid)

    # tags
    tags = item.get("tags")
    if decision == "tagged":
        if not isinstance(tags, dict):
            if not open_tags:  # group A: tags omitted is fine
                pass
            else:
                errors.append(f"{p} group B tagged should include tags")
            tags = {}
        for f in sorted(set(tags) - TAG_FIELDS):
            if f in SCRIPT_FIELDS_FORBIDDEN_IN_TAGS:
                errors.append(f"{p} tags.{f} is a SCRIPT field; must not be emitted")
            else:
                errors.append(f"{p} tags unknown field: {f}")
        for f in ARRAY_TAG_FIELDS & set(tags):
            v = tags[f]
            if not isinstance(v, list):
                errors.append(f"{p}.tags.{f} must be array"); continue
            if f == "primary_story_type" and len(v) < 1:
                errors.append(f"{p}.tags.primary_story_type needs >=1")
            for lab in v:
                if not isinstance(lab, str):
                    errors.append(f"{p}.tags.{f} non-string label"); continue
                if open_tags or f == "entity_role":
                    continue  # group B open-vocab: skip picklist
                if f in OPEN_FIELDS and OTHER_RE.match(lab):
                    continue
                if f in ALLOWED and lab not in ALLOWED[f]:
                    errors.append(f"{p}.tags.{f} invalid label: {lab!r}")
        # in group B, every story_type/tag label should have an evidence pointer
        if open_tags:
            for f in ("primary_story_type",):
                for lab in tags.get(f, []):
                    if (f, lab) not in ev_keys:
                        warnings.append(f"{p} tag {f}={lab} has no evidence pointer")
    elif isinstance(tags, dict):
        for f in SCRIPT_FIELDS_FORBIDDEN_IN_TAGS & set(tags):
            errors.append(f"{p} tags.{f} is a SCRIPT field; must not be emitted")

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
    ap.add_argument("--open-tags", action="store_true", help="group B: allow open-vocab tag values")
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
        e, w = validate_item(it, i, spans, a.open_tags)
        errors += e; warnings += w
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if a.metrics_json:
        dist = Counter((it.get("section") or {}).get("primary_section") for it in items if isinstance(it, dict))
        rg = sum(1 for it in items if isinstance(it, dict) and it.get("report_guidance"))
        print(json.dumps({"n": len(items), "section_distribution": dict(dist), "report_guidance_used": rg,
                          "schema_failed": bool(errors)}, ensure_ascii=False, indent=2))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(items)} V4 result(s)" + ("" if spans is not None else " (spans NOT checked)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
