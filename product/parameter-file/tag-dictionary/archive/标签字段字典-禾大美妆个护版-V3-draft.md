# 标签字段字典 · 禾大 Croda 美妆个护原料版 V3（草稿）

> **状态：草稿（DRAFT）**。本版在 V2 基础上，落地 Pilot-30 测试结论：
> ①栏目改为 AI 一等判断，不再用标签公式反推；②把"活动"从 story_type 拆成独立轴；
> ③事实类标签的"抽取"降回脚本字段；④证据分层。**正式合入需等客户确认栏目框架后**，
> 在此之前 `标签字段字典-禾大美妆个护版-V2.md` 仍为对客确认基线。
>
> - 测试依据：`project-management/dev/docs/section-tagging-test/团队分享-栏目打标测试.md`、
>   `标签体系优化建议-v2.md`、`product/output/test-results/section-tagging-test/analysis/pilot-30-findings.md`
> - schema 命名：`newsletter-tagging/croda-beauty-v3`（字典版本 `croda-beauty-2026-06-11-v3-draft`）

---

## V3 相对 V2 的变更摘要

| # | 变更 | 原因（来自 Pilot-30） |
|---|---|---|
| 1 | **新增 `section` 一等判断**（primary_section + secondary + confidence + needs_review） | 标签公式反推栏目 30 篇错 18 篇；栏目必须 AI 整体判断 |
| 2 | **`market_brief` / `customer_watch` 改为标志位**，不是互斥主栏目 | customer_watch 主栏目命中 0；market_brief 是高亮层 |
| 3 | **`primary_story_type` 剔除 `event_news`**，新增独立 **`is_event` + `event_type`** 轴 | "活动"标签劫持一切，场合与实质不在同一轴 |
| 4 | **`company`、成分/技术"抽取"降为脚本字段** | 字面命中率 company 94% / 成分 96%，脚本可抽 |
| 5 | **证据改为"脚本切句 + AI 指针"**：脚本把正文切成带编号的句子，AI 只回 `trigger_span_id` + `inferred_because`，不再转写引文 | AI 转写引文耗输出 token、且会改写/幻觉；切句是机械活，交脚本 |
| 6 | **取消置信度（confidence）**：AI 不自评置信度，质量由**人工抽检**保证 | 不让 AI 自评质量；`needs_review` 仅作客观状态保留 |
| 7 | **`value_chain_stage` 降为二期**，并粗粒度化（上/中/下游） | 测试显示是判断而非映射，非 MVP 必需 |

---

## 设计原则（V3 更新）

1. **栏目是判断，不是公式**：文章落哪个栏目由 Agent 读懂全文后**整体判断**
   （`section.primary_section`），**不再**由标签按规则反推。标签只做描述、搜索、证据。
2. **字段 vs 标签 vs 判断三分**：
   - **脚本字段（一级）**：ID、来源、语言、地区、URL、时间、**公司实体、成分/技术抽取、
     活动场合**——由抓取/清洗脚本写入，Agent 不重算。
   - **Agent 一等判断**：`relevance`（准入闸门）、`section`（栏目落位）。高风险、驱动输出。
   - **Agent 语义标签（二级）**：需读懂语义才能判的描述维度（story_type、功效判定、
     成分主轴/新词、价值链）。低风险，供搜索/证据/趋势。
3. **正交分轴（MECE）**：每个维度只回答一个切面；"场合"（活动）与"实质"（story_type）
   分开，互不争夺"决定栏目"的权力。
4. **MECE 优先、不盲目细分**：同义不跨字段重复；不能稳定提升筛选价值的维度删除/降期。
5. **公司不入字典词表**：公司名由脚本抽取写 `company`；角色由 Watchlist 匹配（见第七节）。
6. **证据驱动、分层精简**：见第六节——关键判断证"判断链"，描述标签只给定位。
7. **活字典（Picklist）**：开放维度（成分/技术、应用、功效）字典外值写 `other:<名>`，
   频次驱动人工晋升（晋升流程列二期，见第五节）。

---

## 一、字段结构（三层）

### 1.1 脚本字段（一级，入库脚本写入，Agent 不补全）

