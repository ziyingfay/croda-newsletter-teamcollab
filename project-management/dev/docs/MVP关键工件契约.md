# MVP 关键工件契约

> 本文档定义 MVP 月度工作包中的关键文件契约。`project-management/dev/docs/MVP总体规划.md` 只描述项目计划与团队协作；具体字段、生成者、消费者、校验规则以本文档为准。

---

## 一、目录约定

每个自然月使用 `YYYYMM` 作为月份目录。各组件只通过 `product/output/result/` 交换公开工件：

```text
product/output/result/spider/<YYYYMM>/
├── raw/
│   └── rss_raw_*.json
├── fetch_log.json
├── <timestamp>-rss-clean.json
└── run_log.json

product/output/待打标.json

product/output/result/tagging/<YYYYMM>/
├── tagging.json
└── run_log.json

product/output/result/report/<YYYYMM>/
├── report_context.json
├── report_content.json
├── report.html
└── run_log.json
```

`<YYYYMM>` 采用六位自然月编号，例如 `202606`。所有脚本和 Agent 必须通过月份参数定位文件，不应写死某个月份。

## 二、工件总览

| 工件 | 生成者 | 消费者 | MVP 用途 | 完整版本映射 |
|------|--------|--------|----------|--------------|
| `raw/rss_raw_*.json` | RSS 抓取脚本 | 清洗脚本、排查人员 | 保存原始抓取记录 | `article_import_runs.raw_payload` |
| `raw/fetch_log.json` | RSS 抓取脚本 | PM、工程、QA | 记录成功、失败、跳过和异常 | `article_import_runs` |
| `rss_clean.json` | 清洗脚本 | 小龙虾 1、小龙虾 2、QA | 当月干净文章列表 | `articles` + `article_contents` |
| `tagging.json` | 小龙虾 1 | 小龙虾 2、QA | 文章语义标签和证据 | `article_tags` + `tag_evidence` |
| `report_context.json` | 报告控制脚本 | 小龙虾 2 | 近 3 个月报告摘要和去重线索 | `report_runs` 摘要层 |
| `report_content.json` | 小龙虾 2 | HTML 渲染脚本、QA | HTML 报告配置文件 | `report_runs.report_payload` |
| `report.html` | HTML 渲染脚本 | 客户、PM、QA | 最终月报 | `report_runs.output_path` |
| `run_log.json` | 控制脚本 | PM、工程、QA | 运行过程、输入输出、错误、复核记录 | `tagging_runs` / `report_runs` |

## 三、`raw/rss_raw_*.json`

目标：保留抓取入口返回的原始记录，便于排查来源失败、字段缺失、重复链接和正文抽取问题。

要求：

- 文件名应包含来源或批次，例如 `rss_raw_wechat_001.json`、`rss_raw_trade_media.json`。
- 原始字段可保留来源差异，不要求统一为标准字段。
- 不作为 Agent 直接输入。
- 不应在清洗时覆盖；重复运行应生成新批次或在 `fetch_log.json` 记录覆盖原因。

## 四、`raw/fetch_log.json`

目标：记录 RSS/公众号抓取过程，让 PM 和工程可以判断本月输入是否完整。

最小结构：

```json
{
  "month": "202606",
  "started_at": "2026-06-04T10:00:00+02:00",
  "finished_at": "2026-06-04T10:30:00+02:00",
  "sources": [
    {
      "source_key": "example_source",
      "source_name": "Example Source",
      "status": "success",
      "raw_file": "raw/rss_raw_example_source.json",
      "items_found": 20,
      "items_kept": 18,
      "errors": []
    }
  ]
}
```

约束：

- `status` 建议使用 `success`、`partial`、`failed`、`skipped`。
- 抓取失败只进入日志，不混入 `rss_clean.json.articles`。
- 每个异常应有可读 `errors[]`，用于复盘而不是让 Agent 猜测。

## 五、`rss_clean.json`

目标：给打标 Agent 一个完整、干净、可复核的当月文章列表。

最小结构：

```json
{
  "month": "202606",
  "generated_at": "2026-06-04T11:00:00+02:00",
  "source_files": ["raw/rss_raw_example_source.json"],
  "articles": [
    {
      "article_id": "stable_hash",
      "raw_ref": {
        "raw_file": "raw/rss_raw_example_source.json",
        "raw_item_index": 0
      },
      "title": "...",
      "summary": "...",
      "content": "...",
      "content_length": 1200,
      "url": "...",
      "canonical_url": "...",
      "published_at": "...",
      "fetched_at": "...",
      "source_key": "...",
      "source_name": "...",
      "source": "wechat_domestic_media",
      "source_list": ["croda_beauty_customer_excel_industry_media"],
      "ingest_method": "wechat_account",
      "content_language": "zh",
      "market_region": ["china"],
      "extraction_status": "success",
      "raw_tags": []
    }
  ]
}
```

约束：

- 字段应与 `project-management/dev/docs/标签字段字典.md` 的基础数据字段保持一致。
- `article_id` 必须稳定，同一 URL 或 canonical URL 重复处理时保持同一 ID；它是 `rss_clean.json`、`tagging.json`、`report_content.json` 的主串联键。
- `raw_ref` 用于回溯原始抓取记录，建议至少包含 `raw_file` 和 `raw_item_index`；它不参与打标判断。
- `source_key/source_name` 必须能匹配 `source_profiles`；`source`、`source_list`、默认 `ingest_method`、默认 `content_language` 和默认 `market_region` 由该配置派生。
- `articles[]` 只包含可供阅读和打标的文章；失败项、死链、无正文等记录进入 `fetch_log.json`。
- 基础字段由脚本写入，小龙虾 1 不补全这些字段。

