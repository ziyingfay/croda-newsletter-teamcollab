# HTML 月报 Demo 改造 PRD

> 状态：Confirmed for demo v1；已进入 fixture 与 HTML demo 实现。  
> 日期：2026-06-13  
> 范围：Croda Beauty 月度情报报告前端 demo、`report_content.json` 配置结构、交互需求。  
> 当前要求：按本 PRD 生成客户确认用 fixture 与 HTML demo；真实抓取、真实打标和正式渲染器仍不在本轮范围内。

---

## 1. 背景与当前进展

当前项目已经从旧目录迁移为 Croda 标准结构：

- 项目管理与参考资料在 `project-management/`。
- 产品代码、参数文件、运行输出在 `product/`。
- 月度 MVP 仍采用文件驱动链路：抓取/清洗 JSON → 小龙虾 1 栏目与轻量标签判断 → 小龙虾 2 报告内容 JSON → HTML 渲染。
- 最新栏目打标方案已从“完整标签反推栏目”调整为 V3/V4 的 C+D 两段式：脚本抽取事实和 spans，AI 整体判断栏目并输出轻量语义标签。
- V4 草稿已经吸收客户反馈：合并“成分趋势分析”和“技术创新追踪”，新增“法规政策”，将“KA 监测”列为正式栏目。

本次 PRD 面向客户确认用 HTML demo 的下一轮改造。目标不是先完成真实内容抓取或最终报告写作，而是冻结客户可见的页面结构、交互能力和配置渲染契约。

## 2. 产品目标

### 2.1 一句话目标

生成一个固定版式、配置驱动、可中英文切换、可查看术语解释的 Croda Beauty 月报 HTML demo，让客户确认最终月报前端会如何呈现。

### 2.2 业务目标

1. 让客户确认月报栏目结构、页面顺序和首页指标。
2. 让客户感知报告结构稳定、内容可追溯、每月版式一致；配置渲染和 `report_content.json` 属于内部实现口径，不作为客户演示时的主要表达。
3. 保留标签/栏目判断对报告的价值：栏目由 AI 一等判断，标签用于搜索、筛选、趋势聚合、证据追溯和术语解释。
4. 为后续正式 HTML 渲染器、报告内容 Agent 和 WorkBuddy 局部修改打基础。

### 2.3 非目标

- 本轮不实现真实抓取、真实打标、真实报告内容生成。
- 本轮不实现 React 前端代码或正式渲染器。
- 本轮不冻结最终视觉细节到像素级。
- 本轮不做数据库。
- 本轮不让 Agent 直接写 HTML。

## 3. 用户与使用场景

### 3.1 主要用户

- Croda Beauty 市场、竞争情报、BD、研发/产品相关团队。
- 内部项目团队，用于确认 `report_content.json` schema 和 HTML 渲染器开发范围。

### 3.2 核心场景

1. 客户打开 demo，查看月报首页、顶部数据卡片和栏目结构。
2. 客户按栏目浏览内容，看每个板块是否符合业务阅读习惯。
3. 客户一键切换英文，判断是否适合作为内部双语月报。
4. 客户在正文中 hover 或点击某个术语，查看 definition，理解系统如何解释标签、成分、技术或栏目名。
5. 客户点开某一个新闻卡片后，先看到放大的详情窗口：包含标签、文章标题、一段话新闻解释、媒体源和原文链接；点击链接可跳转到文章原链接。
6. 客户确认后，项目团队按该 PRD 进入固定版式和配置渲染开发。

## 4. 信息架构

### 4.1 页面整体结构

HTML demo 使用单页报告结构：

1. Header：报告标题、周期、客户标识、语言切换。
2. Toolbar：搜索、栏目跳转、导出 PDF、语言切换。
3. 顶部数据卡片：5 个固定 KPI。
4. 正文展示：1 个报告编排板块 + 5 个正式打标栏目。
5. 底部附录：数据来源与链接汇总。

### 4.2 顶部数据卡片

顶部必须展示以下 5 个数据卡片，按用户提供顺序呈现：


