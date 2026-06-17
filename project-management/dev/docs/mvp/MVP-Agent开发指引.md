# MVP Agent 开发指引

> 本文档给后续 coding agent、openClaw 或其他执行型 Agent 使用。它不是项目计划，也不是完整 skill 包；目标是让 Agent 在开发 MVP 时知道该读什么、做什么、不要做什么。

---

## 一、先读什么

按渐进式披露读取，不要一次性把所有项目文档塞进上下文。

| 场景 | 必读文档 | 只在需要时读取 |
|------|----------|----------------|
| 开始任何 MVP 开发 | `project-management/dev/docs/MVP总体规划.md` | `project-management/dev/docs/项目管理文档.md` |
| 需要理解文件字段和输入输出 | `project-management/dev/docs/MVP关键工件契约.md` | `project-management/dev/docs/数据库设计.md` |
| 做小龙虾 1 打标 | `product/skills/newsletter-tagging/SKILL.md`、`product/skills/newsletter-tagging/references/workflow.md`、`product/skills/newsletter-tagging/references/llm_prompt.md` | `product/skills/newsletter-tagging/schemas/tag_output.schema.json`、`product/skills/newsletter-tagging/scripts/validate_tags.py` |
| 改标签口径 | `project-management/dev/docs/标签字段字典.md` | `product/skills/newsletter-tagging/references/标签字段字典.md` |
| 做 HTML 渲染 | `project-management/dev/docs/MVP关键工件契约.md` 的 `report_content.json` 部分 | `project-management/reference/source-materials/croda-newsletter/` prototype |
| 做数据库兼容 | `project-management/dev/docs/数据库设计.md` | `project-management/dev/docs/系统结构.md` |

关键工件契约不放在本文档中。需要字段结构、生成者、消费者、校验规则时，读取 `project-management/dev/docs/MVP关键工件契约.md`。

## 二、MVP 总原则

1. 当前主线是月度 JSON 工作流，不是数据库实现。
2. 所有运行工件放在 `product/output/result/<component>/<YYYYMM>/`。
3. 脚本写基础字段，Agent 写语义判断，渲染器写 HTML 版式。
4. 小龙虾 1 和小龙虾 2 必须分开，不要合并成一个“大而全” Agent。
5. 不要让 Agent 直接写 HTML。
6. 不要让渲染脚本生成业务洞察。
7. 不要删除或覆盖完整数据库设计；MVP 只保持兼容。
8. 不要新增质量评分类任务。

## 三、coding agent 可以做什么

coding agent 主要负责工程实现、校验和运行编排。

优先任务：

- 实现 `product/croda-backend/scripts/clean_rss.py --month <month>`，生成 `rss_clean.json`。
- 实现或完善 `tagging.json` validator。
- 实现 `product/croda-backend/scripts/build_report_context.py --month <month> --lookback 3`。
- 定义并校验 `report_content.json`。
- 实现 `product/croda-backend/scripts/render_report.py --month <month>`。
- 实现端到端控制脚本，写入 `run_log.json`。

开发要求：

- 先检查文件和目录是否存在，不要猜路径。
- 脚本通过 `--month` 参数定位 `product/output/result/<component>/<YYYYMM>/`。
- 每一步都要明确输入、输出和失败处理。
- 对 JSON 输出做格式化，方便人工阅读。
- 写入新工件前尽量保留运行日志，避免覆盖后无法追溯。
- 修改范围保持在 `product/croda-backend/`、`project-management/dev/docs/`、`project-management/dev/scripts/`、`product/skills/newsletter-tagging/` 等相关路径。

## 四、小龙虾 1：打标 Agent

输入：

- `product/output/result/spider/<YYYYMM>/<timestamp>-rss-clean.json + product/output/待打标.json`
- `project-management/dev/docs/标签字段字典.md`
- `product/skills/newsletter-tagging/references/llm_prompt.md`

输出：

- `product/output/result/tagging/<YYYYMM>/tagging.json`