> 在 V2 基础字段（`article_id`、`title`、`summary`、`content`、`url`、`published_at`、
> `source*`、`content_language`、`market_region`、`extraction_status` 等，**沿用 V2 第三节**）
> 之上，V3 把以下原属 Agent 的"抽取类"维度**降为脚本字段**：

| 字段 | 类型 | 脚本处理方式 | MVP | 说明 |
|------|------|--------------|-----|------|
| `company` | string[] | NER + Watchlist 别名表匹配（命中即带出角色） | ✅ | 字面命中 94%；Agent 不再自由抽取，只在脚本漏抽时补充 |
| `company_normalized` | string[] | 别名归一化（欧莱雅=L'Oréal） | ✅ | 供搜索与 Watchlist 匹配 |
| `ingredient_mentions` | string[] | 成分/技术别名表命中（多肽、PDRN、合成生物…） | ✅ | 字面命中 96%；**只做抽取**，主轴显著性留 Agent（见 1.3） |
| `is_event` | bool | 活动关键词命中（PCHi、展会、研讨会、webinar、发布会、回顾、预告…） | ✅ | 拆自旧 `event_news`；只判"是否经活动发布" |
| `event_type` | enum/null | `expo`/`webinar`/`forum`/`summit`/`award`/`launch_event`/`other` | ✅ | 关键词初判，Agent 可在 section 证据中确认 |
| `fact_hints` | object | 竞品/客户/成分/活动词命中列表（测试期已用） | 🔸 | 给短文/空文当线索 |
| `spans` | object[] | 正文按句切分，每句 `{id, text}` 编号 | ✅ | 供 AI 用 `trigger_span_id` 指针引用证据，免转写 |

> `spans` 切句规则（脚本）：按 `。！？；\n` 等终止符切分标题+正文，去空、编号
> （`s0`=标题，`s1..`=正文句）。AI **只引用 id**，不复制原文，杜绝转写漂移与幻觉。

> 脚本字段不写进 `article_tags` 关联表；Agent 只读取作上下文。`company` 角色
> （竞品/客户/代理/生态）由后端用 `company` 匹配 Watchlist 得出，不由 Agent 判。

### 1.2 Agent 一等判断（高风险，驱动输出）

| 字段 | 类型 | 用途 | 约束 | MVP |
|------|------|------|------|-----|
| `relevance` | enum | 准入闸门 | `relevant`/`not_relevant`/`unclear`；下游品牌新闻须涉成分/配方/原料采购/功效才算相关 | ✅ |
| `section.primary_section` | enum | 栏目落位（唯一主栏目） | 见第二节标签集；整体判断，非标签反推 | ✅ |
| `section.secondary_sections` | enum[] | 次要栏目 | 可空；跨栏目时承载次要主题 | ✅ |
| `section.is_market_brief_candidate` | bool | 是否市场快讯/TOP10 高亮 | 高亮层标志，非互斥栏目 | ✅ |
| `section.is_customer_watch_candidate` | bool | 是否下游客户监测线索 | 标志位，非互斥栏目 | ✅ |

> **已取消 `confidence`**：不让 AI 自评置信度，质量由**人工抽检**保证。
> `needs_review` 不再作为"AI 不确定"的自评信号，改为**客观状态**：仅当
> ①正文空/极短无可判证据，或②标题与正文出现事实冲突时，`primary_section=needs_review`。
> 它是一个**离散判定结果**（与 `exclude` 并列），不是质量打分。

### 1.3 Agent 语义标签（二级，描述/搜索/证据）

| 字段 | 类型 | 用途 | 约束 | MVP |
|------|------|------|------|-----|
| `primary_story_type` | tag[] | 文章**实质**是哪类事件（**不含活动**） | 多选≥1；活动已拆到 `is_event` | ✅ |
| `ingredient_technology` | tag[] | 成分/技术**主轴 + 新词** | 多选；脚本抽取已在 `ingredient_mentions`，此处只标**主轴**并补 `other:<名>` | ✅ |
| `functional_claim` | tag[] | 宣称功效（**判定**，非关键词命中） | 多选；纯营销词不填；字典外 `other:` | 🔸 |
| `product_application` | tag[] | 产品品类/应用场景 | 多选；脚本可初抽，Agent 兜底；字典外 `other:` | 🔸 |
| `value_chain_stage` | enum/null | 产业链位置（**二期**，粗粒度上/中/下游） | 单选；MVP 可置 null | ❌二期 |

