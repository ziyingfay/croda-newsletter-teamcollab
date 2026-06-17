# Section-Tagging Test Plan — Revisions (v2)

This addendum amends the original `README.md` after the pilot-30 dry run
(see `product/output/test-results/section-tagging-test/analysis/pilot-30-findings.md`).
Keep the original as the canonical spec; apply the deltas below.

## R1. Fail fast: 30 before 120

Run a **pilot-30** (done) before committing two annotators to 120. The pilot already
shows the decisive structural result (formula loses), so we avoid annotating 120 under a
framework we are about to drop. Promote to the 120-article, two-annotator gold standard
**only after** the framework shape is locked and Alexi delivers a larger, time-windowed pull.

## R2. Reframe the experiment: it is "judgment vs formula", not "B vs C vs D"

With a single rater, B / C / D produce the **same section call** (the only difference is
whether tags ride along), so **section accuracy cannot discriminate B from C from D**.
The plan's headline A/B/C/D accuracy table is therefore only meaningful for **A vs the
rest**. Adjust expectations:

- **A vs judgment** is decided by section accuracy + junk-leakage (pilot: A loses).
- **B vs C** is decided by **downstream** metrics only — search recall and report-writer
  usefulness — never by section accuracy. State this in the metrics section.
- **C vs D** is decided by **factual-tag consistency and cost on short/empty articles**,
  not section accuracy.

To get a real section-accuracy spread you need **multiple independent raters/models**
(e.g. two human annotators + 2–3 model runs). Until then, treat the section number as a
self-consistency check, not a benchmark.

## R3. Make the relevance gate a first-class metric

The largest formula failure was **junk leakage** (9/30 non-relevant articles kept). Add as
top-line metrics, reported separately from section accuracy:

- `relevance_gate`: `wrongly_kept (junk)` and `wrongly_dropped (useful)` counts.
- `exclude_precision` / `exclude_recall`.

A framework can have decent section accuracy and still be unusable if it keeps promos and
channel news. The gate is evaluated *first*.

## R4. Name the hard-case suites and add tie-break rules to test

From the pilot, three reproducible hard cases deserve dedicated mini-suites and an explicit
rule each (test whether the rule holds):

1. **Event-vs-substance** (supplier launch/award *at* a webinar/expo). Candidate rule:
   `primary = market_event` only when the post is *primarily* a logistics/recap of the
   event; if a specific new ingredient/tech is the headline, `primary = competitor_watch`
   or `ingredient_trend`/`technology_innovation` and `market_event` goes to secondary.
2. **Roundup → market_brief** (several unrelated items in one post). Candidate rule: detect
   ≥2 unrelated lead items → `primary = market_brief`, components to secondary.
3. **Relevance borderline** (promo with real formulation content; brand story with faint
   ingredient angle; pure M&A). Candidate rule: the V2 gate — downstream/promo is relevant
   only if ingredient/formulation/procurement/claim is a *substantive* part, not a mention.

## R5. Stability run targets the ambiguous cluster, not the whole sample

Re-running all 30 three times wastes budget on stable articles. Run the **3× stability
pass on the ~22 ambiguous articles** (esp. the 8 `market_event` event-vs-substance cases),
and report `section_flip_rate` there. That is where flips actually live.

## R6. Model `market_brief` and `customer_watch` as flags

Pilot: `customer_watch` got zero primaries (overlaps `exclude`/`ingredient_trend`/
`technology_innovation`); `market_brief` is a highlight layer. Change the schema so both are
`is_market_brief_candidate` / `is_customer_watch_candidate` booleans (or secondary-only),
not mutually-exclusive primaries. Re-score with the reduced primary set
(`competitor_watch`, `ingredient_trend`, `technology_innovation`, `market_event`, `exclude`,
`needs_review`).

## R7. Split tags into "script-factual" vs "AI-semantic" in the test itself

The pilot's `fact_hints` (company, ingredient keyword hits, event terms) are exactly the
**factual** tags 陈炜/老燕 said a script should own. Make the test record, per framework,
which tags came from script vs AI, and measure factual-tag precision/recall against the
gold tags. This directly informs the Phase-1/2 split (which tags to script now, which to
leave to the Agent).

## R8. Add downstream-usefulness probes (cheap proxies)

Two lightweight checks the plan gestures at but should operationalize:

- **Search probe:** pick 3 queries (`欧莱雅`, `PDRN`, `PCHi`) and measure recall of the
  relevant pilot articles using only the emitted tags. Tests the search rationale for tags.
- **Report-writer probe:** for one section, feed the section's articles + tags + evidence to
  a drafting prompt and judge whether the evidence is sufficient to write the column without
  re-reading full bodies. Tests the "tags as report material" rationale.
