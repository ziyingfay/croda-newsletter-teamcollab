# 禾大 Croda Beauty Newsletter 需求分析报告

> 本报告基于 `reference/禾大newsletter/` 中的三份原型材料（`Beauty Monthly Report Prompt V1.docx`、`WeChat Article Export.xlsx`、`市场监测月报_202605 workbuddy.html`）反推客户的情报需求，并结合本项目现有的两层 MECE 标签体系（需求变更 009），为禾大定制 newsletter 与配套标签字典提供依据。
>
> 配套交付物：`标签字段字典-禾大美妆个护版.md`（同目录）。

---

## 一、客户画像

| 项 | 内容 |
|----|------|
| 客户 | 禾大 Croda（Croda Beauty / Croda 美妆个护事业部） |
| 客户身份 | **特种化学品 / 美妆个护原料供应商**（B2B 上游），不是品牌方 |
| 使用部门 | 市场部 / 竞争情报 / 研发与产品（RD & Product）/ BD |
| 行业 | 美妆个护原料（Beauty & Personal Care Ingredients），区别于本项目现有食品饮料字典 |
| 交付物 | 每月 1 日 09:00 自动生成的交互式 HTML 月报《市场监测月报_YYYYMM》，中英文双语，内部参考 |
| 核心定位 | Croda 作为原料商，需要监测**上游竞品原料商、平行代理商、下游客户品牌、行业媒体与法规**，并把动态对标到自身产品线（如 Matrixyl® 多肽系列） |

**关键判断：** 禾大与现有字典服务的"食品饮料"完全是另一个行业。现有字典（`industry_segment=finished_food/beverage/ingredients…`、`product_application=dairy/bakery…`、`strategic_driver=health_nutrition…`）**不能直接复用其词表**，但其**两层 MECE 架构、证据驱动、活字典、公司自由实体、无 confidence** 等设计原则完全适用，应当继承。

---

## 二、需求一：监测对象（公司 / 行业 / Topic / 媒体源）

### 2.1 监测的公司实体（按角色分层）

原型把监测对象明确分成五类角色，这正是禾大情报体系的核心结构。这些公司名单来自客户上传的 Excel（`美妆个护公众号list.xlsx`、`competitor PC list.xlsx`），属于**客户配置**，不进字典词表（遵循项目决策 009）。字典用 `entity_role`（仅表达"相对禾大的关系"：self/competitor/customer/channel_partner/ecosystem）+ `market_region`（国际/国内）+ `value_chain_stage`（链位置）三者组合来还原下表的五类角色，避免在单一字段里重复编码关系、地理与位置。

| 角色 | 代表实体（来自原型与 WeChat Export） | 情报用途 |
|------|--------------------------------------|----------|
| **国际原料商（竞品）** | 巴斯夫(BASF)、德之馨(Symrise)、赢创(Evonik)、瓦克化学(Wacker)、帝斯曼-芬美意(DSM-Firmenich)、亚什兰(Ashland)、路博润(Lubrizol)、森馨(Sennics)、嘉法狮(Givaudan)、仙婷(Sethic)、科莱恩/Lucas Meyer(Clariant)、世索科(Syensqo) | 竞品新品、技术、产能、合作监测 |
| **国内原料商（竞品/新锐）** | 辉文生物、唯铂莱(Viablife)、克琴(CoachChem)、JLand 聚源、瑞吉明、维琪(Winkey)、华熙生物、迪克曼、珈凯、STAREA 辰海 | 国产替代 / 出海 / 融资上市监测 |
| **代理商 / 分销** | 美in百好博、百好博致美堂、浦恩生化、萨科萨烁、上海万明、博烁、奥雪、奥利OLI、汇朗颜究院 | 渠道与原料流向信号 |
| **下游客户品牌（MNC）** | 雅诗兰黛、兰蔻、科颜氏、赫莲娜、海蓝之谜、倩碧、资生堂、CPB、IPSA、旁氏、凡士林、多芬、玉兰油、SK-II、妮维雅、优色林 | 客户需求与配方趋势信号、BD 机会 |
| **下游客户品牌（国内）** | 珀莱雅、薇诺娜、润百颜、夸迪、米蓓尔、BM肌活、佰草集、丸美、完美日记、可复美、自然堂、韩束、一叶子、红色小象、newpage一页、美肤宝 | 国货崛起、成分偏好、潜在客户 |
| **行业媒体（公众号/数据库）** | 硅碳鼠日化圈、美浪CBEAUTY、Fbeauty未来迹、美妆小报、美妆产品观、荣格个人护理、美丽修行App、PCHi、青眼、聚美丽、中国化妆品、化妆品观察品观、i美妆头条；SpecialChem、Research and Markets、Global Growth Insights | 资讯来源与趋势数据 |
| **自身** | 禾大 Croda（Matrixyl® Neolide 等） | 自家动态、媒体声量、对标基准 |