| 数值      | 中文说明               | 英文说明                                    |
| ------- | ------------------ | --------------------------------------- |
| `169`   | 2025年新原料备案数量（+88%） | 2025 new ingredient filings (+88%)      |
| `89.3%` | 国产新原料占比            | Share of domestic new ingredients       |
| `~$35B` | 全球化妆品原料市场规模        | Global cosmetic ingredients market size |
| `8.2%`  | 中国市场年复合增速          | China market CAGR                       |
| `30+`   | 本月监测竞品动态           | Competitor updates monitored this month |


约束：

- 这些数值在 demo 中作为长期固定 demo 指标。
- 正式版第一阶段不做 KPI 月度更新，仍沿用上述 5 个固定指标。
- 内部实现中 KPI 应进入 `report_content.json.kpis[]`，由渲染器读取，不散落写死在 HTML 正文中。
- 每个 KPI 需要支持来源或备注字段，便于后续追溯。

### 4.3 正文展示板块与正式栏目

客户确认后的 demo 栏目如下：


| 顺序  | 栏目 ID                   | 中文名              | 英文名                                  | 定位                                   |
| --- | ----------------------- | ---------------- | ------------------------------------ | ------------------------------------ |
| 1   | `market_flash`          | 市场快讯·本月热点事件 | Market Flash · Monthly Highlights     | 当月最值得快速浏览的重点事件卡片，最多 10 条                     |
| 2   | `competitor_watch`      | 竞品动态监测           | Competitor Watch                     | 国际/国内竞品及原料商的新品、技术、合作、投融资、产能等动态       |
| 3   | `ingredient_innovation` | 新成分 & 新趋势情报      | New Ingredients & Trend Intelligence | 合并原成分趋势与技术创新，覆盖新成分、递送、AI、合成生物、可持续工艺等 |
| 4   | `ka_watch`              | KA 监测            | KA Watch                             | MNC 与国内关键客户品牌的成分、功效、产品方向和潜在供应机会      |
| 5   | `market_event`          | 市场活动汇总           | Market Events                        | 展会、峰会、论坛、研讨会、CBE、竞品 seminar/webinar  |
| 6   | `regulation_policy`     | 法规政策             | Regulations & Policy                 | 新原料备案、法规、标准、认证、致敏原、监管动作              |
| 底部  | `source_appendix`       | 数据来源与链接汇总        | Sources & Links                      | 所有引用来源、原文链接、来源类型和对应栏目                |


重要变更：

- `market_flash` / 市场快讯·本月热点事件是报告 Agent 编排板块，不是小龙虾 1 的栏目标签；它从 5 个正式栏目中挑选最多 10 条最相关内容进入展示。
- 原“成分趋势分析”和“技术创新追踪”合并为“新成分 & 新趋势情报”。
- 原“重点客户监测”改为“KA 监测”。
- 新增“法规政策”正式栏目。
- 底部“数据来源与链接汇总”是附录，不参与 AI 的 `primary_section` 竞争。

## 5. 栏目与标签关系

### 5.1 栏目一等判断

正式流程中，栏目不由标签公式反推。小龙虾 1 应直接输出：

```json
{
  "section": {
    "primary_section": "competitor_watch",
    "secondary_sections": [],
    "evidence": {
      "trigger_span_id": "s3",
      "inferred_because": "竞品发布新原料"
    }
  }
}
```

HTML demo 需要表达这种关系：栏目是报告骨架，标签是辅助信息。`market_flash`
不进入小龙虾 1 输出，由报告 Agent 在内容编排阶段从各栏目候选里选出最多 10 条。

### 5.2 轻量标签的用途

轻量标签用于：

- 搜索：公司、成分、功效、应用场景。
- 筛选：只看某类成分、公司或功效。
- 图表：成分热度、竞品技术矩阵、功效分布。
- 术语解释：hover definition 可引用标签字典中的定义。
- 证据追溯：展示一条内容为什么进入某个栏目。

轻量标签不应在 HTML 中变成视觉噪音。每条内容最多展示 3 到 5 个关键标签。

## 6. 配置渲染需求

### 6.1 固定版式

HTML 模板应固定以下结构：

- 顶部 Header 和 KPI 卡片数量固定。
- 栏目顺序固定。
- 每个栏目内部支持不同 item 类型，但容器结构固定。
- 导航、语言切换、术语解释、链接附录是模板能力，不由 Agent 生成 HTML。

