# Croda Beauty HTML Demo 202606

Config-driven monthly-report demo, output in **two versions** for two stages.

- `report_content.json`: bilingual config fixture (KPIs, 6 sections, glossary, source links, V4 tag taxonomy). Single source of truth.
- `render_report.py`: renderer. Reads `report_content.json` and writes both HTML files. HTML owns only layout, interaction, brand visuals, and link display — all business content comes from the JSON.
- `report-internal.html` — **内部调整版**: draft for the internal team to review and request rewrites before publishing.
- `report-final.html` — **最终展示版**: clean final report shown after adjustment.

## Rebuild

```bash
python3 render_report.py        # report_content.json -> report-internal.html + report-final.html
```

Each HTML loads `report_content.json` via `fetch`, with an embedded copy as fallback so it also opens directly from `file://`.

## The two versions

Both share the same layout, data, KPIs, 6 fixed sections, appendix, bilingual toggle, glossary tooltips, search, V4 tag cascade filter, detail modal, and print/PDF. They differ only in the review controls:

| | 内部调整版 (internal) | 最终展示版 (final) |
|---|---|---|
| Mode banner | yes (amber) | no |
| Per-card status badge | none by default; `待修改` appears only when a rewrite suggestion is added | none |
| Per-card control | `✏️ 建议重写` button → free-text suggestion box | none |
| Bottom bar | `一键提交给报告 Agent` (collects all suggestions) | none |

### Internal review logic

- Cards that are fine need no action — no badge, no marking. Unmarked = confirmed.
- Click `✏️ 建议重写` on a card to open an input box; type the rewrite/delete request.
- Saving a suggestion flips the card's top-right status to `待修改` and highlights the card.
- Removing the suggestion clears it = confirmed.
- `一键提交` lists all suggestions and (in the real pipeline) sends them to the report Agent, which returns a new version. Demo only; not persisted.

## Layout & visual

Built on the client's reference demo layout (`project-management/reference/source-materials/croda-newsletter/市场监测月报_202605 workbuddy.html`), reskinned to the Croda deep-green brand palette per PRD §8.

## Notes

- 6 fixed sections: `market_flash`, `competitor_watch`, `ingredient_innovation`, `ka_watch`, `market_event`, `regulation_policy`; bottom `Sources & Links` appendix.
- Tags show only V4 dictionary fields, colored by V4 category; the date-adjacent chip shows section attribution; the toolbar section chips show a definition on hover.
- Chinese view avoids EN/CN mixing (source names are bilingual in the config).
- Dummy content for presentation/interaction confirmation only; no real crawling, tagging, or charts this round.