### 2.2 监测的 Topic / 关键词

原型 prompt 给定的关键词：`原料、成分、配方、新品、技术、创新` + 竞品名 + 明星成分（`视黄醇、烟酰胺、多肽、透明质酸、神经酰胺、益生菌、PDRN`）。

监测的内容主题（对应月报章节）：
- 资本市场 / 投融资 / IPO（如维琪科技北交所过会、瑞吉明 B 轮融资）
- 新品 / 新原料发布（如 Croda Matrixyl® Neolide、赢创 SPHINOX®、巴斯夫 Plantigenix™）
- 成分趋势（多肽、PDRN/核酸、神经酰胺、视黄醇替代、重组胶原蛋白、端粒/长寿成分）
- 技术创新（包封递送、AI 研发、神经美容、蓝生物技术、合成生物学、双靶向递送）
- 法规政策（新原料备案、欧盟致敏原标注、RSPO/可持续认证）
- 行业展会与活动（PCHi、in-cosmetics Global、ICIC、NYSCC Suppliers' Day）

### 2.3 媒体源需求

- **微信公众号**为最主要来源（25+ 行业公众号），故 `source_nature=wechat_public_account`、`ingest_method` 需支持公众号抓取（参考 `reference/wewe-rss/`）。
- 竞品官网新闻稿（`web_scraper`）、行业媒体报道、专业数据库（SpecialChem 等）、展会官方信息。
- 地域以**中国市场为核心**，同时覆盖欧美（in-cosmetics Global、欧盟法规）→ `market_region` 需要 china / global / europe / north_america / japan_korea / sea。
- 语言以**中文为主、英文为辅**，月报要求中英文切换 → `content_language` 主要 zh / en。

---

## 三、需求二：Newsletter 文章涵盖的内容与传达的 Insight

### 3.1 月报章节结构（即内容 Topic）

1. **市场快讯卡片**（TOP10 热点事件）——按事件类型打标签：资本市场、新品发布、行业展会、法规政策、技术创新、投融资。
2. **执行摘要**——关键洞察 + 行动建议（最高价值，需从打标结果聚合）。
3. **竞品动态监测**（国际/国内分类、对比矩阵）——分析维度 `product / technology / activity / cooperation`。
4. **成分趋势分析**（热门成分、新兴成分、趋势变化）。
5. **技术创新追踪**（递送系统、AI、生物技术、专利/研发）。
6. **市场活动汇总**（展会、发布会、研讨会）。
7. **数据可视化** + **附录原文链接汇总**。

### 3.2 每章的"深度分析"折叠板块（Insight 维度）

原型对每类内容定义了固定的深度分析框架，这是 newsletter 要传达的核心 insight，也直接指导我们要打哪些标签：

| 章节 | 深度分析维度 |
|------|--------------|
| 竞品动态 | 战略意图 + 市场影响 + 应对建议 + 置信度评分 |
| 成分趋势 | 技术原理 + 功效机制 + 市场接受度 + 应用前景 + **禾大对标分析** |
| 技术创新 | 技术成熟度 + 商业化潜力 + 竞争壁垒 + 跟进建议 |
| 市场活动 | 活动影响力 + 参与价值 + 后续跟进建议 + 竞品参与情况 |

### 3.3 原型中实际传达的 Insight（样例）