> 说明：`ingredient_technology` 的"抽取"已由脚本 `ingredient_mentions` 完成；Agent 在
> 本字段只回答"**哪个是这篇的主轴成分/技术**"以及"字典外是否有新成分要 `other:`"——
> 即**判显著性 + 补新词**，不重复抄词。

---

## 二、栏目板块定义（一等判断标签集）

> 栏目即客户月报的板块。MVP 主栏目为互斥单选；`market_brief`、`customer_watch`
> 作为**标志位/次要栏目**叠加。

| 主栏目 `primary_section` | 含义 |
|---|---|
| `competitor_watch` | 竞品/原料供应商动态：新品、技术、合作、产能、出海、获奖、法务、融资等 |
| `ingredient_trend` | 成分/功效/消费者接受度/应用前景/市场热度为主线 |
| `technology_innovation` | 技术平台、研究方法、递送系统、AI、生物技术、专利、机理验证、研发突破为主线 |
| `market_event` | 展会、论坛、峰会、webinar、研讨会、颁奖、活动预告或会后报道**本身**为主线 |
| `exclude` | 对禾大原料情报无价值（纯促销、纯渠道、纯品牌/明星、招聘、行政等） |
| `needs_review` | 正文不足、多栏目等价、证据弱、标题正文冲突 |

| 标志位（叠加，非互斥） | 含义 |
|---|---|
| `is_market_brief_candidate` | 适合"市场快讯/TOP10"高亮的重要短讯，或多条不相关短讯汇编 |
| `is_customer_watch_candidate` | 下游客户品牌且涉及成分/配方/功效/采购的监测线索 |

**优先级判定指引（消除"活动劫持"）：**

- 文章**实质**是竞品发新原料/新技术，即使经由活动发布 →
  `primary_section=competitor_watch`（或 `ingredient_trend`/`technology_innovation`），
  `secondary_sections+=market_event`，`is_event=true`。
- 文章**实质就是活动本身**（纯预告/纯会后流水）→ `primary_section=market_event`。
- 多条不相关短讯汇编 → `is_market_brief_candidate=true`，主栏目取最重的一条，其余进 secondary。
- 下游品牌文：有成分/配方/功效角度 → `is_customer_watch_candidate=true`，主栏目按实质
  （多为 `ingredient_trend`）；无任何成分角度 → `exclude`。

---

## 三、推荐标准输出对象（V3 schema）

```json
{
  "schema_version": "newsletter-tagging/croda-beauty-v3",
  "article_id": "stable_hash_or_uuid",
  "relevance": "relevant",
  "tagging_decision": "tagged",
  "section": {
    "primary_section": "competitor_watch",
    "secondary_sections": ["market_event", "technology_innovation"],
    "is_market_brief_candidate": false,
    "is_customer_watch_candidate": false,
    "evidence": {
      "trigger_span_id": "s3",
      "inferred_because": "供应商发布新活性物是实质，webinar 只是发布场合"
    }
  },
  "tags": {
    "primary_story_type": ["product_launch_or_update", "technology_process_innovation"],
    "ingredient_technology": ["plant_botanical_extracts", "other:cocoa_opsin_blumilight"],
    "functional_claim": ["blue_light_protection", "anti_aging"],
    "product_application": ["skincare"],
    "value_chain_stage": null
  },
  "evidence_records": [
    {
      "field": "ingredient_technology",
      "label": "other:cocoa_opsin_blumilight",
      "extracted_name": "可可光护因子 blumilight",
      "trigger_span_id": "s3"
    }
  ],
  "suggested_new_tags": [],
  "review_reasons": [],
  "tag_audit": {
    "tagger": "openclaw",
    "tagged_at": "2026-06-11T12:00:00+08:00",
    "dictionary_version": "croda-beauty-2026-06-11-v3-draft",
    "prompt_version": "newsletter-tagging-prompt/croda-beauty-v3"
  }
}
```

