# Croda Newsletter Section Tagging Test Plan

## 1. Purpose

This test is designed to answer one product question:

> What is the most reliable and cost-efficient way to place each media article into the Croda Beauty newsletter sections?

The current candidate approaches are:

- Full taxonomy tags first, then derive sections by mapping rules.
- Let the AI Agent classify newsletter sections directly.
- Let the AI Agent classify sections first, then output a small set of supporting tags.
- Use scripts for factual hints, then let the AI Agent classify sections.

The test should not assume that a complex tag dictionary is necessary for section placement. Tags may still be useful for search, evidence, trend aggregation, and future analysis, but the test must measure whether tags improve the actual newsletter section decision.

## 2. Source Files And Placement Decision

Keep original source materials in `project-management/reference/`.

Current source files used by this test:

- `project-management/reference/requirements/栏目标签讨论.rtf`
- `project-management/reference/examples/all-articles(1).json`
- `project-management/reference/requirements/croda-newsletter/禾大Croda-Newsletter需求分析报告.md`
- `product/parameter-file/tag-dictionary/标签字段字典-禾大美妆个护版-V2.md`
- `product/parameter-file/source-profiles/source_profiles_seed.json`
- `product/skills/newsletter-tagging/references/workflow.md`
- `product/skills/newsletter-tagging/references/llm_prompt.md`
- `product/skills/newsletter-tagging/schemas/tag_output.schema.json`

Do not copy the original RTF or the 33 MB JSON into this test folder. The test folder should contain only:

- test plans
- annotation guidelines
- prompt variants
- run manifests
- analysis notes

Reason:

- `project-management/reference/` is the canonical place for user-provided source material.
- Keeping one copy avoids stale duplicated data.
- The JSON is large enough that duplicating it would add noise to Git history.
- Test outputs and generated fixtures should not be mixed with original reference material.

If a normalized sample, gold-standard annotation file, or model output is created later, place it under:

```text
product/output/test-results/section-tagging-test/
```

Examples:

```text
product/output/test-results/section-tagging-test/fixtures/sample-120-input.json
product/output/test-results/section-tagging-test/gold-standard/sample-120-gold.json
product/output/test-results/section-tagging-test/runs/20260611-b-direct-section/
product/output/test-results/section-tagging-test/runs/20260611-c-section-plus-tags/
```

## 3. Current JSON Data Profile

The current test JSON is:

```text
project-management/reference/examples/all-articles(1).json
```

Observed structure:

- Top-level fields: `generatedAt`, `totalArticles`, `articles`.
- Article count: `499`.
- Main article fields: `id`, `mpId`, `title`, `author`, `content`, `contentText`, `images`, `url`, `publishTime`, `fetchedAt`, `meta`.
- `meta` includes `contentLength`, `contentTextLength`, and `qualityScore`.

Important data quality observations:

- `contentText` is usable as the main Agent reading input, but quality varies.
- `49` articles have empty `contentText`.
- `66` articles have `contentText` shorter than 300 characters.
- Many short or empty articles come from official ingredient supplier accounts, such as BASF, Lubrizol, Ashland, Symrise, Huiwen, JLand, and similar sources.
- `publishTime` appears close to fetch time and should not be treated as reliable business publication time in this test.
- `source_profiles_seed.json` currently covers only part of the `author` values in the JSON.

Conclusion:

The first test must separate section-classification quality from extraction-quality problems. A high-value official-account article with an empty body should not be silently discarded if the title still contains useful section evidence.

## 4. Minimal Input Normalization

Do not build the full production cleaner for this test. Use a minimal temporary mapping.

Map fields as follows:

| Test field | Source JSON field |
|---|---|
| `article_id` | `id` |
| `title` | `title` |
| `source_name` | `author` |
| `content` | `contentText` |
| `url` | `url` |
| `content_length` | `len(contentText)` |
| `raw_author` | `author` |
| `raw_mp_id` | `mpId` |
| `fetched_at` | `fetchedAt` |

For source metadata:

- If `author` matches `source_profiles_seed.json`, copy the available `source_key`, `source`, `source_list`, `market_region`, and `language`.
- If not matched, set `source_profile_matched=false` and keep `source_name=author`.
- For this test only, create an `author_role_hint` table for obvious source-level roles.

Suggested temporary `extraction_status`:

| Status | Rule |
|---|---|
| `success` | `content_length >= 800` |
| `partial` | `300 <= content_length < 800` |
| `title_only` | `0 < content_length < 300` |
| `empty` | `content_length == 0` |

This is a test convenience, not the final production extraction model.

## 5. Temporary Factual Hints

For the script-assisted test group, generate lightweight `fact_hints`.

Company hints:

- Competitor or ingredient supplier names: BASF / 巴斯夫, Symrise / 德之馨, Lubrizol / 路博润, Ashland / 亚什兰, Evonik / 赢创, Huiwen / 辉文, Viablife / 唯铂莱, JLand / 聚源, CoachChem / 克琴.
- Customer or downstream brand names: 欧莱雅, 珀莱雅, 薇诺娜, 自然堂, 雅诗兰黛, 兰蔻, 资生堂, SK-II, 玉兰油, 多芬.