- **多肽赛道升温**（维琪上市、Croda Matrixyl® Neolide 发布需加速推广）
- **AI 研发成为标配**（路博润、亚什兰、MetaNovas 把生成式 AI 融入研发）
- **情绪护肤科学化 / 神经美容**（EEG 量化情绪调节）
- **可持续从加分到必修**（碳足迹、RSPO、生物质平衡；Matrixyl® Neolide 碳足迹降 43%）
- **国产原料加速出海**（辉文 HWPDRN®、柏垠可拉酸钠）

→ 这些 insight 都可分解为：**事件类型 + 成分/技术 + 功效宣称 + 战略驱动 + 涉事公司+角色**。这正是字典要承载的维度。

---

## 四、需求三：推测客户业务需求 / Newsletter 如何服务业务

| 业务场景 | Newsletter 如何服务 | 对应的标签筛选 |
|----------|---------------------|----------------|
| **竞争情报** | 及时掌握巴斯夫/德之馨/赢创等竞品的新原料、产能、合作、融资 | `entity_role=competitor` + `primary_story_type` + `company` |
| **产品/研发路线图** | 跟踪成分与技术趋势（多肽、PDRN、递送、合成生物、AI），决定 Croda 自研/引进方向 | `ingredient_technology` + `strategic_driver` + `functional_claim` |
| **市场定位 / 营销** | 用差异化卖点（碳足迹、缓释、功效验证）支撑 Matrixyl® 等自家产品推广 | `strategic_driver=sustainability/efficacy_science/delivery_technology` + `company=Croda` |
| **BD / 客户开发** | 监测下游 MNC 与国货品牌的成分偏好与新需求，发现合作机会 | `entity_role=customer` (× `market_region` 分 MNC/国货) + `functional_claim` + `product_application` |
| **法规合规** | 跟踪新原料备案、欧盟致敏原、可持续认证，保障出口合规与注册节奏 | `primary_story_type=regulation_policy` + `strategic_driver=regulation_compliance` |
| **国产替代 / 出海布局** | 评估国内新锐原料商威胁与海外扩张机会 | `strategic_driver=localization/globalization` + `market_region` |
| **投资 / 并购雷达** | 监测融资上市（维琪、瑞吉明）判断行业资本动向 | `primary_story_type=capital_finance` |

**结论：** 禾大 newsletter 的本质是**上游原料商视角的市场+竞争+技术+法规情报雷达**，每篇文章必须能回答"谁（公司+角色）做了什么（事件类型）、涉及什么成分/技术、宣称什么功效、为什么对 Croda 重要（战略驱动）、发生在哪个市场/价值链阶段"。日后所有 newsletter 都应围绕这套维度服务上述七类业务场景。

---

## 五、需求四：原型想实现的功能分析

| 功能 | 说明 | 对打标/字典的要求 |
|------|------|---------------------|
| 每月定时自动生成 | 月报，回溯 30 天 | 需 `published_at` 时间筛选、批处理 runner |
| 交互式 HTML + 中英双语 | 折叠章节、筛选器、图表、词云、搜索、PDF 导出 | `content_language`；标签需可聚合为筛选器维度（按竞品/时间/类型/成分） |
| 可点击有效链接 + 链接验证 | 所有新闻必须有有效原文链接 | `url/canonical_url`、`access_status`、`extraction_status` |
| 市场快讯 TOP10 卡片 | 事件分类标签 | `primary_story_type` 驱动卡片分类 |
| 竞品动态矩阵 | product/technology/activity/cooperation 四维 | `primary_story_type` + `entity_role=competitor` + `company` |
| 成分热度指数 / 备案量趋势图 | 数据可视化 | `ingredient_technology` 多选标签 + 计数聚合 |
| 深度分析（战略意图/对标/价值评估） | LLM 生成的二次洞察 | 依赖准确的一级标签作为输入；置信度由人工复核而非 AI 自评（遵循项目"无 confidence"原则） |
| 异常处理 | 抓取失败记录后继续、数据不足标注 | 对应 `extraction_status`、`needs_review`、失败分类 |

