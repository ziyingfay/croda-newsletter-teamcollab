# 标签字段字典 · 禾大 Croda 美妆个护原料版 V4（草稿）

> **状态：草稿（DRAFT）**。V4 = **V3 的工程决策** + **客户（Qin, Betty）对 V2 问卷的反馈**。
> 客户反馈来源：`project-management/reference/.../Croda Beauty月报 - 栏目与标签体系确认清单_v260605.docx`
> （含 4 条批注 + 多处修订标记，批注/修订人 Qin, Betty，2026-06-11）。
>
> - 工程依据沿用 V3（Pilot-30 测试）：栏目 AI 判断、event 拆轴、事实降脚本、指针证据、取消置信度。
> - 客户反馈仅改"栏目结构"与"标签取值"，不改 V3 的判断机制；本版把两者合并。
> - V2 仍为旧基线；V3 为内部工程草稿；**V4 是当前最新草稿**。
> - schema 命名：`newsletter-tagging/croda-beauty-v4`（字典版本 `croda-beauty-2026-06-12-v4-draft`）

---

## V4 相对 V3 的变更（全部来自客户反馈）

| # | 变更 | 客户来源 |
|---|---|---|
| C1 | **合并"成分趋势分析"+"技术创新追踪"为一个栏目 `ingredient_innovation`（新成分&新趋势情报）** | 批注[5]"可合并…两个板块，新成分&新趋势情报" |
| C2 | **新增栏目 `regulation_policy`（法规政策）** | 批注[15]"可以增加法规新政策" |
| C3 | **`customer_watch` → `ka_watch`（KA监测），且为正式栏目（非标志位）** | 修订插入"KA监测"列 |
| C4 | **行业新闻快讯 / 热点新闻不作为打标栏目**：由报告 Agent 从各栏目候选中编排最多 10 条 | 用户 2026-06-16 澄清 |
| C5 | **删除 `color_cosmetics`（彩妆）；保留"卸妆"并入 `skincare`（面部清洁）** | 批注[28]"美妆不怎么做，可删除" + [29]"但是卸妆可以放" |
| C6 | **新增 `product_application`：`teen_age_care`（青少年护理）**；扩充 skincare/hair_care/men_care 范围 | 修订插入 |
| C7 | **新增 `functional_claim`：`hair_strands`（发丝）、`enhance_penetration`（促进渗透）** | 修订插入 |
| C8 | **`green_chemistry` → `sustainability_chemistry`（绿色化学/可持续工艺，重命名）** | 修订插入 "sustainability" |
| C9 | **`corporate_move` 典型场景补"高校合作"** | 修订插入 "、高校合作" |
| C10 | **Watchlist 名单按客户提供的 Excel 大幅补全**（MNC/国内品牌/竞品/代理商） | 修订插入完整名单 |
| C11 | **市场活动来源补 CBE、竞品 seminar/webinar** | 修订插入 |

> **需向客户说明的两处工程取舍（V3 决策，客户未反对，建议沟通确认）**：
> - **`event_news` 已从 story_type 移到脚本字段 `is_event`/`event_type`**（客户问卷 2.1 仍列 event_news，
>   那是 V2 残留）。市场活动栏目照常工作，活动只是"场合"不抢"实质"。
> - **行业新闻快讯 / 热点新闻是报告编排结果，不是打标栏目**：报告 Agent 从 5 个正式栏目中挑选
>   最相关的最多 10 条，形成"行业新闻快讯"板块；小龙虾 1 不输出 `industry_brief`、
>   `market_brief`、`market_flash` 或"热点新闻"标签。
>
> **待客户再确认的开放问题**（问卷里客户未明确答复）：
> - 删 `color_cosmetics` 后，`oral_care`（成人口腔护理）在客户新表里仅以"口腔护理"并入
>   `teen_age_care` 描述，**成人口腔护理暂无独立归属** —— 建议与客户确认是否单列。
> - 成分/技术是否补 Matrixyl® 系列、特定递送平台（问卷开放问，未答）。
> - 功效是否补"抗氧化""修护光损伤"（问卷开放问，未答）—— 暂不加，走活字典 `other:`。

---

## 一、报告栏目结构（5 个 AI 栏目 + 1 个报告编排板块 + 原文链接）

