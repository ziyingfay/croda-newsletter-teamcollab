#!/usr/bin/env python3
"""Validate Croda Beauty newsletter-tagging JSON output and print batch metrics.

v2 taxonomy (croda-beauty-2026-06-04):
- Agent emits only judgment tags; base fields (source_nature, content_language,
  market_region, ...) are written by the ingest script onto the article record.
- primary_story_type is multi-select; industry_segment / strategic_driver /
  entity_role removed; value_chain merged.
- Open fields (ingredient_technology, product_application, functional_claim)
  accept inline `other:<slug>` values (living dictionary).
- Evidence records keep only field/label/evidence_text (+extracted_name for other:).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "newsletter-tagging/croda-beauty-v1"

# Fields that accept inline `other:<slug>` living-dictionary values.
OPEN_FIELDS = {"ingredient_technology", "product_application", "functional_claim"}

ALLOWED = {
    "primary_story_type": {
        "corporate_move",
        "product_launch_or_update",
        "technology_process_innovation",
        "research_science",
        "regulation_policy",
        "market_consumer_insight",
        "event_news",
        "other",
    },
    "product_application": {
        "skincare",
        "sun_care",
        "color_cosmetics",
        "hair_care",
        "body_personal_care",
        "oral_care",
        "baby_care",
        "men_care",
        "fragrance_perfume",
    },
    "ingredient_technology": {
        "peptides",
        "pdrn_nucleotides",
        "ceramides",
        "retinoids",
        "retinol_alternatives",
        "recombinant_collagen",
        "hyaluronic_acid",
        "niacinamide",
        "vitamin_c",
        "probiotics_postbiotics",
        "exosomes",
        "growth_factors",
        "plant_botanical_extracts",
        "marine_blue_biotech_actives",
        "ergothioneine",
        "longevity_telomere_actives",
        "acids_exfoliants",
        "base_functional_raw",
        "encapsulation_delivery",
        "sustained_release",
        "synthetic_biology",
        "fermentation_biotech",
        "green_chemistry",
        "ai_rd_formulation",
        "neurocosmetics_tech",
        "dual_targeting_delivery",
    },
    "functional_claim": {
        "anti_aging",
        "whitening_brightening",
        "moisturizing",
        "barrier_repair",
        "soothing_sensitive_skin",
        "acne_oil_control",
        "sun_protection",
        "firming_lifting",
        "microbiome_balance",
        "hair_scalp_care",
        "emotion_wellbeing",
    },
    "value_chain_stage": {
        "raw_material_upstream",
        "ingredient_active",
        "formulation_application",
        "manufacturing_contract",
        "packaging",
        "brand_finished_product",
        "distribution_channel",
        "consumer_market",
        "regulation_research",
        "cross_chain",
        "other",
    },
}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "article_id",
    "relevance",
    "tagging_decision",
    "evidence_records",
    "suggested_new_tags",
    "review_reasons",
    "tag_audit",
}
TOP_LEVEL_FIELDS = REQUIRED_TOP_LEVEL | {"url", "source_key", "source_name", "tags"}

# Always required when tagging_decision == tagged.
REQUIRED_TAGGED_FIELDS = {"primary_story_type", "value_chain_stage"}
SINGLE_TAG_FIELDS = {"value_chain_stage"}
ARRAY_TAG_FIELDS = {
    "primary_story_type",
    "product_application",
    "ingredient_technology",
    "functional_claim",
    "company",
}
TAG_FIELDS = REQUIRED_TAGGED_FIELDS | ARRAY_TAG_FIELDS

RELEVANCE_VALUES = {"relevant", "not_relevant", "unclear"}
TAGGING_DECISIONS = {"tagged", "no_relevant_tag", "no_matching_tag", "needs_review"}
REVIEW_REASONS = {
    "insufficient_evidence",
    "ambiguous_relevance",
    "suggested_new_taxonomy_label",
    "conflicting_tags",
    "insufficient_content",
    "broad_or_suspicious_tag",
    "inconsistent_model_output",
    "high_risk_label_sample",
    "random_sample",
    "post_processing_flag",
    "human_requested",
}
OTHER_RE = re.compile(r"^other:[a-z0-9_]+$")
AI_PASSING_TERMS = {"mentions ai", "ai was mentioned", "ai influence"}


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


def validate_string_list(
    item: dict[str, Any],
    key: str,
    allowed: set[str] | None,
    prefix: str,
    errors: list[str],
    *,
    min_items: int = 0,
) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}.{key} must be an array")
        return []
    if len(value) < min_items:
        errors.append(f"{prefix}.{key} must contain at least {min_items} item(s)")
    if len(value) != len(set(value)):
        errors.append(f"{prefix}.{key} must not contain duplicate values")
    labels: list[str] = []
    for label in value:
        if not isinstance(label, str):
            errors.append(f"{prefix}.{key} contains a non-string label: {label!r}")
        elif allowed is not None and not is_allowed_label(key, label):
            errors.append(f"{prefix}.{key} has invalid label: {label!r}")
        else:
            labels.append(label)
    return labels


def validate_suggested_new_tags(value: Any, prefix: str, errors: list[str]) -> set[str]:
    fields: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.suggested_new_tags must be an array")
        return fields
    for index, candidate in enumerate(value):
        candidate_prefix = f"{prefix}.suggested_new_tags[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{candidate_prefix} must be an object")
            continue
        for key in ("field", "label", "display_name", "reason", "evidence", "status"):
            if key not in candidate:
                errors.append(f"{candidate_prefix} missing {key}")
        field = candidate.get("field")
        if isinstance(field, str):
            fields.add(field)
        if candidate.get("status") != "pending_review":
            errors.append(f"{candidate_prefix}.status must be pending_review")
        label = candidate.get("label")
        if not isinstance(label, str) or not label.replace("_", "").isalnum() or label.lower() != label:
            errors.append(f"{candidate_prefix}.label must be lowercase snake_case")
        if field in OPEN_FIELDS:
            errors.append(
                f"{candidate_prefix}.field is an open field ({field}); use inline other:<slug> instead of suggested_new_tags"
            )
        for key in ("display_name", "reason", "evidence"):
            if not isinstance(candidate.get(key), str) or not candidate.get(key):
                errors.append(f"{candidate_prefix}.{key} must be a non-empty string")
    return fields


def validate_evidence_records(value: Any, prefix: str, errors: list[str]) -> set[tuple[str, str]]:
    evidence_keys: set[tuple[str, str]] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.evidence_records must be an array")
        return evidence_keys
    for index, evidence in enumerate(value):
        evidence_prefix = f"{prefix}.evidence_records[{index}]"
        if not isinstance(evidence, dict):
            errors.append(f"{evidence_prefix} must be an object")
            continue
        for key in ("field", "label", "evidence_text"):
            if key not in evidence:
                errors.append(f"{evidence_prefix} missing {key}")
        field = evidence.get("field")
        label = evidence.get("label")
        if isinstance(field, str) and isinstance(label, str):
            evidence_keys.add((field, label))
        if field in OPEN_FIELDS and isinstance(label, str) and OTHER_RE.match(label):
            extracted_name = evidence.get("extracted_name")
            if not isinstance(extracted_name, str) or not extracted_name:
                errors.append(f"{evidence_prefix}.extracted_name is required for {label}")
        if not isinstance(evidence.get("evidence_text"), str) or not evidence.get("evidence_text"):
            errors.append(f"{evidence_prefix}.evidence_text must be a non-empty string")
    return evidence_keys


def post_processing_flags(item: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    tags = item.get("tags") if isinstance(item.get("tags"), dict) else {}
    evidence_records = [e for e in item.get("evidence_records", []) if isinstance(e, dict)]

    def evidence_text_for(field: str, label: str) -> str:
        return " ".join(
            str(evidence.get("evidence_text", "")).lower()
            for evidence in evidence_records
            if evidence.get("field") == field and evidence.get("label") == label
        )

    if "ai_rd_formulation" in as_list(tags.get("ingredient_technology")):
        text = evidence_text_for("ingredient_technology", "ai_rd_formulation")
        if any(term in text for term in AI_PASSING_TERMS) or len(text.strip()) < 30:
            flags.append("broad_or_suspicious_tag:ai_rd_formulation")

    return flags


def validate_item(item: Any, index: int) -> tuple[list[str], list[str]]:
    prefix = f"[{index}]"
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(item, dict):
        return [f"{prefix} item must be an object"], warnings

    unknown_top_level = sorted(set(item) - TOP_LEVEL_FIELDS)
    if unknown_top_level:
        errors.append(f"{prefix} unknown top-level fields: {', '.join(unknown_top_level)}")

    missing = sorted(REQUIRED_TOP_LEVEL - set(item))
    if missing:
        errors.append(f"{prefix} missing top-level fields: {', '.join(missing)}")

    if item.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{prefix} schema_version must be {SCHEMA_VERSION}")

    if not isinstance(item.get("article_id"), str) or not item.get("article_id"):
        errors.append(f"{prefix} article_id must be a non-empty string")

    relevance = item.get("relevance")
    if relevance not in RELEVANCE_VALUES:
        errors.append(f"{prefix} relevance has invalid value: {relevance!r}")

    decision = item.get("tagging_decision")
    if decision not in TAGGING_DECISIONS:
        errors.append(f"{prefix} tagging_decision has invalid value: {decision!r}")

    review_reasons = validate_string_list(item, "review_reasons", REVIEW_REASONS, prefix, errors)
    suggested_fields = validate_suggested_new_tags(item.get("suggested_new_tags"), prefix, errors)
    evidence_keys = validate_evidence_records(item.get("evidence_records"), prefix, errors)

    tags = item.get("tags")
    formal_labels: list[tuple[str, str]] = []
    if decision == "tagged":
        if not isinstance(tags, dict):
            errors.append(f"{prefix} tags must be an object when tagging_decision=tagged")
            tags = {}
        missing_tags = sorted(REQUIRED_TAGGED_FIELDS - set(tags))
        if missing_tags:
            errors.append(f"{prefix} tags missing required fields: {', '.join(missing_tags)}")
        for field in sorted(set(tags) - TAG_FIELDS):
            errors.append(f"{prefix} tags has unknown field: {field}")
        for field in SINGLE_TAG_FIELDS:
            label = tags.get(field)
            if label not in ALLOWED[field]:
                errors.append(f"{prefix} tags.{field} has invalid label: {label!r}")
            else:
                formal_labels.append((field, label))
        for field in ARRAY_TAG_FIELDS:
            if field not in tags:
                continue
            labels = validate_string_list(
                tags,
                field,
                ALLOWED.get(field),
                f"{prefix}.tags",
                errors,
                min_items=1 if field == "primary_story_type" else 0,
            )
            formal_labels.extend((field, label) for label in labels)
    elif tags not in (None, {}):
        errors.append(f"{prefix} tags must be omitted or empty unless tagging_decision=tagged")

    if decision == "tagged" and not formal_labels:
        errors.append(f"{prefix} tagging_decision=tagged requires at least one formal label")

    for field, label in formal_labels:
        if (field, label) not in evidence_keys:
            errors.append(f"{prefix} missing evidence for {field}={label}")

    if decision in {"needs_review", "no_matching_tag"} and not review_reasons:
        errors.append(f"{prefix} {decision} requires at least one review_reasons value")

    if relevance == "not_relevant" and decision != "no_relevant_tag":
        errors.append(f"{prefix} relevance=not_relevant requires tagging_decision=no_relevant_tag")

    if decision == "no_matching_tag" and "suggested_new_taxonomy_label" not in review_reasons:
        warnings.append(f"{prefix} no_matching_tag usually should include suggested_new_taxonomy_label")

    if suggested_fields and "suggested_new_taxonomy_label" not in review_reasons:
        errors.append(
            f"{prefix} suggested_new_tags requires review_reasons to include suggested_new_taxonomy_label"
        )

    tag_audit = item.get("tag_audit")
    if not isinstance(tag_audit, dict):
        errors.append(f"{prefix} tag_audit must be an object")
        tag_audit = {}
    for key in ("tagger", "tagged_at", "dictionary_version", "prompt_version"):
        if key not in tag_audit:
            errors.append(f"{prefix} tag_audit missing {key}")

    warnings.extend(f"{prefix} post-processing flag: {flag}" for flag in post_processing_flags(item))
    return errors, warnings


def build_metrics(items: list[Any], errors: list[str]) -> dict[str, Any]:
    decision_counts = Counter(item.get("tagging_decision") for item in items if isinstance(item, dict))
    tag_counter: Counter[str] = Counter()
    formal_tag_total = 0
    tagged_items = 0
    invalid_json_count = 0
    inline_other_terms_count = 0
    schema_validation_failed_count = 1 if errors else 0

    for item in items:
        if not isinstance(item, dict):
            invalid_json_count += 1
            continue
        if item.get("tagging_decision") != "tagged":
            continue
        tagged_items += 1
        tags = item.get("tags") if isinstance(item.get("tags"), dict) else {}
        for field, value in tags.items():
            for label in as_list(value):
                tag_counter[f"{field}:{label}"] += 1
                formal_tag_total += 1
                if field in OPEN_FIELDS and isinstance(label, str) and OTHER_RE.match(label):
                    inline_other_terms_count += 1

    return {
        "processed_count": len(items),
        "tagged_count": decision_counts.get("tagged", 0),
        "failed_count": schema_validation_failed_count,
        "needs_review_count": decision_counts.get("needs_review", 0)
        + decision_counts.get("no_matching_tag", 0),
        "no_relevant_tag_count": decision_counts.get("no_relevant_tag", 0),
        "invalid_json_count": invalid_json_count,
        "schema_validation_failed_count": schema_validation_failed_count,
        "retry_count": 0,
        "average_tags_per_article": round(formal_tag_total / tagged_items, 2) if tagged_items else 0,
        "top_tags_distribution": dict(tag_counter.most_common(20)),
        "inline_other_terms_count": inline_other_terms_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", help="Path to a tagging output JSON file")
    parser.add_argument("--metrics-json", action="store_true", help="Print metrics as JSON after validation")
    args = parser.parse_args()

    try:
        payload = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid_json: {exc}", file=sys.stderr)
        if args.metrics_json:
            print(
                json.dumps(
                    {
                        "processed_count": 0,
                        "tagged_count": 0,
                        "failed_count": 1,
                        "needs_review_count": 0,
                        "no_relevant_tag_count": 0,
                        "invalid_json_count": 1,
                        "schema_validation_failed_count": 0,
                        "retry_count": 0,
                        "average_tags_per_article": 0,
                        "top_tags_distribution": {},
                        "inline_other_terms_count": 0,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        return 2
    except Exception as exc:
        print(f"ERROR: failed to load input: {exc}", file=sys.stderr)
        return 2

    items = payload if isinstance(payload, list) else [payload]
    errors: list[str] = []
    warnings: list[str] = []
    for index, item in enumerate(items):
        item_errors, item_warnings = validate_item(item, index)
        errors.extend(item_errors)
        warnings.extend(item_warnings)

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    metrics = build_metrics(items, errors)
    if args.metrics_json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if not args.metrics_json:
        print(f"OK: validated {len(items)} tagging result(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