### 6.2 配置驱动

正式 HTML 不应手写业务内容。渲染器读取 `report_content.json`：

```text
product/output/result/report/<YYYYMM>/report_content.json
→ product/output/result/report/<YYYYMM>/report.html
```

渲染器职责：

- 读取 JSON。
- 渲染固定版式。
- 应用 Croda 品牌视觉。
- 渲染中英文文本。
- 渲染 tooltip definition。
- 渲染来源链接。

渲染器不得生成业务洞察、改写结论或补标签。

### 6.3 建议 `report_content.json` 顶层结构

```json
{
  "schema_version": "croda-report-content/v1-draft",
  "month": "202606",
  "title": {
    "zh": "市场监测月报",
    "en": "Market Intelligence Monthly"
  },
  "period": {
    "start": "2026-06-01",
    "end": "2026-06-30",
    "display_zh": "2026年6月",
    "display_en": "June 2026"
  },
  "language_default": "zh",
  "kpis": [],
  "sections": [],
  "glossary": [],
  "source_links": [],
  "render_options": {}
}
```

### 6.4 KPI 对象

```json
{
  "kpi_id": "new_ingredient_filings_2025",
  "value": "169",
  "label": {
    "zh": "2025年新原料备案数量（+88%）",
    "en": "2025 new ingredient filings (+88%)"
  },
  "source_ref_ids": ["src_001"],
  "note": {
    "zh": "Demo 固定数据，正式版本需绑定来源",
    "en": "Demo fixed data; final version requires source binding"
  }
}
```

### 6.5 Section 对象

```json
{
  "section_id": "ingredient_innovation",
  "title": {
    "zh": "新成分 & 新趋势情报",
    "en": "New Ingredients & Trend Intelligence"
  },
  "summary": {
    "zh": "聚合本月新成分、技术平台和趋势信号。",
    "en": "Aggregates new ingredients, technology platforms, and trend signals."
  },
  "items": []
}
```

### 6.6 Item 对象

```json
{
  "item_id": "competitor_watch_001",
  "article_ids": ["article_001"],
  "title": {
    "zh": "某竞品发布新型递送技术",
    "en": "A competitor launches a new delivery platform"
  },
  "facts": {
    "zh": "事实摘要。",
    "en": "Fact summary."
  },
  "insight": {
    "zh": "AI 草稿洞察，待业务确认。",
    "en": "AI-drafted insight, pending business review."
  },
  "detail": {
    "zh": "用于详情弹窗的一段话新闻解释。",
    "en": "One-paragraph news explanation for the detail modal."
  },
  "tags": ["encapsulation_delivery", "anti_aging"],
  "glossary_term_ids": ["encapsulation_delivery"],
  "source_ref_ids": ["src_001"],
  "review_status": "pending_review",
  "workbuddy_editable": true
}
```

## 7. 交互需求

### 7.1 一键切换英文

需求：

- 页面提供明显的语言切换控件，例如 `中文 / English`。
- 默认中文。
- 点击 English 后，标题、导航、KPI 标签、栏目标题、正文卡片、详情弹窗、完整正文、按钮和附录字段切换为英文。
- 再次点击或切换回中文后恢复中文。

实现原则：

- 正式版本不在浏览器端实时机器翻译。
- 中英文文本都来自 `report_content.json`。
- 第一阶段要求完整英文正文；如果 demo 某字段临时缺英文，优先显示中文并在内部 QA 中标记 `translation_missing`，避免客户看到空白。

验收标准：

- 切换不刷新页面。
- 切换后栏目顺序不变。
- 切换后搜索仍可对当前语言文本生效。
- 打印/PDF 使用当前语言状态。

### 7.2 Definition 解释功能

需求：

- 正文中的关键术语、标签、成分和栏目名可带 definition。
- 桌面端 hover 或 focus 时显示解释浮层。
- 移动端点击术语显示解释浮层，再点其他位置关闭。
- 解释内容支持中英文。

适用对象：

- 成分/技术：如 PDRN、多肽、包封/递送技术、合成生物学。
- 功效：如抗衰、屏障修护、促进渗透。
- 栏目概念：如 KA 监测、市场快讯、法规政策。
- 法规术语：如新原料备案、已使用化妆品原料目录、致敏原标识、功效宣称评价。
- 标签概念：如 `primary_section`、`secondary_sections`、`other:`。