> **栏目改为平等多标签（取消 primary/secondary 分级，2026-06-17 用户决定）**：小龙虾 1 输出
> `section.sections`——一个**平等的栏目数组**。一篇文章若符合多个栏目，就**把符合的全部平等打上**
> （不判主次、不分等级）；之后由**报告 Agent** 决定是各栏目重复放置、还是择一最优落位。
> 打标这步**不判栏目优先级**，但仍须按下方标准/边界**只打真正符合的，不多打不乱打**。
>
> 取值：5 个正式栏目（可多选）；或系统态 `exclude` / `needs_review`（互斥，单独出现，不与正式栏目并列）。
> "行业新闻快讯 / 本月热点新闻"是报告展示板块，**不打标签**，由报告 Agent 从各正式栏目挑 ≤10 条编排。
> 原文链接为附录（脚本汇总，非分类目标）。

### 1.1 小龙虾 1 正式栏目（`section.sections[]`，平等多选）

| 栏目 | 客户栏目名 | 定位 |
|---|---|---|
| `competitor_watch` | 竞品动态监测 | 国际/国内原料商的新品、技术、合作、投融资、产能等动态 |
| `ingredient_innovation` | **新成分与新技术** | **（合并）** 热门成分与新兴技术的市场热度、应用方向、竞品布局；递送系统、AI 研发、合成生物、可持续工艺等前沿技术（栏目中文名 2026-06-18 由"新成分&新趋势情报"改为"新成分与新技术"；key 不变） |
| `ka_watch` | KA监测 | MNC 及国内品牌（关键客户）的原料相关动态、新品方向、技术合作 |
| `market_event` | 市场活动汇总 | 展会、峰会、论坛、研讨会、**CBE**、竞品 seminar/webinar 的预告与回顾 |
| `regulation_policy` | 法规新政策 | **（新增）** 新原料备案、法规、标准、认证、致敏原、监管动作 |
| `exclude` | —（系统态） | 对禾大原料情报无价值（纯促销、纯渠道、纯品牌、招聘等） |
| `needs_review` | —（系统态） | 正文不足、标题正文冲突等客观无法判定 |

### 1.2 报告展示板块（不进入小龙虾 1 标签）

| 报告板块 | 生成者 | 规则 |
|---|---|---|
| 行业新闻快讯 / 本月热点新闻 | 报告 Agent | 从 `competitor_watch`、`ingredient_innovation`、`ka_watch`、`market_event`、`regulation_policy` 中综合挑选最多 10 条最相关新闻；不要求小龙虾 1 输出热点标签 |
| 原文链接汇总 | 脚本 / 报告 Agent | 汇总本期引用文章的 URL、来源和栏目归属；不是分类目标 |

**归类规则（平等多选；符合就打，不符合不打；不判主次）：**
- 供应商/竞品在 webinar/展会发新原料/新技术 → 同时打 `competitor_watch` + `ingredient_innovation`
  + `market_event`（三者都符合就都打，平等）；`is_event=true`。
- 纯活动预告/会后流水（无实质内容）→ 只打 `market_event`。
- 多条不相关重大短讯汇编 → 把涉及到的正式栏目**都打上**；行业新闻快讯由报告 Agent 编排，不在此打。
- 下游 KA 品牌**且**涉及成分/配方/功效/采购 → 打 `ka_watch`（可与 ingredient_innovation 等并存）；
  **无成分角度 → 不打 ka_watch**（纯品牌营销/明星/公益/ESG/诉讼/人事/财报带货/渠道包装 → `exclude`）。
- 监管/备案/标准动作 → 打 `regulation_policy`（若同篇也讲成分趋势，就**同时**打 `ingredient_innovation`）。

> **平等多标签如何消解第三轮的"主次轮换"问题**：第三轮 probe 发现"哪个当 primary"会在共属栏目间
> 来回翻（克琴/德之馨这类原料商发新成分 = 竞品 + 成分 + 法规皆成立）。取消主次后，**这些栏目一律
> 平等打上、不再选主**，主次轮换的不稳定**从根上消失**；剩下的只是"某栏目算不算成员"的真判断，
> 交报告 Agent + 人工抽检即可。
>
> **唯一仍需把住的边界 = ka_watch ↔ exclude**：ka_watch 必须有真实成分/配方/功效/采购角度，
> "KA 品牌出现即收"是错的，宁可 exclude 也不滥收（reg↔ingredient 因平等多选已自然化解：两者都符合就都打）。

