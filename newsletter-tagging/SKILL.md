---
name: newsletter-tagging
description: Use this skill when OpenClaw runs structured tagging for Croda Beauty market-intelligence newsletter articles from monthly rss_clean.json input or, in the full database version, v_articles_for_tagging. It separates code-controlled workflow from LLM semantic judgment, validates strict JSON output, records evidence, supports inline open-field other terms, review queues, and free company entity extraction.
---

# Newsletter Tagging

## Use

Use this skill for Croda Beauty article tagging, retagging, review preparation, inline open-field other extraction, and company entity extraction.

OpenClaw must not improvise the workflow. The code workflow owns input loading, retries, validation, post-processing, writes, review collection, logging, dry runs, and batch metrics. The LLM only performs semantic judgment for one article at a time.

## Load

- Read `references/workflow.md` before implementing or running a tagging batch.
- Use `references/llm_prompt.md` as the LLM prompt template.
- Read `references/标签字段字典.md` when tag definitions, allowed labels, inline `other:<slug>` rules, suggested-new-tag boundaries, or company extraction rules are needed.
- Validate LLM output against `schemas/tag_output.schema.json` and `scripts/validate_tags.py` before any database write.

## Required Workflow

1. MVP code reads candidate articles from `outputs/<month>/rss_clean.json`.
2. Full-version code may instead read from `v_articles_for_tagging`.
3. Code calls the LLM with exactly one article package, active Croda taxonomy, and `references/llm_prompt.md`.
4. LLM returns strict JSON using `schema_version: newsletter-tagging/croda-beauty-v1`.
5. Code runs schema validation, then `python3 newsletter-tagging/scripts/validate_tags.py output.json`.
6. Code runs deterministic post-processing rules from `references/workflow.md`.
7. MVP code writes validated results to `outputs/<month>/tagging.json`.
8. Full-version code may write equivalent records to `article_tags`, `tag_evidence`, `inline_other_terms`, and review tables.
9. Code records validation results, review reasons, retry attempts, raw invalid model output, and batch metrics in the monthly run log or database audit tables.

## LLM Contract

The LLM may:

- Judge relevance to Croda Beauty market intelligence.
- Choose allowed taxonomy labels with evidence.
- Extract company entities when they are news subjects or important related parties.
- Use inline `other:<slug>` labels in the open fields (`ingredient_technology`, `product_application`, `functional_claim`) such as `other:synthetic_pdrn` when a concrete value is absent from the dictionary. Prefer over-extracting to missing a new trend.
- Choose multiple `primary_story_type` values when the article genuinely spans several event types.
- Return `no_matching_tag` when the article is relevant but a closed taxonomy field lacks a suitable label.
- Return `suggested_new_tags` for review instead of inventing formal labels in closed fields (`primary_story_type`, `value_chain_stage`).
- Return `needs_review` with explicit reasons when evidence, relevance, or label boundaries are unclear.

The LLM must not:

- Decide workflow steps, retries, status transitions, database writes, or sampling.
- Invent formal labels outside the dictionary, except allowed inline `other:<slug>` in the open fields (`ingredient_technology`, `product_application`, `functional_claim`).
- Add tags without evidence.
- Treat general text classification as the goal; tags must serve newsletter intelligence filtering, grouping, deduplication, prioritization, company monitoring, trend analysis, or monthly report generation.

## Output

Return either one Croda v1 tagging result object or an array of such objects. Minimal tagged result:

```json
{
  "schema_version": "newsletter-tagging/croda-beauty-v1",
  "article_id": "stable-id",
  "relevance": "relevant",
  "tagging_decision": "tagged",
  "tags": {
    "primary_story_type": ["product_launch_or_update"],
    "product_application": ["skincare"],
    "ingredient_technology": ["peptides"],
    "functional_claim": ["anti_aging"],
    "value_chain_stage": "ingredient_active",
    "company": ["Example Company"]
  },
  "evidence_records": [
    {
      "field": "primary_story_type",
      "label": "product_launch_or_update",
      "evidence_text": "The article reports a new peptide active launch."
    }
  ],
  "suggested_new_tags": [],
  "review_reasons": [],
  "tag_audit": {
    "tagger": "openclaw",
    "tagged_at": "2026-06-04T12:00:00+08:00",
    "dictionary_version": "croda-beauty-2026-06-04",
    "prompt_version": "newsletter-tagging-prompt/croda-beauty-v1"
  }
}
```
