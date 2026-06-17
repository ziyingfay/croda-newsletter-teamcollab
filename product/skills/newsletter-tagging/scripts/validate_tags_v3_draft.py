#!/usr/bin/env python3
"""Validate Croda Beauty newsletter-tagging V3/V4 (DRAFT) output and print batch metrics.

V3/V4 taxonomy (croda-beauty-2026-06-11-v3-draft + V4 section update).
Differences vs V2 validator:

- `section` is a required, first-class judgment object (primary_section + secondary +
  evidence). The section is NEVER derived from tags.
- Industry flash / hot news is NOT a tagging section. The report Agent selects up to
  10 highlight items from the five formal content sections.
- Evidence is a `trigger_span_id` POINTER into the article's script-provided `spans`,
  not a transcribed `evidence_text`. Pass the input article package via `--article` to
  cross-check that every cited span id actually exists in that article's `spans`.
- NO confidence score anywhere (rejected if present); quality is assured by human
  spot-check sampling. `needs_review` is an objective state, kept consistent with
  `tagging_decision`.
- `event_news` removed from `primary_story_type` (the occasion is the script field
  `is_event`/`event_type`). `company` is a script field and must NOT appear in `tags`.
- `value_chain_stage` may be null (phase 2).

Usage:
    python3 validate_tags_v3_draft.py output.json
    python3 validate_tags_v3_draft.py output.json --article 待打标.json   # enables span-id checks
    python3 validate_tags_v3_draft.py output.json --metrics-json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "newsletter-tagging/croda-beauty-v3"

OPEN_FIELDS = {"ingredient_technology", "product_application", "functional_claim"}

SECTION_LABELS = {
    "competitor_watch",
    "ingredient_innovation",
    "ka_watch",
    "market_event",
    "regulation_policy",
    "exclude",
    "needs_review",
}
CONTENT_SECTIONS = {
    "competitor_watch",
    "ingredient_innovation",
    "ka_watch",
    "market_event",
    "regulation_policy",
}

ALLOWED = {
    "primary_story_type": {
        "corporate_move",
        "product_launch_or_update",
        "technology_process_innovation",
        "research_science",
        "regulation_policy",
        "market_consumer_insight",
        "other",
        # NOTE: event_news intentionally removed in V3 (occasion -> script is_event)
    },
    "product_application": {
        "skincare", "sun_care", "hair_care", "body_personal_care", "baby_care",
        "teen_age_care", "men_care", "fragrance_perfume",
    },
    "ingredient_technology": {
        "peptides", "pdrn_nucleotides", "ceramides", "retinoids", "retinol_alternatives",
        "recombinant_collagen", "hyaluronic_acid", "niacinamide", "vitamin_c",
        "probiotics_postbiotics", "exosomes", "growth_factors", "plant_botanical_extracts",
        "marine_blue_biotech_actives", "ergothioneine", "longevity_telomere_actives",
        "acids_exfoliants", "base_functional_raw", "encapsulation_delivery",
        "sustained_release", "synthetic_biology", "fermentation_biotech", "sustainability_chemistry",
        "ai_rd_formulation", "neurocosmetics_tech", "dual_targeting_delivery",
        "microfluidics", "stem_cell",
    },
    "functional_claim": {
        "anti_aging", "whitening_brightening", "moisturizing", "barrier_repair",
        "soothing_sensitive_skin", "acne_oil_control", "sun_protection", "firming_lifting",
        "microbiome_balance", "hair_scalp_care", "emotion_wellbeing", "anti_glycation",
        "blue_light_protection", "anti_pollution", "hair_strands", "enhance_penetration",
    },
    # V3 phase-2 coarse value chain (null allowed at MVP). Fine-grained V2 values still accepted.
    "value_chain_stage": {
        "upstream", "midstream", "downstream",
        "raw_material_upstream", "ingredient_active", "formulation_application",
        "manufacturing_contract", "packaging", "brand_finished_product",
        "distribution_channel", "consumer_market", "regulation_research",
        "cross_chain", "other",
    },
}

REQUIRED_TOP_LEVEL = {
    "schema_version", "article_id", "relevance", "tagging_decision", "section",
    "evidence_records", "suggested_new_tags", "review_reasons", "tag_audit",
}
TOP_LEVEL_FIELDS = REQUIRED_TOP_LEVEL | {"url", "source_key", "source_name", "tags"}

# `company` is a SCRIPT field in V3 and must not be re-emitted in tags.
SCRIPT_FIELDS_FORBIDDEN_IN_TAGS = {"company", "is_event", "event_type", "ingredient_mentions"}
ARRAY_TAG_FIELDS = {"primary_story_type", "product_application", "ingredient_technology", "functional_claim"}
SINGLE_TAG_FIELDS = {"value_chain_stage"}
TAG_FIELDS = ARRAY_TAG_FIELDS | SINGLE_TAG_FIELDS

RELEVANCE_VALUES = {"relevant", "not_relevant", "unclear"}
TAGGING_DECISIONS = {"tagged", "excluded", "no_matching_tag", "needs_review"}
REVIEW_REASONS = {
    "insufficient_content",
    "title_body_conflict",
    "ambiguous_relevance",
    "suggested_new_taxonomy_label",
    "no_matching_closed_label",
    "human_requested",
}
OTHER_RE = re.compile(r"^other:[a-z0-9_]+$")
SPAN_ID_RE = re.compile(r"^s[0-9]+$")
# any key containing 'confidence' is forbidden in V3
CONFIDENCE_RE = re.compile(r"confidence", re.IGNORECASE)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def is_allowed_label(field: str, label: str) -> bool:
    if field in OPEN_FIELDS and OTHER_RE.match(label):
        return True
    allowed = ALLOWED.get(field)
    return allowed is None or label in allowed


def find_confidence_keys(obj: Any, path: str = "") -> list[str]:
    """Recursively flag any 'confidence' key — banned in V3."""
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and CONFIDENCE_RE.search(k):
                hits.append(f"{path}.{k}".lstrip("."))
            hits.extend(find_confidence_keys(v, f"{path}.{k}".lstrip(".")))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(find_confidence_keys(v, f"{path}[{i}]"))
    return hits


def validate_string_list(item, key, allowed, prefix, errors, *, min_items=0):
    value = item.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}.{key} must be an array")
        return []
    if len(value) < min_items:
        errors.append(f"{prefix}.{key} must contain at least {min_items} item(s)")
    if len(value) != len(set(value)):
        errors.append(f"{prefix}.{key} must not contain duplicate values")
    labels = []
    for label in value:
        if not isinstance(label, str):
            errors.append(f"{prefix}.{key} contains a non-string label: {label!r}")
        elif allowed is not None and not is_allowed_label(key, label):
            errors.append(f"{prefix}.{key} has invalid label: {label!r}")
        else:
            labels.append(label)
    return labels


def validate_span_id(value, where, prefix, errors, valid_spans, span_refs):
    if not isinstance(value, str) or not SPAN_ID_RE.match(value):
        errors.append(f"{prefix}.{where} must be a span id like 's3'; got {value!r}")
        return
    span_refs.append(value)
    if valid_spans is not None and value not in valid_spans:
        errors.append(f"{prefix}.{where} cites {value!r} not present in the article's spans")


def validate_section(section, prefix, errors, valid_spans, span_refs):
    if not isinstance(section, dict):
        errors.append(f"{prefix}.section must be an object")
        return None
    for key in ("primary_section", "secondary_sections", "evidence"):
        if key not in section:
            errors.append(f"{prefix}.section missing {key}")
    for removed_key in ("is_market_brief_candidate", "is_customer_watch_candidate"):
        if removed_key in section:
            errors.append(
                f"{prefix}.section.{removed_key} was removed in V4; hot news is report-Agent "
                "curation and KA is represented by primary_section=ka_watch"
            )
    primary = section.get("primary_section")
    if primary not in SECTION_LABELS:
        errors.append(f"{prefix}.section.primary_section invalid: {primary!r}")
    secondary = section.get("secondary_sections")
    if not isinstance(secondary, list):
        errors.append(f"{prefix}.section.secondary_sections must be an array")
    else:
        for s in secondary:
            if s not in SECTION_LABELS:
                errors.append(f"{prefix}.section.secondary_sections has invalid label: {s!r}")
            if s in {"exclude", "needs_review"}:
                errors.append(f"{prefix}.section.secondary_sections must contain content sections only: {s!r}")
        if primary in secondary:
            errors.append(f"{prefix}.section.secondary_sections must not repeat primary_section")
    evidence = section.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{prefix}.section.evidence must be an object")
    else:
        validate_span_id(evidence.get("trigger_span_id"), "section.evidence.trigger_span_id",
                         prefix, errors, valid_spans, span_refs)
        because = evidence.get("inferred_because")
        if not isinstance(because, str) or not because.strip():
            errors.append(f"{prefix}.section.evidence.inferred_because must be a non-empty string")
        elif len(because) > 60:
            errors.append(f"{prefix}.section.evidence.inferred_because must be <=60 chars")
    return primary


def validate_evidence_records(value, prefix, errors, valid_spans, span_refs):
    keys: set[tuple[str, str]] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.evidence_records must be an array")
        return keys
    for i, ev in enumerate(value):
        ep = f"{prefix}.evidence_records[{i}]"
        if not isinstance(ev, dict):
            errors.append(f"{ep} must be an object")
            continue
        for key in ("field", "label", "trigger_span_id"):
            if key not in ev:
                errors.append(f"{ep} missing {key}")
        field, label = ev.get("field"), ev.get("label")
        if isinstance(field, str) and isinstance(label, str):
            keys.add((field, label))
        if field in OPEN_FIELDS and isinstance(label, str) and OTHER_RE.match(label):
            name = ev.get("extracted_name")
            if not isinstance(name, str) or not name:
                errors.append(f"{ep}.extracted_name is required for {label}")
        if "evidence_text" in ev:
            errors.append(f"{ep} uses evidence_text; V3 requires trigger_span_id pointer instead")
        validate_span_id(ev.get("trigger_span_id"), "trigger_span_id", ep, errors, valid_spans, span_refs)
    return keys


def validate_suggested_new_tags(value, prefix, errors, valid_spans, span_refs):
    fields: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.suggested_new_tags must be an array")
        return fields
    for i, c in enumerate(value):
        cp = f"{prefix}.suggested_new_tags[{i}]"
        if not isinstance(c, dict):
            errors.append(f"{cp} must be an object")
            continue
        for key in ("field", "label", "display_name", "reason", "trigger_span_id", "status"):
            if key not in c:
                errors.append(f"{cp} missing {key}")
        field = c.get("field")
        if isinstance(field, str):
            fields.add(field)
        if field in OPEN_FIELDS:
            errors.append(f"{cp}.field is an open field ({field}); use inline other:<slug>")
        if c.get("status") != "pending_review":
            errors.append(f"{cp}.status must be pending_review")
        label = c.get("label")
        if not isinstance(label, str) or not label.replace("_", "").isalnum() or label.lower() != label:
            errors.append(f"{cp}.label must be lowercase snake_case")
        for key in ("display_name", "reason"):
            if not isinstance(c.get(key), str) or not c.get(key):
                errors.append(f"{cp}.{key} must be a non-empty string")
        validate_span_id(c.get("trigger_span_id"), "trigger_span_id", cp, errors, valid_spans, span_refs)
    return fields


def validate_item(item, index, spans_by_id):
    prefix = f"[{index}]"
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(item, dict):
        return [f"{prefix} item must be an object"], warnings

    # V3 hard rule: no confidence anywhere
    for k in find_confidence_keys(item):
        errors.append(f"{prefix} confidence is banned in V3 (found key: {k})")

    unknown = sorted(set(item) - TOP_LEVEL_FIELDS)
    if unknown:
        errors.append(f"{prefix} unknown top-level fields: {', '.join(unknown)}")
    missing = sorted(REQUIRED_TOP_LEVEL - set(item))
    if missing:
        errors.append(f"{prefix} missing top-level fields: {', '.join(missing)}")

    if item.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{prefix} schema_version must be {SCHEMA_VERSION}")
    article_id = item.get("article_id")
    if not isinstance(article_id, str) or not article_id:
        errors.append(f"{prefix} article_id must be a non-empty string")

    relevance = item.get("relevance")
    if relevance not in RELEVANCE_VALUES:
        errors.append(f"{prefix} relevance invalid: {relevance!r}")
    decision = item.get("tagging_decision")
    if decision not in TAGGING_DECISIONS:
        errors.append(f"{prefix} tagging_decision invalid: {decision!r}")

    # resolve this article's valid span ids (None => skip cross-check, warn once)
    valid_spans = spans_by_id.get(article_id) if spans_by_id is not None else None
    if spans_by_id is not None and isinstance(article_id, str) and article_id not in spans_by_id:
        warnings.append(f"{prefix} no spans found for article_id={article_id} in --article input; span ids unchecked")
    span_refs: list[str] = []

    primary = validate_section(item.get("section"), prefix, errors, valid_spans, span_refs)
    review_reasons = validate_string_list(item, "review_reasons", REVIEW_REASONS, prefix, errors)
    suggested_fields = validate_suggested_new_tags(item.get("suggested_new_tags"), prefix, errors, valid_spans, span_refs)
    evidence_keys = validate_evidence_records(item.get("evidence_records"), prefix, errors, valid_spans, span_refs)

    # tags
    tags = item.get("tags")
    formal_labels: list[tuple[str, str]] = []
    if decision == "tagged":
        if not isinstance(tags, dict):
            errors.append(f"{prefix} tags must be an object when tagging_decision=tagged")
            tags = {}
        if "primary_story_type" not in tags:
            errors.append(f"{prefix} tags missing required field: primary_story_type")
        for field in sorted(set(tags) - TAG_FIELDS):
            if field in SCRIPT_FIELDS_FORBIDDEN_IN_TAGS:
                errors.append(f"{prefix} tags.{field} is a SCRIPT field in V3 and must not be emitted by the Agent")
            else:
                errors.append(f"{prefix} tags has unknown field: {field}")
        for field in SINGLE_TAG_FIELDS:
            if field not in tags or tags.get(field) is None:
                continue  # value_chain_stage null allowed (phase 2)
            label = tags.get(field)
            if label not in ALLOWED[field]:
                errors.append(f"{prefix} tags.{field} has invalid label: {label!r}")
            else:
                formal_labels.append((field, label))
        for field in ARRAY_TAG_FIELDS:
            if field not in tags:
                continue
            labels = validate_string_list(
                tags, field, ALLOWED.get(field), f"{prefix}.tags",
                errors, min_items=1 if field == "primary_story_type" else 0,
            )
            formal_labels.extend((field, label) for label in labels)
        if primary not in CONTENT_SECTIONS:
            errors.append(f"{prefix} tagging_decision=tagged requires a content primary_section, got {primary!r}")
        if not formal_labels:
            errors.append(f"{prefix} tagging_decision=tagged requires at least one formal label")
    else:
        if isinstance(tags, dict):
            for field in SCRIPT_FIELDS_FORBIDDEN_IN_TAGS & set(tags):
                errors.append(f"{prefix} tags.{field} is a SCRIPT field and must not be emitted")

    # every formal label needs an evidence pointer
    for field, label in formal_labels:
        if (field, label) not in evidence_keys:
            errors.append(f"{prefix} missing evidence pointer for {field}={label}")

    # decision <-> section / relevance consistency
    if decision == "excluded":
        if primary != "exclude":
            errors.append(f"{prefix} tagging_decision=excluded requires section.primary_section=exclude")
        if relevance == "relevant":
            warnings.append(f"{prefix} excluded but relevance=relevant (check)")
    if decision == "needs_review":
        if primary != "needs_review":
            errors.append(f"{prefix} tagging_decision=needs_review requires section.primary_section=needs_review")
        if not review_reasons:
            errors.append(f"{prefix} needs_review requires at least one review_reasons value")
    if decision == "no_matching_tag" and not review_reasons:
        errors.append(f"{prefix} no_matching_tag requires at least one review_reasons value")
    if primary == "exclude" and decision not in {"excluded"}:
        warnings.append(f"{prefix} primary_section=exclude usually pairs with tagging_decision=excluded")
    if relevance == "not_relevant" and decision != "excluded":
        errors.append(f"{prefix} relevance=not_relevant requires tagging_decision=excluded")

    if suggested_fields and "suggested_new_taxonomy_label" not in review_reasons:
        errors.append(f"{prefix} suggested_new_tags requires review_reasons to include suggested_new_taxonomy_label")

    tag_audit = item.get("tag_audit")
    if not isinstance(tag_audit, dict):
        errors.append(f"{prefix} tag_audit must be an object")
        tag_audit = {}
    for key in ("tagger", "tagged_at", "dictionary_version", "prompt_version"):
        if key not in tag_audit:
            errors.append(f"{prefix} tag_audit missing {key}")

    return errors, warnings


def load_spans(article_path: str) -> dict[str, set[str]]:
    """Build {article_id: {span ids}} from the input article package."""
    payload = json.loads(Path(article_path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "articles" in payload:
        records = payload["articles"]
    elif isinstance(payload, list):
        records = payload
    else:
        records = [payload]
    out: dict[str, set[str]] = {}
    for r in records:
        if not isinstance(r, dict):
            continue
        aid = r.get("article_id") or r.get("id")
        spans = r.get("spans")
        ids = {s["id"] for s in spans if isinstance(s, dict) and "id" in s} if isinstance(spans, list) else set()
        if isinstance(aid, str):
            out[aid] = ids
    return out


def build_metrics(items, errors):
    decision_counts = Counter(i.get("tagging_decision") for i in items if isinstance(i, dict))
    section_counts = Counter(
        i.get("section", {}).get("primary_section")
        for i in items if isinstance(i, dict) and isinstance(i.get("section"), dict)
    )
    tag_counter: Counter[str] = Counter()
    formal_total = tagged = inline_other = 0
    for i in items:
        if not isinstance(i, dict) or i.get("tagging_decision") != "tagged":
            continue
        tagged += 1
        tags = i.get("tags") if isinstance(i.get("tags"), dict) else {}
        for field, value in tags.items():
            for label in as_list(value):
                if label is None:
                    continue
                tag_counter[f"{field}:{label}"] += 1
                formal_total += 1
                if field in OPEN_FIELDS and isinstance(label, str) and OTHER_RE.match(label):
                    inline_other += 1
    return {
        "processed_count": len(items),
        "tagged_count": decision_counts.get("tagged", 0),
        "excluded_count": decision_counts.get("excluded", 0),
        "needs_review_count": decision_counts.get("needs_review", 0) + decision_counts.get("no_matching_tag", 0),
        "schema_validation_failed_count": 1 if errors else 0,
        "section_distribution": dict(section_counts),
        "average_tags_per_article": round(formal_total / tagged, 2) if tagged else 0,
        "top_tags_distribution": dict(tag_counter.most_common(20)),
        "inline_other_terms_count": inline_other,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", help="Path to a V3 tagging output JSON file")
    parser.add_argument("--article", help="Input article package (with spans) to cross-check span ids")
    parser.add_argument("--metrics-json", action="store_true", help="Print metrics as JSON")
    args = parser.parse_args()

    try:
        payload = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid_json: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: failed to load input: {exc}", file=sys.stderr)
        return 2

    spans_by_id = None
    if args.article:
        try:
            spans_by_id = load_spans(args.article)
        except Exception as exc:
            print(f"ERROR: failed to load --article spans: {exc}", file=sys.stderr)
            return 2

    items = payload if isinstance(payload, list) else [payload]
    errors: list[str] = []
    warnings: list[str] = []
    for index, item in enumerate(items):
        e, w = validate_item(item, index, spans_by_id)
        errors.extend(e)
        warnings.extend(w)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    metrics = build_metrics(items, errors)
    if args.metrics_json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if not args.metrics_json:
        print(f"OK: validated {len(items)} V3 tagging result(s)"
              + ("" if spans_by_id is not None else " (span ids NOT cross-checked; pass --article to enable)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