---

## 二、字段结构（三层，沿用 V3）

### 2.1 脚本字段（一级，入库脚本写入，Agent 不补全）

沿用 V3：`article_id`、`title`、`summary`、`content`、`url`、`published_at`、`source*`、
`content_language`、`market_region`、`extraction_status` 等，外加 V3 下放的：

| 字段 | 类型 | 说明 |
|------|------|------|
| `company` / `company_normalized` | string[] | 脚本 NER + Watchlist 别名表匹配（见第六节客户名单） |
| `ingredient_mentions` | string[] | 成分/技术别名表命中（仅抽取，主轴显著性留 Agent） |
| `is_event` / `event_type` | bool / enum | 活动场合（拆自旧 event_news）：`expo`/`webinar`/`forum`/`summit`/`award`/`launch_event`/`other` |
| `spans` | object[] | 标题+正文按句切分编号 `{id,text}`，供 AI `trigger_span_id` 指针引用 |
| `fact_hints` | object | 竞品/客户/成分/活动词命中（短文/空文线索） |

### 2.2 Agent 判断字段（**AI 只判这两类：relevance + sections**）

> 第三轮 A/B 测试定论：让 AI 在判栏目之外还打描述标签**不提升栏目、成本翻倍**。所以
> **AI 只做 relevance + sections**（+可选 report_guidance）；**其余描述标签全部由脚本生成**（见 2.3）。

| 字段 | 用途 | 约束 |
|------|------|------|
| `relevance` | 准入闸门 | `relevant`/`not_relevant`/`unclear`；下游品牌须涉成分/配方/采购/功效才算相关 |
| `section.sections` | 栏目落位（**平等多选数组**） | 5 个正式栏目可多选；或单独的 `exclude` / `needs_review`（系统态，不与正式栏目并列）。**不判主次、不分等级** |
| `section.evidence` | 证据 | `{trigger_span_id, inferred_because(≤20字)}`；指向促成归类的句子（多栏目可给多条 evidence_records） |
| `report_guidance` | **可选**：给报告 Agent 的一句话提醒 | **默认省略**；仅当有必须提醒的点才写，单条字符串（≤1 句） |

> **取消 `primary_section` / `secondary_sections` 主次分级**（2026-06-17 用户决定）→ 改 `sections[]` 平等多选。
> **取消 `confidence`**（V3 决策）；质量由人工抽检；`needs_review` 仅作客观状态。
> **取消 `is_market_brief_candidate` / `is_customer_watch_candidate` 标志位**：热点新闻由报告 Agent 编排。

#### `report_guidance` —— 给报告 Agent 的可选提醒（不是闸门，默认不写）

为**不增加打标 Agent 的复杂度**，这是个**可选的单条字符串**：**绝大多数文章不写**。只有当打标
Agent（作为文章首位完整读者）发现**有一个必须提醒报告 Agent 的点**时才补一句话——在复杂情况下
给报告 Agent 补上下文、或在下游模型能力不足时做辅助，建议怎么用也直接写在这句话里，不至于上下文爆炸。

> 例（路博润"全球首发丨邀您体验路家科技"，正文 4 字）：section=market_event（可落栏目，不进隔离），
> 补 `report_guidance: "仅活动预告无产品/技术细节，建议一句话带过或并入市场活动汇总"`。
> 普通有正文、内容充分的文章**不写 report_guidance**。
>
> 与隔离的区别：**判不了 → needs_review 隔离（不传下游）**；**判得了但有需提醒处 → 正常落栏目
> + 可选 report_guidance**。前者拦在打标，后者只是给精筛递个话。

### 2.3 脚本派生标签（**配置驱动，非 AI；2026-06-17 改**）

> 第三轮定论：除 relevance + sections 外，**其余标签一律由脚本在入库阶段生成**（关键词/别名表命中），
> 仅作展示点缀 + 搜索辅助。脚本不内嵌词表，全部读**配置文件**（改词表=改配置，不动代码）。