> 脚本字段（`company`、`ingredient_mentions`、`is_event`、`event_type`、`spans`、
> 来源/语言/地区等）随 article 包提供给 Agent，Agent 直接沿用、不重复输出在 `tags` 里。
> 证据用 `trigger_span_id` 指向脚本提供的 `spans[].id`，**不转写原文**。后端在落库时
> 可按 id 回填句子原文，供月报/搜索展示。

输入侧 article 包中的 `spans`（脚本切句，节选）：

```json
"spans": [
  {"id": "s0", "text": "WeMeet | 全新! 可可光护因子打开肌肤\"眼界\""},
  {"id": "s1", "text": "亚什兰个人护理网络研讨会 10.28 今日 14:00-15:00"},
  {"id": "s3", "text": "亚什兰升级发布全球领先的光损应对方案——可可光护因子 blumilight™ 生物功能性原料"}
]
```

---

## 四、Agent 判断标签词表（V3 更新）

### 4.1 主故事类型 `primary_story_type`（多选≥1，**已去除 event_news**）

| 标签值 | 中文名 | 定义 |
|--------|--------|------|
| `corporate_move` | 企业动态 | 并购、合作、产能/建厂、出海、投融资、IPO、组织调整、市场进入、经销、召回/质量处理 |
| `product_launch_or_update` | 新原料/新品发布 | 新原料、新活性物、新配方方案、商业化发布或升级 |
| `technology_process_innovation` | 技术/工艺创新 | 递送系统、合成生物、发酵、AI 研发、绿色化学、加工突破 |
| `research_science` | 科研/功效验证 | 学术研究、临床/功效测试、专利、机理验证 |
| `regulation_policy` | 政策法规 | 备案、法规、标准、认证、致敏原、监管召回/限量/检测 |
| `market_consumer_insight` | 市场/消费者洞察 | 市场规模、品类走势、成分热度、消费者偏好、趋势报告、原料价格/进出口趋势 |
| `other` | 其他 | 相关但无法归入，进复核 |

> **删除 `event_news`**：活动是"场合"不是"实质"，已拆到脚本字段 `is_event`/`event_type`。
> 一篇"在 webinar 发新原料"的文章 = `is_event=true` + `story_type=product_launch_or_update`，
> 不再被活动标签劫持。

### 4.2 活动场合 `event_type`（脚本字段，枚举）

| 标签值 | 中文名 | 关键词示例 |
|--------|--------|------|
| `expo` | 展会 | PCHi、in-cosmetics、ICIC、展位 |
| `webinar` | 网络研讨会 | WeMeet、网络研讨、直播 |
| `forum` | 论坛/研讨会 | 论坛、研讨会、峰会、大会 |
| `award` | 颁奖/榜单 | 芳典奖、获奖、颁奖、TOP10 |
| `launch_event` | 发布会 | 发布会、全球首发、新品发布 |
| `other` | 其他活动 | 报名、预告、邀请函、圆满落幕 |

### 4.3 成分/技术 `ingredient_technology`（**主轴 + other**，词表沿用 V2 4.3）

成分类与技术类词表**完全沿用 V2 第四节 4.3**（peptides、pdrn_nucleotides、ceramides…
encapsulation_delivery、synthetic_biology、fermentation_biotech… `other:<名>`）。
V3 唯一变化：**逐字抽取由脚本 `ingredient_mentions` 完成**，本字段只标"主轴成分/技术"
并补字典外 `other:`。

### 4.4 功效宣称 `functional_claim`、4.5 产品/应用 `product_application`

词表沿用 V2（4.4 / 4.2）。V3 变化：脚本可做关键词初抽，Agent 负责**判定**
（"是否真宣称该功效"而非命中即打），并补 `other:`。

### 4.6 价值链 `value_chain_stage`（**二期**，粗粒度）

MVP 置 null。二期启用时建议先用**粗粒度**：`upstream`（上游原料/生物制造）、
`midstream`（原料/配方/制造/包装）、`downstream`（品牌/渠道/消费者），
细分（V2 的 11 值）作为二期内的进一步增强。理由：测试显示它是多信号判断而非简单映射，
非 MVP 必需。

### 4.7 公司 `company`（脚本字段）

由脚本 NER + Watchlist 别名表抽取与归一化（见第一节 1.1 与第七节）。Agent 不再自由抽取，
仅在脚本明显漏抽时于 `review_reasons` 提示。

---

## 五、活字典（Picklist）与维护