建议 glossary 对象：

```json
{
  "term_id": "pdrn_nucleotides",
  "display": {
    "zh": "PDRN / 核酸原料",
    "en": "PDRN / nucleotides"
  },
  "definition": {
    "zh": "用于皮肤修护、再生或医美相关叙事的核酸类活性物。本定义为 demo 示例，正式版本以字典为准。",
    "en": "Nucleotide-based actives used in repair, regeneration, or aesthetics-related skincare narratives. Demo definition only."
  },
  "source": "tag_dictionary"
}
```

验收标准：

- tooltip 不遮挡正文关键内容。
- 支持键盘 focus。
- 支持移动端点击。
- glossary 缺失时术语正常显示，不报错。

### 7.3 搜索与筛选

Demo 至少保留搜索能力：

- 支持按公司、成分、功效、栏目、来源搜索。
- 搜索范围包括当前语言文本、标签和 glossary display。
- 后续可扩展栏目筛选、状态筛选、来源筛选。

搜索不是本轮最核心功能，但不能破坏语言切换与 definition。

### 7.4 导出与打印

Demo 需保留打印/PDF 入口。

约束：

- 打印使用当前语言。
- 打印时保留 KPI、栏目、来源链接。
- tooltip 不应在打印中悬浮显示。

### 7.5 新闻卡片详情弹窗

需求：

- 栏目中的新闻卡片默认保持轻量展示：标签、文章标题和一到两句话 summary。
- 点击卡片后打开详情弹窗或放大窗口。
- 详情窗口展示：关键标签、文章标题、一段话新闻解释、媒体源、发布时间、原文链接。
- 点击原文链接跳转到文章原链接。
- 详情窗口中的术语仍支持 definition hover/focus/click。
- 详情窗口中的中英文内容跟随全局语言切换。

验收标准：

- 桌面端弹窗不遮挡关闭按钮和来源链接。
- 移动端详情窗口可滚动，关闭后回到原栏目位置。
- 来源链接必须来自 `source_links[]`，不能由前端临时拼接。

### 7.6 WorkBuddy 局部修改示例

正式 HTML demo 保留 WorkBuddy 局部修改示例，用于说明后续客户可对单条内容进行改写、删除或移动，而不影响整份报告。

展示原则：

- 该能力作为 demo 中的“可编辑草稿示意”，不要求本轮实现真实后台编辑。
- 示例应围绕单条新闻卡片或单条栏目 item 展示。
- 可展示编辑状态，如 `待确认`、`已调整`、`建议重写`。
- 不把编辑控件做成客户必须学习的复杂后台界面。

## 8. 视觉与品牌要求

### 8.1 品牌优先级

视觉优先级：

1. Croda 客户公司官网和品牌绿色调。
2. 客户已有 WorkBuddy prototype 的月报阅读习惯。
3. kai-report-creator 的报告 shell 能力。

不得反过来以 ClawHub / kai-report-creator 配色覆盖客户品牌。

### 8.2 视觉方向

- 主色：Croda 深绿。
- 辅助色：植物绿、浅鼠尾草绿。
- 正文：中性深灰或深绿色黑。
- 背景：浅绿色或近白。
- 卡片：白底、细边框、轻阴影。
- 图表：低饱和绿色体系，避免装饰性强色。

### 8.3 响应式

- 桌面端：左侧或顶部导航均可，但客户阅读区必须清晰。
- 移动端：顶部控件可换行，不遮挡正文。
- KPI 卡片在移动端纵向排列。
- tooltip 在移动端改为点击浮层。

## 9. 各栏目内容展示需求

### 9.1 市场快讯·本月热点事件

展示方式：

- 最多展示 10 张事件卡片，不要求固定满 10 条。
- 若当月不足 10 条，则有多少放多少，不额外生成占位卡片。
- 每张卡片展示：序号、标题、事件类型、事实摘要、来源、关联标签。
- 支持点击跳到来源或展开详情。

Demo 数据可沿用旧 prototype 的 Dummy Data，但字段结构必须按配置渲染。