| 字段 | 谁生成 | 配置文件 | 状态 |
|------|--------|----------|------|
| `company` / `company_normalized` / `company_detail` | 脚本（别名匹配→display_name+role） | `watchlist/watchlist_entities_seed.json` | ✅ 已配置 + 已跑（450 篇） |
| `ingredient_mentions` / `ingredient_keys` | 脚本（别名命中） | `ingredient-alias/ingredient_alias_seed.json` | ✅ 已配置 + 已跑 |
| `is_event` / `event_type` | 脚本（关键词命中） | `event-keywords/event_keywords_seed.json` | ✅ 已配置 + 已跑 |
| `product_application` | 脚本（品类关键词命中） | `product-application/product_application_seed.json` | ✅ 配置已建 |
| `functional_claim` | 脚本（功效关键词命中） | `functional-claim/functional_claim_seed.json` | ✅ 配置已建；纯关键词精度有限（"是否真宣称"难判），仅作展示 |
| ~~`primary_story_type`~~ | — | — | ⛔ **已弃用**（2026-06-18，移入 archive，见下）|
| `value_chain_stage` | 脚本（二期，粗粒度） | 二期 | ⛔ 二期 |

> **`primary_story_type` 已弃用**：第三轮体检显示纯关键词无区分度（450 篇 94% 命中、多数同中 3–4 类），
> 栏目 `section` 已覆盖其大部分用途。词表与配置已归档：`tag-dictionary/archive/deprecated-primary_story_type-v4.md`、
> `parameter-file/archive/story-type/story_type_seed.json`，不再接入任何脚本。

> **重要权衡（脚本化的代价）**：纯别名/关键词脚本**抓不到字典外的新成分/新功效**（旧"活字典 `other:`"
> 靠 AI 语义发现，现已不在打标 Agent 里）。即**新趋势发现能力下降**——可接受，因为标签现仅作展示；
> 若后续要回补新词发现，需单独加一个轻量 AI 富化趟（不在 MVP 打标 Agent 主链路）。
> `functional_claim` 仍是关键词较难做准的一项（"是否真宣称"语义重），上线前需用真实数据评估
> "脚本版够不够展示用"，否则考虑降级。

---

## 三、标签词表（V4）—— 现作为**脚本配置文件的词源**

> ⚠️ 自 2026-06-17：以下词表**不再由 AI 判断**，而是作为 2.3 各脚本**配置文件的取值来源**
> （company/ingredient/event/product_application/functional_claim 配置均已建）。
> 词表内容保留不变，仅用途从"AI picklist"改为"脚本别名/关键词表来源"。

### 3.1 主故事类型 `primary_story_type` —— ⛔ 已弃用（2026-06-18）

> 第三轮体检显示纯关键词无区分度（450 篇 94% 命中、多数同中 3–4 类），栏目 `section` 已覆盖其用途，故弃用。
> 词表内容与配置已**归档（不删除）**：
> - 词表：`product/parameter-file/tag-dictionary/archive/deprecated-primary_story_type-v4.md`
> - 配置：`product/parameter-file/archive/story-type/story_type_seed.json`（已标 `_DEPRECATED`，不接入脚本）

### 3.2 产品/应用场景 `product_application`（多选，可空，活字典）

| 标签值 | 中文名 |
|--------|--------|
| `skincare` | 护肤（**面部清洁/卸妆**、面部护肤、精华、面霜、水乳、**面膜**） |
| `sun_care` | 防晒（防晒产品、防晒剂应用） |
| `hair_care` | 洗护发（洗发、**养护**、头皮护理、**护色**） |
| `body_personal_care` | 身体/个护（身体护理、沐浴） |
| `baby_care` | 母婴护理（婴幼儿/母婴个护） |
| `teen_age_care` | **青少年护理（头部洗护、面部洗护、身体洗护、口腔护理）** |
| `men_care` | 男士护理（面部护理、头发洗护、头发造型） |
| `fragrance_perfume` | 香水/香氛（香水、家居/身体香氛） |
| `other:<名>` | 字典外应用（如"医美级护肤""院线护理"，实时识别） |

> **C5 已删除 `color_cosmetics`（彩妆）**：客户"美妆不怎么做"；"卸妆"并入 `skincare` 的面部清洁。
> **开放问题**：成人 `oral_care` 暂无独立项（口腔护理目前仅在 `teen_age_care` 描述内），待客户确认。