**注意事项（与本项目原则的衔接）：**
- 原型 prompt 要求竞品动态给"置信度评分"。但本项目决策 008 已明确**废弃 AI 自评 confidence**。建议禾大版同样不让 LLM 输出 confidence，置信度改由**证据强度 + 人工复核抽样**体现；如客户坚持要展示置信度，应在生成层用规则（来源性质 + 证据字段数）派生，而非让打标 LLM 自评。
- 深度分析（战略意图/对标/价值评估）属于 newsletter **生成阶段**的二次加工，不属于打标阶段；打标只负责输出客观可复现的受控标签 + 证据，深度洞察由后续生成 prompt 基于标签聚合产出。

---

## 六、对本项目字典设计的继承与差异

### 6.1 继承（保持不变的原则）
1. **两层模型**：基础数据字段（代码/规则）+ Agent 判断标签（LLM 语义）。
2. **MECE**：每字段一个独立维度，不跨字段重复。
3. **客户匹配导向**：字段必须能帮后端把文章匹配到客户关注的对象/议题。
4. **公司不入字典**：公司名自由实体抽取，watchlist 作为客户配置而非 taxonomy。
5. **证据驱动 + 无 confidence + 活字典候选机制（suggested_new_tags → 人工 qualification）**。

### 6.2 差异（针对禾大美妆个护重构的词表）
| 维度 | 食品饮料版 | 禾大美妆个护版 |
|------|-----------|----------------|
| `industry_segment` | finished_food/beverage/ingredients… | active_ingredients/functional_ingredients/finished_cosmetics/contract_manufacturing… |
| `product_application` | dairy/bakery/confectionery… | skincare/sun_care/color_cosmetics/hair_care/body_care… |
| `strategic_driver` | health_nutrition/clean_label… | sustainability/efficacy_science/delivery_technology/biotech/ai_rd/localization/globalization… |
| **新增 `functional_claim`** | （无，原 benefit_claim 已删） | 抗衰/美白/保湿/修护/祛痘/情绪护肤/微生态…（美妆功效是核心筛选维度，独立于战略驱动） |
| **新增 `ingredient_technology`** | （无） | 多肽/PDRN/神经酰胺/视黄醇替代/重组胶原/递送技术/合成生物…（成分与技术是月报主轴，活字典在此最活跃） |
| **新增 `entity_role`** | （无，纯自由实体） | self/competitor/customer/channel_partner/ecosystem（**仅关系轴**，与 value_chain_stage 解耦；地理交给 market_region，公司名仍自由抽取） |
| `value_chain_stage` | agriculture→consumer | upstream_raw_material→ingredient_active→formulation→contract_mfg→brand_product→channel→consumer |

详细词表见配套文件 `标签字段字典-禾大美妆个护版.md`。

---

## 七、风险与待确认事项

1. **置信度评分**：原型要求展示，项目原则禁止 AI 自评 confidence。需向客户确认改为"证据强度+人工复核"或规则派生（见 §5）。
2. **watchlist 来源**：监测公司名单来自客户 Excel，需作为客户配置文件维护，并定期与客户同步增删（如新增竞品、新锐原料商）。
3. **成分/技术词表的活字典节奏**：美妆新成分迭代极快（如外泌体、合成 PDRN、蓝生物技术）。已采用**内联 `other:<名>` 实时打标**机制（字典见 4.4.1）：字典外成分由 AI 实时打标、宁多勿漏，文章当下即可检索；后端按频次驱动晋升，人工只看高频列表批量审核（无需重读文章）。复核节奏建议每两周。
4. **下游品牌信号的相关性边界**：客户品牌新闻很多与原料无关（如代言、营销），需在 prompt 中强约束：只有当品牌新闻涉及**成分/配方/原料采购/功效宣称**时才打标，否则判 `no_matching_tag` 或低相关。
5. **双语**：抓取以中文公众号为主，月报需英文版，翻译属生成阶段，不影响打标，但 `content_language` 需准确以便分流。

---

*报告日期：2026-06-03 ｜ 基于 reference/禾大newsletter/ 原型材料反推 ｜ 配套字典见同目录*