职责：

- 判断文章是否与禾大美妆个护情报相关。
- 输出 6 类语义标签：`primary_story_type`、`product_application`、`ingredient_technology`、`functional_claim`、`value_chain_stage`、`company`。
- 为每个正式标签提供客观证据文本。
- 对需要人工复核的情况写入 `review_reasons`。

禁止：

- 不补写 `title`、`url`、`published_at` 等基础字段。
- 不生成报告段落。
- 不判断 HTML 版式。
- 不新增数据库写入逻辑。

验收：

- `tagging.json` 能通过 `product/skills/newsletter-tagging/scripts/validate_tags.py`。
- 每个 `article_id` 能在 `rss_clean.json` 找到。
- 抽样复核时，标签和证据能对应原文。

## 五、小龙虾 2：报告 Agent

输入：

- `product/output/result/spider/<YYYYMM>/<timestamp>-rss-clean.json + product/output/待打标.json`
- `product/output/result/tagging/<YYYYMM>/tagging.json`
- `product/output/result/report/<YYYYMM>/report_context.json`
- 近 3 个月最终报告摘要

输出：

- `product/output/result/report/<YYYYMM>/report_content.json`

职责：

- 判断哪些文章进入本期月报。
- 避免重复上月已经写过的同类叙事。
- 按固定 section 输出结构化报告内容。
- 保留每条内容对应的 `article_id` 和 URL。
- 输出执行摘要、关键洞察、行动建议和栏目内容。

禁止：

- 不直接输出 HTML。
- 不改小龙虾 1 的标签结果。
- 不绕过 `report_content.json` schema。
- 不把没有来源的判断写入报告。

验收：

- `report_content.json` 能被渲染脚本读取。
- 报告内容可追溯到原文。
- PM 或行业 Reviewer 能复核入选理由。

## 六、HTML 渲染 Agent / 脚本

输入：

- `product/output/result/report/<YYYYMM>/report_content.json`

输出：

- `product/output/result/report/<YYYYMM>/report.html`

职责：

- 根据固定模板、CSS 和 JavaScript 渲染报告。
- 支持客户确认的栏目、折叠、筛选、链接和打印/PDF 友好样式。
- 保证只改 JSON 就能稳定改变报告内容。

禁止：

- 不新增业务洞察。
- 不改写小龙虾 2 的正文含义。
- 不把内容散落写死在 HTML 模板中。

验收：

- 浏览器打开无明显版式错误。
- 所有链接可点击。
- section 顺序与 `report_content.json` 一致。
- 打印或导出 PDF 时核心内容不丢失。

## 七、控制脚本职责

控制脚本负责把步骤串起来，不负责业务判断。

建议顺序：

```text
clean_rss
→ run_tagging_json
→ build_report_context
→ run_report_agent
→ render_report
```

每一步都应记录到 `product/output/result/<component>/<YYYYMM>/run_log.json`：

- step 名称
- started_at / finished_at
- input / output
- status
- errors
- manual review notes

如果某一步失败，控制脚本应停止后续依赖步骤，并在日志中说明失败原因。

## 八、开发完成前检查

每次 Agent 完成一个任务前，至少检查：

1. 是否更新了相关项目文档或工作日志。
2. 是否保留了 MVP 与完整数据库版的边界。
3. 是否引用了 `project-management/dev/docs/MVP关键工件契约.md`，而不是临时发明字段。
4. 是否运行了能运行的 schema、语法或渲染检查。
5. 是否把发现的问题写入 `project-management/dev/docs/问题跟踪.md`。

## 九、不要做的扩展

以下任务除非用户明确要求，否则不要在 MVP 中实现：

- SQLite 入库。
- 跨月文章级检索。
- 后台管理界面。
- 历史重打标。
- 自动晋升活字典。
- Agent 直接生成最终 HTML。
- 把项目计划、客户沟通内容塞进 OpenClaw 执行 prompt。