### 3.3 成分/技术 `ingredient_technology`（多选，主轴维度，活字典）

**成分类**：沿用 V3（peptides、pdrn_nucleotides、ceramides、retinoids、retinol_alternatives、
recombinant_collagen、hyaluronic_acid、niacinamide、vitamin_c、probiotics_postbiotics、exosomes、
growth_factors、plant_botanical_extracts、marine_blue_biotech_actives、ergothioneine、
longevity_telomere_actives、acids_exfoliants、base_functional_raw）。

**技术类**（C8 改名）：

| 标签值 | 中文名 |
|--------|--------|
| `encapsulation_delivery` | 包封/递送技术 |
| `sustained_release` | 缓释/控释 |
| `synthetic_biology` | 合成生物学 |
| `fermentation_biotech` | 发酵/生物技术 |
| `sustainability_chemistry` | **绿色化学/可持续工艺**（原 `green_chemistry` 重命名） |
| `ai_rd_formulation` | AI 研发/配方 |
| `neurocosmetics_tech` | 神经美容技术 |
| `dual_targeting_delivery` | 双靶向递送 |
| `microfluidics` | 微流控 |
| `stem_cell` | 干细胞 |
| `other:<名>` | 字典外成分/技术（实时识别） |

> 抽取由脚本 `ingredient_mentions` 完成；本字段标主轴 + 补 `other:`。
> **开放问题**：是否补 Matrixyl® 系列、特定递送平台（客户问卷未答），暂走 `other:`。

### 3.4 功效宣称 `functional_claim`（多选，可空，活字典）

| 标签值 | 中文名 |
|--------|--------|
| `anti_aging` | 抗衰/抗皱 |
| `whitening_brightening` | 美白/提亮 |
| `moisturizing` | 保湿 |
| `barrier_repair` | 屏障修护 |
| `soothing_sensitive_skin` | 舒缓/敏感肌 |
| `acne_oil_control` | 祛痘/控油 |
| `sun_protection` | 防晒防护 |
| `firming_lifting` | 紧致提拉 |
| `microbiome_balance` | 微生态平衡 |
| `hair_scalp_care` | 发用/头皮功效 |
| `hair_strands` | **发丝** |
| `enhance_penetration` | **促进渗透** |
| `emotion_wellbeing` | 情绪护肤/愉悦 |
| `anti_glycation` | 抗糖化 |
| `blue_light_protection` | 抗蓝光 |
| `anti_pollution` | 抗污染 |
| `other:<名>` | 字典外功效（实时识别） |

> C7 新增 `hair_strands`、`enhance_penetration`。客户问卷提及的"抗氧化/修护光损伤"未确认，暂走 `other:`。

### 3.5 价值链阶段 `value_chain_stage`（单选，二期）

沿用 V3：MVP 置 null；二期启用粗粒度 `upstream`/`midstream`/`downstream`，
细分（raw_material_upstream … cross_chain）作二期增强。客户问卷词表与 V2/V3 一致，无改动。

### 3.6 公司 `company`（脚本抽取 + Watchlist 匹配）

脚本抽取，角色由 Watchlist 匹配（见第六节客户名单）。不进 taxonomy。

---

## 四、活字典 / 五、证据规则（沿用 V3）

- **活字典**：开放字段 `other:` 实时采集；频次晋升流程列二期。
- **证据规则（脚本切句 spans + AI `trigger_span_id` 指针）**：
  - 脚本派生标签（company/成分/活动/场景/功效）：无需 Agent 证据（脚本存命中位置）。
  - AI 判断（`relevance`、`section.sections`）：`trigger_span_id` + `inferred_because`；多栏目可多条 evidence_records。
  - 不设置信度；`needs_review` 仅客观状态；质量靠人工抽检。

---

## 六、Watchlist（客户/竞品监测名单）—— 按客户 Excel 确认

> Watchlist 是客户配置（落库 `watchlist_entities`），用抽取的 `company` 匹配出角色，不进 taxonomy。
> 以下为客户在确认清单中提供的名单（seed），与 `source_profiles_seed.json` 一并维护。