Ingredient and technology hints:

- PDRN
- 多肽 / peptide
- 胶原 / collagen
- 神经酰胺 / ceramide
- 视黄醇 / A 醇 / retinol
- 透明质酸 / 玻尿酸 / hyaluronic acid
- 防晒 / sunscreen
- 发酵 / fermentation
- 合成生物 / synthetic biology
- AI / 人工智能
- 微生态 / microbiome
- 外泌体 / exosome

Event hints:

- PCHi
- 展会
- 峰会
- 研讨会
- 发布会
- 论坛
- 直播
- 报名

The Agent may use these hints as clues, but the final section decision must still cite article-level evidence from title or content.

## 6. Candidate Frameworks

### A. Full Tags Then Section Rules

Use the current full tagging workflow first, then derive newsletter sections by rules.

Process:

1. Run semantic tagging with the current taxonomy.
2. Output `primary_story_type`, `product_application`, `ingredient_technology`, `functional_claim`, `value_chain_stage`, and `company`.
3. Match `company` against a temporary Watchlist or `author_role_hint`.
4. Apply section mapping rules.
5. Store both the original tags and the derived section.

Section mapping examples:

- Competitor company plus product, technology, activity, cooperation, capacity, or finance signal -> `competitor_watch`.
- Customer brand plus ingredient, formula, claim, quality, or product signal -> `customer_watch`.
- Ingredient or functional theme is the main story -> `ingredient_trend`.
- Technology, process, research, AI, delivery, biotechnology, patent, or validation is the main story -> `technology_innovation`.
- PCHi, summit, webinar, forum, launch event, or exhibition -> `market_event`.
- Important high-level event suitable for TOP10 -> `market_brief`.

Use this as a comparison group, not the default recommendation.

Risk to measure:

- High token cost.
- More fields for the Agent to misclassify.
- Ambiguous mapping from tags to sections.
- Correct tags may still produce confusing section placement.

### B. Direct Section Classification

Let the Agent read the article and classify the newsletter section directly.

Output fields:

- `relevance`
- `primary_section`
- `secondary_sections`
- `section_confidence`
- `section_evidence`
- `needs_review_reason`

Do not require full taxonomy tags in this group.

Use this as the low-complexity baseline.

Risk to measure:

- Good for monthly report generation, but weak for search and later trend analysis.
- If section definitions change, old results may need retagging.

### C. Section First Plus Lightweight Tags

This is the recommended main candidate.

Process:

1. Agent first decides `primary_section` and `secondary_sections`.
2. Agent then outputs only lightweight supporting tags:
   - `company`
   - `ingredient_technology`
   - `functional_claim`
   - `product_application`
   - `primary_story_type`
3. Tags are used for evidence, search, filters, and report writing support.
4. Tags are not used as the sole engine for deriving the section.

Expected benefit:

- Lower complexity than full taxonomy-first tagging.
- More useful than direct section-only classification.
- Keeps article search possible, for example company search, ingredient search, and event search.

Risk to measure:

- Prompt must make section priority clear.
- Agent may still over-tag unless output rules are strict.

### D. Script Hints Plus Agent Section Classification

Use scripts for factual extraction and leave semantic section classification to the Agent.

Process:

1. Generate `fact_hints` from title and content using a simple alias table.
2. Agent reads `title`, `content`, `source_name`, `extraction_status`, and `fact_hints`.
3. Agent decides the section and may confirm or reject hints.
4. Agent must provide evidence for the final section.

Expected benefit:

- Lower token and reasoning cost.
- Better consistency for facts like company names, ingredients, and event terms.
- Useful for short or title-only articles.

Risk to measure:

- Alias tables may miss long-tail terms.
- Script hints may bias the Agent if not clearly marked as hints.

## 7. Section Definitions For The Test

Use these labels during the first test:

| Label | Meaning |
|---|---|
| `market_brief` | Important short-form event suitable for TOP10 market news cards. This is a highlight layer, not a normal content category. |
| `competitor_watch` | Competitor or ingredient supplier activity, including product launches, technology, cooperation, capacity, market entry, awards, events, or finance. |
| `ingredient_trend` | Ingredient, functional claim, consumer acceptance, application outlook, or market heat is the main story. |
| `technology_innovation` | Technology platform, research method, delivery system, AI, biotechnology, patent, validation, or R&D breakthrough is the main story. |
| `market_event` | Exhibition, forum, summit, webinar, seminar, conference, award, activity preview, or event recap. |
| `customer_watch` | Downstream customer brand article involving ingredient, formula, product claim, quality signal, product upgrade, or supply opportunity. |
| `exclude` | Not useful for Croda Beauty ingredient intelligence. |
| `needs_review` | Insufficient content, multiple equally plausible sections, weak evidence, or conflict between title and content. |