### 9.2 竞品动态监测

展示方式：

- 国际竞品、国内竞品可分组。
- 推荐使用表格或矩阵。
- 每条内容展示：公司、动态、涉及成分/技术、对 Croda 的意义、来源。

### 9.3 新成分 & 新趋势情报

展示方式：

- 合并成分与技术，不再拆成两个栏目。
- 可用趋势卡片、热度条或小图表。
- 每个趋势展示：核心成分/技术、代表文章、涉及公司、功效/应用、definition。

### 9.4 KA 监测

展示方式：

- 按 MNC / 国内 KA 分组。
- KA 名单直接沿用 V4 Watchlist，第一阶段不要求客户另行提供 priority KA 子名单。
- 每条内容展示：客户品牌、产品或卖点、涉及成分/功效、潜在供应机会、来源。
- 纯营销、纯代言、纯促销不纳入。

### 9.5 市场活动汇总

展示方式：

- 时间线或活动列表。
- 展示：活动名称、日期、地点、涉及公司、活动类型、与 Croda 的相关性。
- 注意 V4 规则：活动是“场合”，如果供应商在活动中发布新原料，主栏目可能是竞品动态或新趋势，活动作为 secondary section。

### 9.6 法规政策

展示方式：

- 规则/法规卡片或表格。
- 展示：法规标题、地区、时间节点、影响对象、对 Croda 的提示、来源。
- 支持 `definition` 解释监管术语。

### 9.7 数据来源与链接汇总

展示方式：

- 按栏目或来源类型分组。
- 每条来源展示：标题、来源名称、URL、对应栏目、对应 item_id。
- 链接可去重，但需保留一条链接被多个栏目引用的关系。

## 10. 验收标准

### 10.1 PRD 确认后 HTML Demo 验收

后续 HTML demo 进入实现时，应满足：

1. 顶部 5 个 KPI 按本 PRD 顺序显示。
2. 1 个报告编排板块、5 个正式打标栏目和底部来源附录齐全。
3. 成分/技术栏目合并为“新成分 & 新趋势情报”。
4. `KA 监测`、`法规政策` 为正式栏目。
5. 提供中文/英文一键切换，并覆盖完整英文正文。
6. 至少 8 个术语具备 definition hover/click 解释，范围覆盖标签、成分、栏目和法规术语。
7. 内容由配置对象渲染，不在 HTML 里散落业务正文。
8. 页面支持桌面和移动端，无横向溢出。
9. 打印/PDF 入口可用。
10. 新闻卡片可打开详情窗口并跳转原文链接。
11. 保留 WorkBuddy 局部修改示例。
12. 通过结构和视觉 QA 后再交付客户看。

### 10.2 配置验收

1. `report_content.json` 可被 `python3 -m json.tool` 解析。
2. 所有 section_id 在允许列表中。
3. 所有 item 至少有 title、facts 或 summary、source_ref_ids。
4. glossary term 被引用时必须能在 `glossary[]` 找到。
5. source_ref_ids 被引用时必须能在 `source_links[]` 找到。
6. 中英文字段缺失时有明确 fallback 策略。

## 11. 已确认口径

1. 顶部 KPI 的 5 个数字长期固定为 demo 指标，正式版第一阶段不做月度更新。
2. 英文版需要完整英文正文，不只是栏目标题、KPI、摘要和 tooltip 英文化。
3. Definition 的术语范围覆盖标签、成分、栏目和法规术语。
4. “市场快讯·本月热点事件”最多 10 条，不要求固定满 10 条；当月不足 10 条时有多少放多少。
5. KA 监测里的 KA 名单直接沿用 V4 Watchlist。
6. 正式 HTML demo 保留 WorkBuddy 局部修改示例。

## 12. 后续实施建议

本 PRD 已确认，当前进入 HTML demo v1 开发：

1. 已定义 `report_content.json` fixture。
2. 已实现固定版式 HTML demo。
3. 已用 fixture 同构数据渲染 demo HTML。
4. 已做桌面/移动端基础 QA。
5. 已做中英文切换、新闻详情弹窗、glossary tooltip 和搜索功能检查。
6. 下一步可交给用户/客户做视觉与内容口径确认。
