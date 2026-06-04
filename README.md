# 禾大 Croda 情报订阅 Agent 工作区

Repository: `corda-newsletter`

这是为客户**禾大 Croda Beauty / Croda 美妆个护事业部**定制的行业情报订阅项目工作区。

项目已从上一代“食品饮料 RSS 抓取 + newsletter 打标”模板迁移为禾大专属项目。旧食品饮料代码、字典和数据流说明已归档到 `reference/legacy-food-beverage/`，仅作为方法论和实现参考；当前活跃文档、标签字典和打标 skill 均以禾大美妆个护原料情报场景为准。

## 项目目标

构建一套面向禾大的情报订阅 Agent，按月自动监测美妆个护原料行业动态，并生成可交互、可追溯、可筛选的市场监测月报。

核心问题是帮助禾大回答：

- 哪些竞品、国内新锐原料商、代理商、客户品牌和行业机构出现了重要动态？
- 这些动态涉及什么成分、技术、功效、法规、市场活动或商业动作？
- 它们对 Croda 的产品推广、研发路线、BD、法规合规和竞争策略有什么意义？
- 哪些信息应进入月报、趋势图、竞品矩阵、成分热度榜和行动建议？

## 客户资料

| 路径 | 说明 |
|------|------|
| `reference/禾大newsletter/Beauty Monthly Report Prompt V1.docx` | 客户提供的月报生成 prompt，定义运行频率、报告结构、链接、双语、交互和质量要求 |
| `reference/禾大newsletter/WeChat Article Export.xlsx` | 客户提供的监测对象清单，包括行业媒体、国际/国内原料商、代理商、MNC 客户品牌和国内品牌 |
| `reference/禾大newsletter/市场监测月报_202605 workbuddy.html` | 客户提供的交互式 HTML prototype，定义月报栏目、卡片、图表和深度分析形式 |
| `outputs/禾大Croda/禾大Croda-Newsletter需求分析报告.md` | 已完成的客户需求分析与项目背景反推 |
| `outputs/禾大Croda/标签字段字典-禾大美妆个护版.md` | 已完成的禾大美妆个护定制标签字段字典 |

## 工作区结构

```text
newsletter 字典/
├── app/
│   └── README.md                    # 后续放禾大正式应用代码
├── newsletter-tagging/              # 禾大版结构化打标 skill、prompt、schema、validator
├── dev/
│   ├── docs/                        # 项目计划、需求、系统、数据库、问题、测试、里程碑
│   ├── notes/                       # 工作日志
│   ├── scripts/                     # 后续项目脚本
│   └── temp/                        # 临时工作区
├── outputs/禾大Croda/               # 当前客户交付文档
└── reference/
    ├── 禾大newsletter/              # 客户 prototype 原始资料
    ├── wewe-rss/                    # 微信公众号/RSS 服务化参考
    └── legacy-food-beverage/        # 上一代食品饮料项目归档
```

## 当前状态

- 禾大项目背景：已根据客户 Word、Excel、HTML prototype 梳理完成。
- 禾大标签字典：已作为当前活跃字典同步到 `dev/docs/标签字段字典.md` 和 `newsletter-tagging/references/标签字段字典.md`。
- 打标原则：沿用字段/标签分离、MECE、证据驱动、公司自由实体和活字典机制。
- 打标主轴：`primary_story_type`、`product_application`、`ingredient_technology`、`functional_claim`、`value_chain_stage`、`company`。
- 旧项目清理：食品饮料抓取代码、旧字典、旧数据流说明已归档；缓存、`node_modules`、`.git`、`.DS_Store`、`__pycache__` 已清理。

## 下一阶段

1. 跑通 `outputs/<month>/rss_clean.json`，把当月 RSS 原始记录整理成干净文章 JSON。
2. 跑通小龙虾 1，读取 `rss_clean.json` 并输出 `tagging.json`。
3. 跑通 HTML 渲染脚本，读取 `report_content.json` 稳定输出月报。
4. 跑通小龙虾 2，读取近 3 个月最终报告、当月 RSS JSON 和打标 JSON，输出 `report_content.json`。
5. 在 MVP 稳定后，再评估是否接入 `dev/docs/数据库设计.md` 中的完整数据库版本。

详细计划见 `dev/docs/项目管理文档.md` 和 `dev/docs/里程碑检查清单.md`。