| 角色 `entity_role` | 名单 |
|---|---|
| `competitor`（国际原料商） | 巴斯夫、德之馨、赢创、瓦克、帝斯曼芬美意、亚什兰、路博润、森馨、嘉法狮、仙婷、科莱恩、世索科 |
| `competitor`（国内原料商） | 辉文生物、唯铂莱、克琴、JLand聚源生物、瑞吉明、维琪、辰海生科、瑞德林 |
| `channel_partner`（代理商） | 美in百好博、百好博致美堂、浦恩生化、萨科萨烁、上海万明生物、博烁个人护理、Ownsnow奥雪、奥利OLI、汇朗颜究院 |
| `customer`（MNC 品牌） | L'Oréal Paris、玉兰油、大宝、AHC、凡士林、施华蔻、沙宣、香缇卡、清扬、露得清、多芬、力士、旁氏、兰蔻、科颜氏、赫莲娜、雅诗兰黛、海蓝之谜、倩碧、CPB、IPSA、SK-II、优色林 |
| `customer`（国内品牌） | 韩束、一叶子、红色小象、newpage一页、珀莱雅、薇诺娜、润百颜、夸迪、米蓓尔、BM肌活、佰草集、丸美、完美日记、可复美、颐莲、瑷尔博士、自然堂、美肤宝、澳宝、HBN |
| `self` | 禾大 Croda |

> 别名归一化（如 L'Oréal=欧莱雅、禾大=Croda）由 Watchlist 维护；客户可继续增删。
> 别名表落库文件：`product/parameter-file/watchlist/watchlist_entities_seed.json`（脚本 company 抽取以 aliases 匹配并归一到 display_name）。

---

## 七、订阅来源（信源）—— 客户已确认

客户确认的订阅清单：行业媒体 13、国际原料商官方 13、国内原料商官方 7、国内代理商 9
（名单见确认清单第三节 / `WeChat Article Export_v260604.xlsx`）。**这是 `source_profiles` 的种子，
不属于本字典 taxonomy**；落库到 `source_profiles_seed.json`，由抓取脚本使用。

---

## 八、AI 打标约束（V4，**AI 只判 relevance + sections**）

> 描述标签（company/成分/功效/场景/活动）由**入库脚本**在打标前生成（见 2.3），AI 不碰；story_type 已弃用。

1. 沿用脚本字段（来源、语言、地区、`company`、`ingredient_mentions`、`is_event`、`spans` 等），不重算。
2. 判 `relevance`。
3. **判 `section.sections`（平等多选数组）**：把**所有真正符合的正式栏目都打上**，不判主次、不分等级、不输出置信度；
   每个归类给 `evidence`（trigger_span_id + inferred_because，多栏目可多条）。
   - 只打真正符合的：`ka_watch` 必须有成分/配方/功效/采购角度；纯品牌出现不算。不多打、不乱打。
   - `exclude` / `needs_review` 单独出现，不与正式栏目并列。
   - 判 section 前，必须依次穷尽"正文→标题→脚本字段→来源画像"才允许 `needs_review`（隔离，不传下游）。
   - 行业新闻快讯 / 热点新闻不在此输出，由报告 Agent 从各栏目挑 ≤10 条编排。
4. **（可选）`report_guidance`**：仅当有必须提醒报告 Agent 的点时补一句话；普通文章省略。不改栏目、不是闸门。

> AI 不再输出 ingredient_technology / functional_claim / product_application / value_chain
> （全部下放脚本，见 2.3；primary_story_type 已弃用并归档）；也不再做 `other:` 新词发现
> （脚本只命中已知词，新词发现能力下降，属已知权衡）。

---

## 九、脚本后处理：兜底"其他-X 待确认"标签（2026-06-18 新增）

> 这是一个**很小的脚本规则函数**，在"AI 出栏目 + 脚本出标签"之后跑，用来补齐"字典没收到的内容"。
> **不需要 AI 判断**，纯规则。

### 9.1 规则

对每篇文章，比对【AI 给的栏目】与【脚本打出的对应标签】，缺则补一个**通用待确认标签**（由脚本加，不是 AI）：

