# MVP 总体规划

> 本文档定义当前 MVP 路线。MVP 采用**按月文件夹 + JSON 工件 + HTML 渲染**的轻量流程，目标是尽快稳定产出月度报告；完整数据库版本保留在 `dev/docs/数据库设计.md`，作为后续第二版接入方案。

---

## 一、MVP 定位

当前客户需求是**月度频次的行业情报报告**，核心交付物是每月一份可阅读、可交互、可复核的 HTML 月报。现阶段不需要复杂的历史数据管理、跨月检索、长期回填或多用户数据运营，因此 MVP 不实现数据库入库、状态机和长期存量维护。

MVP 的工程目标是：

- 每个月形成一个独立工作包，例如 `outputs/2606/`。
- 每一步都输出可读 JSON，方便人工查看、复核和调试。
- Agent 只处理当月数据，除“写报告”阶段读取过往 3 个月最终报告外，不依赖历史存量。
- HTML 版式由固定脚本渲染，报告内容由 JSON 配置驱动。
- 产物结构与完整数据库版字段保持兼容，未来可把月度 JSON 导入 SQLite。

## 二、MVP 与完整版本的边界

| 项 | MVP 版本（当前） | 完整版本（第二版） |
|----|------------------|--------------------|
| 数据组织 | 按月份文件夹组织 JSON / HTML | SQLite 表、视图、状态机 |
| 数据范围 | 当前月份为主；写报告时读取过往 3 个月最终报告 | 支持历史文章、重打标、活字典晋升、跨月查询 |
| 打标输入 | 干净 RSS JSON | `v_articles_for_tagging` |
| 打标输出 | `tagging.json` | `article_tags` + `tag_evidence` |
| 报告输入 | RSS JSON + 打标 JSON + 近 3 个月最终报告 | `v_monthly_report_articles` + `report_runs` |
| 报告输出 | `report_content.json` + HTML | HTML + JSON 摘要 + report_runs |
| 主要优势 | 快、可读、接近人工工作方式 | 可追溯、可统计、可长期运营 |
| 当前优先级 | 最高 | 保留设计，不做第一阶段实现 |

## 三、月度文件夹结构

建议每个月使用一个固定目录，短期采用用户现有口径：

```text
outputs/2606/
├── raw/
│   ├── rss_raw_*.json
│   └── fetch_log.json
├── rss_clean.json
├── tagging.json
├── report_context.json
├── report_content.json
├── report.html
└── run_log.json
```

| 文件 | 生成者 | 用途 |
|------|--------|------|
| `raw/rss_raw_*.json` | RSS 抓取脚本 | 原始抓取记录，保留排查线索 |
| `raw/fetch_log.json` | RSS 抓取脚本 | 抓取过程、失败源、跳过原因 |
| `rss_clean.json` | 清洗脚本 | 完整且干净的当月文章 JSON，是 Agent 输入 |
| `tagging.json` | 小龙虾 1 | 每篇文章的标签、证据、相关性判断 |
| `report_context.json` | 报告控制脚本 | 近 3 个月最终报告摘要 + 当月输入索引 |
| `report_content.json` | 小龙虾 2 | HTML 配置文件，决定本期报告写什么和怎么分区 |
| `report.html` | 渲染脚本 | 最终 HTML 月报 |
| `run_log.json` | 控制脚本 | 每步输入、输出、时间、错误和人工复核记录 |

## 四、MVP 流程

```text
RSS 抓取
→ 清洗为 rss_clean.json
→ 小龙虾 1 读取 rss_clean.json 并输出 tagging.json
→ 小龙虾 2 读取近 3 个月 final report + rss_clean.json + tagging.json
→ 小龙虾 2 判断入选文章并生成 report_content.json
→ HTML 渲染脚本读取 report_content.json
→ 输出 report.html
```

## 五、关键工件契约

### 5.1 `rss_clean.json`

目标：给打标 Agent 一个完整、干净、可复核的文章列表。

最小结构：