机制沿用 V2 第五节（路径 A 内联 `other:` 实时抽取；路径 B `suggested_new_tags`）。
**V3 分期**：MVP 只做 `other:` **采集**（Agent 照常打、落 `inline_other_terms`）；
**频次晋升人工审核流程列为二期**。成分迭代快，二期上线后建议每两周审一次。

---

## 六、证据规则（V3：脚本切句 + AI 指针）

> 核心：①证据要**证判断，而非只证事实**——事实拉对、解读错的标签同样无用；
> ②**切句是机械活交脚本，AI 只指针 + 给理由，不转写原文**。

**分工**：脚本把标题+正文切成带编号的 `spans`（见第一节 1.1）；AI 引用 `trigger_span_id`
指向决定性句子，绝不复制原文。AI 唯一写自由文本的地方是关键判断的 `inferred_because`。

| 标签类型 | 证据要求 |
|---|---|
| 脚本事实字段（company、ingredient_mentions、is_event…） | **无需 Agent 证据**，脚本自带匹配 span 偏移 |
| Agent 一等判断（`relevance`、`section`、`other:` 新词） | **`trigger_span_id` + `inferred_because`**（≤20字，说明这句为何支撑该判断） |
| Agent 描述标签（story_type、功效、应用、成分主轴） | **只给 `trigger_span_id` 指针**，不写理由、不转写 |

- **为什么指针优于引文**：AI 不再转写原文 → 省输出 token、杜绝改写/幻觉；
  "找哪句决定性"仍是 AI 的判断（脚本只负责切句编号，不替 AI 选）。
- **不设置信度**：AI 不自评 confidence；质量由**人工抽检**（按来源/栏目/分层抽样复核）。
  `needs_review` 仅作客观状态（空文/极短无证据、标题正文冲突），不是"AI 不确定"。
- 测试侧对证据双轴评分：`span_valid`（指向的句子真实在题）与
  `inference_valid`（该句确能支撑标签）。

---

## 七、Watchlist（客户/竞品监测名单）

**完全沿用 V2 第六节**：客户配置，`company` 匹配出 `entity_role`
（self/competitor/customer/channel_partner/ecosystem），不进 taxonomy、不回写字典。
V3 中 `company` 抽取已前移到脚本字段（1.1），与 Watchlist 匹配的链路不变。

---

## 八、AI 打标约束（V3 推荐判断顺序）

1. 沿用脚本字段（来源、语言、地区、`company`、`ingredient_mentions`、`is_event`、`spans` 等），不重算。
2. 判 `relevance`（下游品牌须涉成分/配方/采购/功效才算相关）。
3. **判 `section`**：整体阅读后给 `primary_section` + `secondary_sections` +
   标志位（market_brief/customer_watch），并给 `section.evidence`
   （`trigger_span_id` 指向 spans + `inferred_because`）。**不得用标签反推栏目；不输出置信度。**
4. 判 `primary_story_type`（实质，多选≥1，**不含活动**）。
5. 标 `ingredient_technology` 主轴并补 `other:`；按需 `functional_claim`（判定）、
   `product_application`。
6. `value_chain_stage` 二期再启用。
7. 描述标签给 `trigger_span_id` 指针（不转写、不写理由）；一等判断给
   `trigger_span_id` + `inferred_because`；`other:` 另给 `extracted_name`。
8. 封闭字段缺标签时写 `suggested_new_tags`（进二期复核），不创造正式标签。
9. 边界：不为凑数补标签（`other:` 例外宁多勿漏）；公司/品牌/展会名不进 taxonomy；
   不拆 `corporate_move` 子类；不新增文章体裁字段；**不自评置信度**。

---

*字典版本：croda-beauty-2026-06-11-v3-draft ｜ 主要变更：新增 section 一等判断、
market_brief/customer_watch 改标志位、event_news 拆为 is_event/event_type 轴、
company 与成分抽取降为脚本字段、证据改为"脚本切句 spans + AI trigger_span_id 指针"、
取消 confidence（人工抽检 + needs_review 仅作客观状态）、value_chain 降二期 ｜
schema 名 newsletter-tagging/croda-beauty-v3 ｜ 状态：草稿，待客户栏目框架确认后正式合入*