| AI 归入的栏目 | 脚本对应标签家族 | 若脚本该家族为空 → 自动补 |
|---|---|---|
| `ingredient_innovation`（新成分与新技术） | `ingredient_mentions`（成分/技术） | **`其他-成分技术`** |
| `ingredient_innovation`（新成分与新技术） | `functional_claim`（功效宣称） | **`其他-宣称`** |
| `regulation_policy`（法规与政策） | （法规细分标签，暂无）| **`其他-法规`** |
| `market_event`（市场活动汇总） | `event_type`/`is_event` | **`其他-活动`** |
| `competitor_watch` | — | **不补**（按用户决定，竞品不加 other） |
| `ka_watch` | — | **不补**（KA 不加 other） |

> 含义：AI 认定这篇属于"新成分与新技术 / 法规 / 活动"，但脚本字典没命中具体成分/功效/活动词
> → 说明很可能是**字典外内容**，补一个通用占位 `其他-X` 作为**待确认入口**，供人工在 HTML 审阅时处理。
> 说明：`其他-宣称`**只挂在 `ingredient_innovation` 栏目下**（成分/技术文才该有功效宣称）——不在
> 竞品/活动/法规等无功效角度的文章上触发，避免噪声。一篇成分文若 ingredient 和 claim 都没命中，
> 会同时拿到 `其他-成分技术` + `其他-宣称`（两个待确认维度，互不冲突）。

### 9.2 三条边界（务必遵守）

- **不判新旧**：系统**只**判"属于成分/技术相关内容"，**绝不**判断某成分是"新"还是"旧"。
  玻色因/依克多因/传明酸可能是老成分，但不在字典里——一律走 `其他-成分技术`（待确认），
  **新/旧由业务团队在报告审阅阶段人工定**。
- **当前不做活字典**：`其他-X` 是**通用占位**，**不是**具体新标签。**不要**让 AI/脚本自动生成
  `其他→玻色因`、`其他→依克多因` 这类具体新标签，也不自动入正式字典。先沉淀人工修改记录，
  跑几期后再统一看客户反复补了哪些，才决定是否纳入正式字典。
- **标签不承担报告正文责任**：标签只为筛选/归类/点缀展示。某篇讲了玻色因但没打出"玻色因"标签，
  **不代表报告里不能写玻色因**——报告撰写 Agent 会读标题/摘要/正文自行生成内容。**不要**为了"让报告
  写全所有成分名"而把打标做复杂。

---

*字典版本：croda-beauty-2026-06-12-v4-draft ｜ 基线：V3 工程草稿 + 客户 v260605 确认清单反馈 ｜
主要变更：合并成分趋势+技术创新为 ingredient_innovation、新增 regulation_policy 栏目、
customer_watch→ka_watch（升为栏目）、行业新闻快讯/热点新闻改为报告编排板块（不打标签）、删 color_cosmetics 保留卸妆、
新增 teen_age_care / hair_strands / enhance_penetration、green_chemistry→sustainability_chemistry、
corporate_move 补高校合作、Watchlist 按客户名单补全、**新增可选 `report_guidance` 字段**（默认省略，
仅在有必须提醒报告 Agent 的点时补一句 note，避免增加打标复杂度）、**明确 needs_review 隔离门槛**（穷尽
正文→标题→脚本字段→来源画像才隔离，且不传下游、待人工周期审计）｜
**2026-06-17 重大更新（按用户决定 + 第三轮定论）：①栏目取消 primary/secondary 主次分级 → `section.sections[]`
平等多选（符合就都打、不判主次，报告 Agent 再去重/择一）；②AI 只判 relevance + sections，其余描述标签
（company/成分/功效/场景/活动）全部下放脚本配置驱动（watchlist/ingredient-alias/event-keywords/
product-application/functional-claim 配置均已建，前三个已跑过 450 篇）；**story_type 已弃用并归档**
（纯关键词无区分度）；③已知权衡：脚本化后字典外新成分/新功效的"活字典发现"能力下降。** ｜
**2026-06-18 更新：①栏目"新成分&新趋势情报"中文名改为"新成分与新技术"（key ingredient_innovation 不变）；
②新增 §九 脚本后处理兜底"其他-X 待确认"（ingredient_innovation→其他-成分技术 / regulation_policy→其他-法规 /
market_event→其他-活动；competitor/ka 不补）；③明确不判新旧、当前不做活字典、标签不承担报告正文责任。** ｜
schema 名 newsletter-tagging/croda-beauty-v4 ｜
状态：草稿，待客户对栏目结构与开放问题最终确认后正式合入*