```json
{
  "month": "2606",
  "generated_at": "2026-06-04T00:00:00+02:00",
  "articles": [
    {
      "article_id": "stable_hash",
      "title": "...",
      "summary": "...",
      "content": "...",
      "url": "...",
      "canonical_url": "...",
      "published_at": "...",
      "source_key": "...",
      "source_name": "...",
      "ingest_method": "wechat_account",
      "source_nature": "wechat_public_account",
      "content_language": "zh",
      "market_region": ["china"],
      "raw_tags": []
    }
  ]
}
```

约束：

- 字段与 `dev/docs/标签字段字典.md` 的“基础数据字段”一致。
- 抓取失败记录不混入 `articles`，进入 `raw/fetch_log.json`。
- `article_id` 必须稳定，后续导入数据库时可复用。

### 5.2 `tagging.json`

目标：保存小龙虾 1 对当月文章的语义判断。

结构应兼容 `newsletter-tagging/schemas/tag_output.schema.json`：

```json
{
  "month": "2606",
  "dictionary_version": "croda-beauty-2026-06-04",
  "items": [
    {
      "schema_version": "newsletter-tagging/croda-beauty-v1",
      "article_id": "stable_hash",
      "relevance": "relevant",
      "tagging_decision": "tagged",
      "tags": {
        "primary_story_type": ["product_launch_or_update"],
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
- 开放字段可用 `other:<slug>`。
- 每个正式标签必须有 `evidence_text`。

### 5.3 `report_context.json`

目标：让小龙虾 2 知道过去 3 个月写过什么，避免重复叙事，并延续趋势判断。

最小结构：

```json
{
  "month": "2606",
  "previous_reports": [
    {
      "month": "2605",
      "path": "outputs/2605/report.html",
      "summary": "...",
      "covered_companies": ["..."],
      "covered_topics": ["..."],
      "open_followups": ["..."]
    }
  ]
}
```

### 5.4 `report_content.json`

目标：作为 HTML 渲染配置文件。小龙虾 2 只负责生成结构化报告内容，渲染脚本负责版式。

建议结构：

```json
{
  "month": "2606",
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
- HTML 里所有可点击链接来自 `source_links` 或 section item 的 `url`。
- 渲染脚本不得自由生成业务内容，只读取 JSON。

## 六、三类工作进度

### 6.1 项目规划与交付物目标

阶段目标：

1. 与客户确认标签分类和 Watchlist 角色口径。
2. 确认报告栏目、入选标准、深度分析颗粒度和最终 HTML 交付标准。
3. 确认 MVP 只交付月度文件夹工件，不做数据库实现。
4. 确认 HTML prototype 版式后冻结第一版渲染结构。

任务拆分：

| 任务 | 输出 | 验收 |
|------|------|------|
| 标签口径确认 | `dev/docs/标签字段字典.md` v2 确认版 | 客户接受字段、标签、Watchlist、活字典机制 |
| 报告标准确认 | 报告栏目和 section schema | 客户知道每章写什么、不写什么 |
| MVP 范围确认 | 本文档 + 里程碑 | 团队认同先 JSON 后数据库 |
| HTML 样式确认 | `report_content.json` schema + HTML prototype | 改 JSON 可稳定影响报告内容 |

### 6.2 脚本部分

阶段目标：

1. 抓取后生成 `rss_clean.json`。
2. 建立 HTML 渲染脚本，让 `report_content.json` 稳定渲染为 `report.html`。
3. 调优 JavaScript 和 CSS，使筛选、折叠、图表、打印/PDF 友好。

任务拆分：

| 模块 | 任务 | 输出 |
|------|------|------|
| RSS 清洗 | 合并原始 RSS、去重、字段补全、剔除失败项 | `rss_clean.json` |
| JSON 校验 | 校验 `rss_clean.json`、`tagging.json`、`report_content.json` | schema / validator |
| HTML 渲染 | 将配置 JSON 渲染成固定版式 | `report.html` |
| 前端交互 | 折叠、筛选、搜索、图表、打印/PDF | JS/CSS |
| 样式调优 | 按客户确认版修改视觉层级、卡片、表格、图表 | HTML/CSS |

### 6.3 Agent 与控制脚本

阶段目标：

1. 小龙虾 1 跑通“文章 → 标签 JSON”。
2. 小龙虾 2 跑通“过往报告 + 当月文章/标签 → 报告内容 JSON”。
3. 控制脚本负责编排步骤、传入上下文、收集错误、写日志。
4. 多智能体分角色协作，避免一个 Agent 同时做打标、选题、写作和版式。

任务拆分：

| Agent / 脚本 | 职责 | 输入 | 输出 |
|--------------|------|------|------|
| 控制脚本 | 调度月份目录、校验输入输出、写 `run_log.json` | month 参数 | 月度工件 |
| 小龙虾 1：打标 | 判断文章相关性、标签、证据、公司实体 | `rss_clean.json` | `tagging.json` |
| 小龙虾 2：报告策划/写作 | 读取过往报告，选择本期入选内容，写报告 JSON | `rss_clean.json` + `tagging.json` + `report_context.json` | `report_content.json` |
| 渲染脚本 | 固定版式渲染 HTML | `report_content.json` | `report.html` |
| 人工复核 | 检查入选文章、关键洞察、链接、版式 | 全部工件 | 修改意见 |

## 七、阶段计划

### Phase 0：MVP 方案冻结

目标：确认“不先做数据库，以月度 JSON 工作包为 MVP”的项目路线。

完成标志：

- 本文档进入 `dev/docs/`。
- `项目管理文档`、`系统结构`、`里程碑检查清单` 与本文档一致。
- 数据库设计保留为完整版本，不作为 MVP 阻塞项。

### Phase 1：月度输入清洗

目标：从 RSS/raw 记录生成完整干净的 `rss_clean.json`。

任务：

- 定义 `outputs/2606/` 目录约定。
- 定义 `rss_clean.json` schema。
- 编写或整理清洗脚本。
- 用 2606 样本跑通一次。

### Phase 2：小龙虾 1 打标 JSON

目标：让 Agent 基于 `rss_clean.json` 输出稳定 `tagging.json`。

任务：

- 将 `newsletter-tagging` workflow 从数据库入口改为兼容 JSON 入口。
- 校验 `tagging.json`。
- 抽样人工复核标签质量。

### Phase 3：HTML 渲染脚本

目标：先把 `report_content.json` 渲染成稳定 HTML。

任务：

- 设计 `report_content.json` schema。
- 从 prototype 拆出 HTML 模板、CSS、JS。
- 实现渲染脚本。
- 验证只改 JSON 即可改变报告内容。

### Phase 4：小龙虾 2 报告 JSON

目标：让 Agent 读取近 3 个月最终报告和当月 JSON，输出可渲染的 `report_content.json`。

任务：

- 定义“入选本期报告”的规则。
- 定义“避免重复上月内容”的规则。
- 定义每个 section 的写作要求和字段。
- 跑通 `report_content.json` 生成。

### Phase 5：客户验收与迭代

目标：让客户确认报告分类、内容标准和 HTML 展示。

任务：

- 交付一版 2606 HTML。
- 根据客户反馈调整标签、栏目、样式。
- 固化 MVP 操作流程。

## 八、与完整数据库版的兼容策略

为了未来能重新接入数据库，MVP 需要遵守以下规则：

1. `article_id` 稳定，未来可直接作为 `articles.article_id`。
2. `rss_clean.json.articles[]` 字段命名与 `articles` / `article_contents` 保持一致。
3. `tagging.json.items[]` 与 `newsletter-tagging` schema 保持一致，未来可拆入 `article_tags` / `tag_evidence`。
4. `report_content.json` 保留 `article_id` 和 URL，未来可关联 `report_runs`。
5. 活字典 `other:<slug>` 不在 MVP 阶段强制晋升，但要保留 `extracted_name`，未来可导入 `inline_other_terms`。
6. 月度文件夹不要写死数据库假设；完整版本通过 adapter 导入 JSON，而不是重写 Agent 逻辑。

## 九、当前不做的事

- 不实现 SQLite 入库与状态机。
- 不实现跨月全文检索。
- 不实现长期历史重打标。
- 不实现复杂后台管理界面。
- 不让 Agent 直接写 HTML。
- 不让渲染脚本生成业务洞察。