## 六、`tagging.json`

目标：保存小龙虾 1 对当月文章的语义判断。

结构应兼容 `product/skills/newsletter-tagging/schemas/tag_output.schema.json`：

```json
{
  "month": "202606",
  "dictionary_version": "croda-beauty-2026-06-04",
  "items": [
    {
      "schema_version": "newsletter-tagging/croda-beauty-v1",
      "article_id": "stable_hash",
      "relevance": "relevant",
      "tagging_decision": "tagged",
      "tags": {
        "primary_story_type": ["product_launch_or_update"],
        "product_application": ["facial_skincare"],
        "ingredient_technology": ["peptides"],
        "functional_claim": ["anti_aging"],
        "value_chain_stage": "ingredient_active",
        "company": ["Croda"]
      },
      "evidence_records": [
        {
          "field": "ingredient_technology",
          "label": "peptides",
          "evidence_text": "..."
        }
      ],
      "review_reasons": []
    }
  ]
}
```

约束：

- 不输出基础字段；基础字段来自 `rss_clean.json`。
- 每个正式标签必须有对应 `evidence_text`。
- 开放字段可使用 `other:<slug>`，并保留可读名称，便于后续活字典审核。
- `items[].article_id` 必须能在 `rss_clean.json.articles[]` 中找到。

## 七、`report_context.json`

目标：让小龙虾 2 知道过去 3 个月写过什么，避免重复叙事，并延续趋势判断。

最小结构：

```json
{
  "month": "202606",
  "lookback_months": 3,
  "previous_reports": [
    {
      "month": "202605",
      "path": "product/output/result/report/202605/report.html",
      "summary": "...",
      "covered_companies": ["..."],
      "covered_topics": ["..."],
      "open_followups": ["..."]
    }
  ]
}
```

约束：

- 上月内容只作为去重和延续判断，不作为小龙虾 1 的打标输入。
- 如果某个月缺少最终报告，应在 `run_log.json` 记录，不阻塞当月打标。
- 摘要应保留栏目、公司、成分/技术和未完待续线索。

## 八、`report_content.json`

目标：作为 HTML 渲染配置文件。小龙虾 2 负责结构化报告内容，渲染脚本负责版式。

建议结构：

```json
{
  "month": "202606",
  "title": "市场监测月报",
  "period": "2026-06-01 至 2026-06-30",
  "summary": {
    "key_insights": [],
    "actions": []
  },
  "sections": [
    {
      "section_id": "market_flash",
      "title": "市场快讯",
      "items": []
    },
    {
      "section_id": "competitor_watch",
      "title": "竞品动态监测",
      "items": []
    },
    {
      "section_id": "ingredient_trends",
      "title": "成分趋势分析",
      "items": []
    },
    {
      "section_id": "technology_innovation",
      "title": "技术创新追踪",
      "items": []
    },
    {
      "section_id": "customer_watch",
      "title": "重点客户监测",
      "items": []
    },
    {
      "section_id": "events",
      "title": "市场活动汇总",
      "items": []
    },
    {
      "section_id": "appendix",
      "title": "原文链接汇总",
      "items": []
    }
  ],
  "charts": [],
  "source_links": []
}
```

约束：

- 每条报告内容必须能追溯到 `article_id` 和 URL。
- HTML 中所有可点击链接来自 `source_links` 或 section item 的 `url`。
- 渲染脚本不得自由生成业务内容，只读取 JSON。
- 小龙虾 2 不直接输出 HTML、CSS 或 JavaScript。

## 九、`report.html`

目标：最终客户可阅读的 HTML 月报。

要求：

- 由固定渲染脚本读取 `report_content.json` 生成。
- 支持客户确认的栏目结构、链接、折叠/筛选、打印或 PDF 友好样式。
- 业务内容应可从 `report_content.json` 找到来源，不应在 HTML 中出现脚本额外生成的洞察。

## 十、`run_log.json`

目标：记录端到端运行过程，便于复盘、排错和项目管理。

建议结构：

```json
{
  "month": "202606",
  "runs": [
    {
      "step": "clean_rss",
      "started_at": "...",
      "finished_at": "...",
      "input": ["raw/rss_raw_example_source.json"],
      "output": "rss_clean.json",
      "status": "success",
      "notes": []
    }
  ],
  "manual_reviews": [
    {
      "reviewer": "PM",
      "artifact": "report_content.json",
      "reviewed_at": "...",
      "decision": "approved_with_changes",
      "notes": ["..."]
    }
  ]
}
```

约束：

- 每次自动化运行都应写入 step、输入、输出、状态和错误。
- 人工复核结论应进入 `manual_reviews[]`，不要只留在聊天记录中。
- 若重复运行同一步，应保留足够信息判断哪一次输出被用于最终报告。

## 十一、通用验收规则

1. 路径固定：公开工件必须位于 `product/output/result/<component>/<YYYYMM>/`；唯一例外是固定打标交接文件 `product/output/待打标.json`，它必须与对应 spider archive JSON 内容一致。
2. JSON 可读：所有 JSON 应格式化，便于人工审阅。
3. ID 可追溯：报告内容、标签输出和原文必须通过 `article_id` 串联。
4. 职责分离：脚本写基础字段，Agent 写语义判断，渲染器写版式。
5. 数据库兼容：MVP 字段命名尽量贴近 `project-management/dev/docs/数据库设计.md`，未来通过 adapter 导入。
