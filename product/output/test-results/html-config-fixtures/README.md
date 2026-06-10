# HTML 配置测试样例说明

本目录保存 3 份基于链接导出文件生成的 `report_content` 测试配置，用于开发和测试禾大 Croda 月报 HTML 渲染器。

## 最终交付物判断

根据现有 MVP 文档、禾大 newsletter 需求和 3 个 HTML 链接导出，最终客户交付物应是：

- 按月生成的静态 HTML 月报：`product/output/result/report/<YYYYMM>/report.html`。
- HTML 内容由 `report_content.json` 驱动，渲染器只负责版式、导航、卡片、图表和链接。
- Agent 2 输出 `report_content.json`，并通过 `article_id` 回连 `rss_clean.json` 和 `tagging.json`。
- 月报栏目至少覆盖：市场快讯、执行摘要与行动建议、竞品动态、成分趋势、技术创新、重点客户、市场活动、数据可视化、附录原文链接。
- 渲染器需要支持中文、英文、双语标题、锚点导航、重复 URL 去重、长标题、外链附录和来源域名图表。

## 文件

| 文件 | 用途 |
|---|---|
| `report_content_2605_workbuddy_cn.fixture.json` | 中文 workbuddy 风格报告测试配置；无原始锚点，测试默认导航、中文长标题、重复外链与附录。 |
| `report_content_2605_bilingual_nav.fixture.json` | 双语完整导航测试配置；保留原始 8 个锚点，测试双语标题、导航和栏目顺序。 |
| `report_content_2605_en.fixture.json` | 英文报告测试配置；测试英文标题、英文卡片、英文附录和无锚点时的默认导航。 |

这些配置来自 `project-management/reference/source-materials/croda-newsletter/link_exports/` 中的链接导出文件。它们是开发和测试 fixture，不代表最终报告正文质量；真实洞察与正文应由小龙虾 2 基于 `rss_clean.json`、`tagging.json` 和 `report_context.json` 生成。