Priority guidance:

- If an article is only about an event invitation or event recap, prefer `market_event`.
- If an event article contains a major new product or technology announcement, allow `primary_section=market_event` and `secondary_sections` for the business topic.
- If a customer brand product launch is mainly about ingredient or formulation demand, prefer `customer_watch`.
- If the same article primarily explains an ingredient across brands or the market, prefer `ingredient_trend`.
- If the article is about how a technology works or how R&D is done, prefer `technology_innovation`.
- `market_brief` should be a separate highlight flag or secondary layer, not the only section for every important article.

## 8. Gold Standard Annotation

First create a gold-standard sample of about `120` articles.

Sampling plan:

- `70` articles with `content_length >= 800`.
- `25` articles with `300 <= content_length < 800`.
- `25` articles with `content_length < 300`.

Make sure the sample covers:

- industry media accounts
- PCHi
- competitor or ingredient supplier official accounts
- downstream brand/customer-related stories
- regulation or quality stories
- clearly irrelevant or low-value promotional articles

Human annotation fields:

| Field | Values |
|---|---|
| `article_id` | Source `id` |
| `title` | Source `title` |
| `source_name` | Source `author` |
| `relevance` | `relevant`, `not_relevant`, `unclear` |
| `primary_section` | One section label |
| `secondary_sections` | Array, may be empty |
| `must_include_in_report` | `yes`, `no` |
| `evidence` | Short human explanation |
| `content_quality_issue` | `none`, `short`, `empty`, `noisy_html`, `promotional` |
| `ambiguous` | `yes`, `no` |

If possible, two people should independently annotate the first 30 to 50 articles, then reconcile disagreements and update section definitions before annotating the rest.

## 9. Metrics

Core accuracy metrics:

- `primary_section_accuracy`
- `top2_section_recall`
- `per_section_precision`
- `per_section_recall`
- `per_section_f1`
- `confusion_matrix`
- `exclude_precision`
- `needs_review_rate`

Data-quality metrics:

- Accuracy on `success` articles.
- Accuracy on `partial` articles.
- Accuracy on `title_only` articles.
- Review rate on `empty` articles.
- Error rate for high-value official-account articles with short or empty body text.

Stability metrics:

- Run each framework three times on the same sample.
- Track `section_flip_rate`.
- Track confidence variance.
- Track whether evidence remains materially consistent.

Cost and workflow metrics:

- Average input tokens per article.
- Average output tokens per article.
- Average processing time per article.
- JSON or schema failure rate.
- Average number of tags per article.
- Human review load.

Business usefulness metrics:

- Whether each newsletter section gets enough candidate articles.
- Whether `market_brief` can produce a plausible TOP10.
- Whether search works for company, ingredient, functional claim, and event terms.
- Whether generated evidence is enough for the later report-writing Agent.

## 10. First Run Procedure

Run the first test on the 120-article gold-standard sample, not the full 499 articles.

Recommended order:

1. Run Framework B as the direct-section baseline.
2. Run Framework C as the main candidate.
3. Run Framework D to test whether script hints improve stability or reduce cost.
4. Run Framework A only on the `content_length >= 800` subset, so full taxonomy tagging is not unfairly penalized by empty content.

Compare outputs in one summary table:

| Framework | Primary accuracy | Top-2 recall | Needs review | Stability | Avg tokens | Search usefulness | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| A full tags then sections | TBD | TBD | TBD | TBD | TBD | High | Control group |
| B direct sections | TBD | TBD | TBD | TBD | TBD | Low | Baseline |
| C section plus lightweight tags | TBD | TBD | TBD | TBD | TBD | Medium-high | Main candidate |
| D script hints plus sections | TBD | TBD | TBD | TBD | TBD | Medium | Cost-optimized candidate |

## 11. Decision Rules

Use these rules after the first run:

- If C is as accurate as or more accurate than A, do not use full taxonomy formulas to derive sections.
- If B is close to C, keep section classification simple and add only the minimum tags required for search.
- If D improves stability or cost without hurting accuracy, move factual extraction to scripts.
- If A is clearly better only on full-body articles, keep full taxonomy tagging as a later enhancement rather than the MVP section-placement engine.
- If short official-account articles are often valuable but low-confidence, design a separate title-level preclassification and review queue.
- If `market_brief` behaves like a secondary highlight rather than a true category, model it as `is_market_brief_candidate` or `importance_score`, not as a mutually exclusive section.

## 12. Assumptions

- This test uses `all-articles(1).json` as an evaluation dataset, not as the final production clean JSON.
- The test does not validate database writes.
- The test does not validate final HTML rendering.
- The test does not validate real monthly time-window filtering.
- `publishTime` is not reliable enough for business date evaluation in this dataset.
- Tags are treated as support for search, filtering, evidence, and later analysis unless test results prove that full tag formulas are better for section placement.
