---
name: newsletter-tagging
description: Use this skill when OpenClaw runs structured, batch-safe tagging for Croda Beauty market-intelligence newsletter articles from v_articles_for_tagging or validated JSON input. It separates code-controlled workflow from LLM semantic judgment, validates strict JSON output, records evidence, supports inline ingredient/technology other terms, review queues, and free company entity extraction.
---

# Newsletter Tagging

## Use

Use this skill for Croda Beauty article tagging, retagging, review preparation, inline ingredient/technology other extraction, and company entity extraction.

OpenClaw must not improvise the workflow. The code workflow owns database reads, status transitions, retries, validation, post-processing, writes, review queue creation, logging, dry runs, and batch metrics. The LLM only performs semantic judgment for one article at a time.

## Load

- Read `references/workflow.md` before implementing or running a tagging batch.
- Use `references/llm_prompt.md` as the LLM prompt template.
- Read `references/标签字段字典.md` when tag definitions, allowed labels, inline `other:<slug>` rules, suggested-new-tag boundaries, or company extraction rules are needed.
- Validate LLM output against `schemas/tag_output.schema.json` and `scripts/validate_tags.py` before any database write.

## Required Workflow

1. Code reads candidate articles from `v_articles_for_tagging`.
2. Code moves each article through `article_tag_status`: `pending` -> `in_progress` -> `tagged`, `needs_review`, or `failed`.
3. Code calls the LLM with exactly the article package, active Croda taxonomy, and `references/llm_prompt.md`.
4. LLM returns strict JSON using `schema_version: newsletter-tagging/croda-beauty-v1`.
5. Code runs schema validation, then `python3 newsletter-tagging/scripts/validate_tags.py output.json`.
6. Code runs deterministic post-processing rules from `references/workflow.md`.
7. Code writes validated formal tags, inline `ingredient_technology` other terms, and free company entities to `article_tags`.
8. Code writes their evidence to `tag_evidence`.
9. Code maps `suggested_new_tags`, `no_matching_tag`, ambiguous cases, insufficient content, random samples, and post-processing flags into `needs_review` / review queue records.
10. Code records retry attempts, failure type, raw invalid model output, and batch metrics.
11. Code supports `--dry-run` so validation, post-processing, review queue decisions, and metrics can be inspected without database writes.

## LLM Contract

The LLM may:

- Judge relevance to Croda Beauty market intelligence.
- Choose allowed taxonomy labels with evidence.
- Extract company entities when they are news subjects or important related parties.
- Use `ingredient_technology` inline labels such as `other:synthetic_pdrn` when a concrete ingredient or technology is absent from the dictionary.
- Return `no_matching_tag` when the article is relevant but a closed taxonomy field lacks a suitable label.
- Return `suggested_new_tags` for review instead of inventing formal labels in closed fields.
- Return `needs_review` with explicit reasons when evidence, relevance, or label boundaries are unclear.

The LLM must not:

- Decide workflow steps, retries, status transitions, database writes, or sampling.
- Invent formal labels outside the dictionary, except allowed `ingredient_technology` inline `other:<slug>`.
- Use self-rated confidence or confidence thresholds.
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
  "source_nature": "wechat_public_account",
  "tags": {
    "content_language": "zh",
    "primary_story_type": "product_launch_or_update",
    "industry_segment": "active_ingredients",
    "product_application": ["skincare"],
    "ingredient_technology": ["peptides"],
    "functional_claim": ["anti_aging"],
    "strategic_driver": ["delivery_technology"],
    "value_chain_stage": "ingredient_active",
    "entity_role": ["competitor"],
    "company": ["Example Company"]
  },
  "evidence_records": [
    {
      "field": "primary_story_type",
      "label": "product_launch_or_update",
      "evidence_field": "content",
      "evidence_text": "The article reports a new peptide active launch.",
      "reason": "The main event is a commercial ingredient launch."
    }
  ],
  "suggested_new_tags": [],
  "review_reasons": [],
  "tag_audit": {
    "tagger": "openclaw",
    "tagged_at": "2026-06-03T12:00:00+02:00",
    "evidence_fields": ["title", "summary", "content"],
    "dictionary_version": "croda-beauty-2026-06-03",
    "prompt_version": "newsletter-tagging-prompt/croda-beauty-v1"
  }
}
```
