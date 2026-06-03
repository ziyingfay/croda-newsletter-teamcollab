# Structured Tagging Workflow

This reference defines the code-controlled workflow for Croda Beauty newsletter tagging. The LLM only judges article semantics.

## Code Responsibilities

Code or scripts must own:

- Read pending articles from `v_articles_for_tagging`.
- Lock rows and move `article_tag_status` through `pending`, `in_progress`, `tagged`, `needs_review`, and `failed`.
- Call the LLM with the approved prompt and one article package at a time.
- Parse strict JSON and validate it against `schemas/tag_output.schema.json`.
- Run `scripts/validate_tags.py`.
- Run deterministic post-processing rules.
- Retry technical failures and invalid model output according to configured max attempts.
- Write validated formal taxonomy labels, inline `ingredient_technology` other terms, and free company entities to `article_tags`.
- Write one or more `tag_evidence` rows for every formal tag.
- Map `ingredient_technology` inline `other:<slug>` to `inline_other_terms` for frequency tracking.
- Map `suggested_new_tags` to the review flow, not directly into formal tags.
- Create review queue rows for `needs_review`, random samples, high-risk tags, and post-processing flags.
- Log attempts, raw invalid output, validation errors, retry counts, and final outcomes.
- Support `--dry-run`, batch limits, retry limits, and batch metrics output.

## LLM Responsibilities

The LLM only owns semantic judgment:

- Read `title`, `summary`, `content`, `source_name`, `source_key`, `url`, `raw_tags`, and source metadata.
- Judge whether the article is relevant to Croda Beauty market intelligence.
- Select allowed taxonomy labels from `references/标签字段字典.md`.
- Extract inline `ingredient_technology` `other:<slug>` labels for concrete, dictionary-missing ingredients or technologies.
- Provide evidence for every formal label.
- Identify articles that need review because relevance, evidence, taxonomy fit, or content quality is unclear.
- Return `no_matching_tag` when the article is relevant but no controlled label fits.
- Return `suggested_new_tags` for review instead of inventing formal labels in closed fields.

## State Machine

Primary `article_tag_status.status` values:

| Status | Meaning | Allowed next status |
|--------|---------|---------------------|
| `pending` | Ready to tag | `in_progress` |
| `in_progress` | Locked by a batch run | `tagged`, `needs_review`, `failed`, `pending` on stale lock reset |
| `tagged` | Valid formal tags were written | `pending` for retagging |
| `needs_review` | Business review or quality review needed | `pending`, `tagged`, `failed` after human action |
| `failed` | Technical/system failure after retries | `pending` for manual retry |

Recommended secondary fields:

- `outcome_type`: `tagged`, `no_relevant_tag`, `no_matching_tag`, `insufficient_content`, `ambiguous_tagging`, `technical_failure`, `invalid_model_output`.
- `failure_type`: one of the failure taxonomy values below when applicable.
- `review_reasons_json`: machine-readable review reason array.
- `last_error`: concise machine-readable error summary.
- `raw_model_output`: only for invalid output or audit storage.

## Failure Taxonomy

Do not call every exception `failed`.

| Type | Definition | Final handling |
|------|------------|----------------|
| `technical_failure` | API failure, network error, timeout, database write failure, script/runtime error | Retry; after max retries set `failed` |
| `invalid_model_output` | Non-JSON, schema failure, missing required fields, unknown formal labels | Retry once or configured retry count; then `failed` and store raw output |
| `insufficient_content` | Missing body, only title, too-short content, extraction quality too poor to judge | Set `needs_review` or outcome `insufficient_content`; not technical failed |
| `no_matching_tag` | Readable and relevant article but taxonomy lacks a suitable closed-field label | Set `needs_review` when suggested labels exist, otherwise outcome `no_matching_tag`; not failed |
| `ambiguous_tagging` | Multiple plausible directions, weak evidence, or conflicting labels | Set `needs_review`; not failed |

`failed` is reserved for technical/system inability to complete the workflow.

## Needs Review Triggers

Set `needs_review` when any condition is true:

- LLM JSON is valid but evidence is missing, weak, circular, or from a low-priority source only.
- Relevance is `unclear`.
- `tagging_decision` is `needs_review`.
- The article is relevant but returns `no_matching_tag` with `suggested_new_tags`.
- Content is missing, too short, mostly navigation, or extraction status is not enough to judge.
- Tags conflict, such as unsupported combinations of story type, strategic driver, and evidence.
- Post-processing flags broad or suspicious labels.
- Repeated LLM attempts produce materially different formal tags.
- The article is selected by random sample review.
- The article contains high-risk tags or newly suggested taxonomy labels.

Do not set `needs_review` solely because `ingredient_technology` contains a valid inline `other:<slug>` with evidence and `extracted_name`.

## Deterministic Post-Processing Rules

These rules belong in code, not only in the prompt:

- Reject any formal label not in the active taxonomy, except valid `ingredient_technology` inline `other:<slug>`.
- Reject any formal tag without an evidence record for the exact `(field, label)`.
- Reject `ingredient_technology` `other:<slug>` evidence without `extracted_name`.
- Reject any output containing `confidence`, `confidence_score`, or threshold-based logic.
- Flag `sustainability` when evidence only says generic green, eco, natural, or environmentally friendly without concrete sustainability facts.
- Flag `ai_rd_formulation` when evidence merely mentions AI in passing.
- Do not infer broad beauty tags just because the source or company is in beauty; require article-level evidence.
- Flag `source_defaults`-only evidence for optional article tags.
- If `content_length` is below the configured minimum, or content is missing and summary is too thin, set `needs_review` with `insufficient_content`.
- Do not require a company watchlist. Company names are free entities extracted by the LLM and validated by evidence.
- If a company appears only in navigation, ads, related links, quote attribution, or long lists, do not write the company entity.
- Reject or flag company entities without matching evidence for `field=company` and the exact company display name.

## Batch, Dry Run, Retry, And Logging

Recommended runner options:

- `--limit N`: maximum articles to load from `v_articles_for_tagging`.
- `--dry-run`: run LLM, validation, post-processing, and metrics without writing tags or status changes permanently.
- `--retry-max N`: retry count for `technical_failure` and `invalid_model_output`.
- `--batch-id ID`: explicit tagging run id, otherwise generated.
- `--review-sample-rate 0.05`: random review sample rate.
- `--high-risk-sample-rate 0.20`: review sample rate for high-risk tags or new tag suggestions.
- `--log-file PATH`: JSONL attempt and metrics log.

Every attempt log should include `tag_run_id`, `article_id`, attempt number, model/prompt version, status transition, validation result, post-processing flags, retry decision, and final outcome.

## Quality Metrics

Each batch should output at least:

- `processed_count`
- `tagged_count`
- `failed_count`
- `needs_review_count`
- `no_relevant_tag_count`
- `invalid_json_count`
- `schema_validation_failed_count`
- `retry_count`
- `average_tags_per_article`
- `top_tags_distribution`
- `inline_other_terms_count`

Reserve optional fields for human-reviewed metrics when data exists:

- `precision`
- `recall`
- `f1`

Do not fabricate precision, recall, or F1 without reviewed ground truth.
