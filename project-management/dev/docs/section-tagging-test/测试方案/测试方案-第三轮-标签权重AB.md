# 第三轮测试方案 · 标签权重 & A/B 分层（基于 V4 字典）

> 承接第二轮（`round2-gold-free-results.md`）。本轮回答一个**架构问题**：
> **标签到底该多重要？** 你的判断是"标签权重太高、应降为展示点缀"，本轮用 A/B 两组
> 数据来检验这个判断该不该落地到架构里。
>
> 字典基线：`标签字段字典-禾大美妆个护版-V4-draft.md`。模型：**全部 Opus 4.8**。
> Gold：沿用 Fable 那份（需按 V4 重映射，见第 5 节）。

---

## 0. 先回答你的问题：当前架构需要调整吗？

**结论：你的方向是对的，而且大部分已经在 V4 里了；本轮要验证的是"还能不能再往前一步、把标签彻底降权"。**

逐条对你的想法做评估：

1. **"标签不作为逻辑分类，只作展示点缀"** —— ✅ **V3/V4 已经是这样**。第一轮就证明了
   "标签公式反推栏目"不行，所以 V4 的栏目是 AI **整体判断**、**不由标签推导**。也就是说
   标签现在对栏目**已经没有决定权**了。你担心的"标签权重太高影响结果"，在*栏目决定*这条
   链路上其实已经解除。

2. **但还剩一个真问题**：即便标签不再*公式决定*栏目，**让同一个 Agent 在判栏目的同时
   还要打一堆标签**，仍可能**分散它判栏目的注意力 / 占输出预算 / 产生锚定**。这才是
   "标签权重"残留的地方——**A/B 两组正是测这个**：把标签从 Agent 身上拿掉（A），栏目会
   不会判得更准或一样准？

3. **"Relevance 是初筛，报告撰写 Agent 再精筛"** —— ✅ 这是个好架构判断，而且它**改变了
   relevance 的评判标准**：既然下游还有精筛，relevance 就该做成**宽进（高召回）**的闸门
   ——**错杀有用文章（漏掉）比错放垃圾（多留）代价大得多**，因为漏掉的文章下游再也捞不
   回来，多留的下游会筛掉。本轮 relevance 指标据此改成**召回优先**（见第 6 节）。

4. **"标签先做展示用，数据量大了再优化"** —— ✅ 合理。本轮就是要确认：现在用**脚本**做
   展示标签（A 组）够不够用；如果够，Agent 就只管 relevance+section，标签留给脚本/二期。

**我的架构建议（供本轮验证）**：把"打标"拆成**三件权重不同的事**，别再笼统叫"标签"：

| 事项 | 权重 | 谁做 | 评判 |
|---|---|---|---|
| relevance 准入 | 中（宽进闸门，**与 section 耦合**） | Agent 优先判，section 可回修 | **召回优先**（少漏） |
| **section 栏目** | **高（必须对）** | Agent 一等判断 | 准确率 / F1 |
| 描述标签（成分/功效/场景/故事类型/角色） | **低（展示点缀）** | 脚本（A/B 都做）+ Agent 补充（仅 B） | "够不够展示"+成本 |

> **relevance ↔ section 耦合 + needs_review 隔离（按你的澄清）**：relevance 是初判闸门，
> section 判断可回修它。每周期三种去向：
> - **可落栏目** → 进报告（再经第三层报告撰写 Agent 精筛）。
> - **section=exclude / relevance=not_relevant**（确信不相关：纯促销/渠道/招聘/无原料角度）→ 丢弃。
> - **section=needs_review / relevance=unclear**（确实判不了）→ **隔离（quarantine）**：
>   **既不流向报告撰写 Agent**（不给下一步添乱），**也不等人工**；**留到人工周期性审计**回看这堆。
>
> 关键：needs_review 是"判不了"，exclude 是"确信不要"，两者都不进报告，但 exclude 是丢弃、
> needs_review 是暂存待审。**正文薄不等于 needs_review**——必须先用标题+脚本字段+来源画像去判。

#### needs_review 判定门槛（什么才算"实在判不了"）

Agent 必须**依次穷尽**下列信号后才允许 needs_review；任一信号能定栏目，就**必须**给栏目，不许偷懒：

1. **正文**（若 `extraction_status` 可用）能判 → 给栏目。
2. 正文薄/空 → 用**标题 s0** 判（如"…重组胶原蛋白原料销售严正声明" → competitor_watch）。
3. 仍不定 → 用**第一层脚本字段**：`company`（命中竞品/KA → 指向 competitor/ka）、
   `is_event`/`event_type`（指向 market_event 或"活动是场合"）、`ingredient_mentions`（指向 ingredient_innovation）。
4. 仍不定 → 用**来源画像 `source`**：竞品官号→competitor_watch 倾向、行业媒体→industry/ingredient 倾向、展会官号→market_event 倾向。

**只有同时满足以下才判 needs_review（且 relevance=unclear、隔离）**：
- 正文空或仅标题，**且**
- 标题对栏目无信息量（纯问候/纯促销口号/纯转发语，无公司/活动/成分/主题线索），**且**
- 脚本字段无可用信号（无公司命中、无成分命中、is_event 无指向），**且**
- 来源画像也无法消歧（来源本身模糊或多义）；

**或** 出现**标题与正文的事实冲突**且无法判定哪个为准。

> 反例（**不**该 needs_review）：路博润"全球首发丨邀您体验路家科技"（正文 4 字）——标题有"首发+邀您体验"
> + company=路博润（竞品）+ is_event → 应判 market_event/competitor_watch，不进隔离。
> 预期 needs_review 率应**很低**；隔离堆是人工周期审计的对象，不是每周期的人工队列。

A/B 实验观察两件事：①Agent 在判栏目之外**是否还要打标签**会不会拖累第 2 行的栏目准确率；
②Agent 打出来的标签长什么样、和脚本标签比如何。

> **A/B 的正确理解（按你的澄清修正）**：**两组在第一层都由脚本打标签，这点不变。**
> 区别只在第二层 Agent：
> - **A**：Agent 只判 relevance + section，**不打标签**。
> - **B**：Agent 在判 relevance + section 之外，**额外**用开放语义打一遍标签（作"补充/参考"，
>   不查字典固定值）。最后写报告的 Agent 可以在这些标签里筛选。
>
> 所以 B = A 的脚本标签（保留） + Agent 的补充标签。这反而让对比更干净：
> - **栏目维度**：A vs B 直接看"Agent 多干打标这件事，栏目判得更差/一样/更好吗"。
> - **标签维度**：在 B 这一组里，同一篇文章**同时有脚本标签和 Agent 标签**，可以**并排对比**
>   脚本 vs Agent 谁打得更好——这是干净的同篇对照，不再是跨组混淆。

---

## 1. 工作流分层（与你的理解对齐 + 一处调整）

```text
第一层 · 数据采集
  抓取（公众号13行业媒体/竞品官方20+ ≈30+信源, ~499篇/月）→ 清洗(HTML→纯文本+质量分)
  → 入库 rss_clean.json / all-articles
  ★ 调整：把原"第二层脚本字段"全部前移到这一层做掉——
    NER 抽 company、成分命中 ingredient_mentions、spans 分句、is_event/event_type、
    脚本描述标签（**A/B 都做**）。产出"文章包"。

第二层 · AI 打标引擎 (newsletter-tagging)
  Agent 一等判断：relevance 准入(宽进，与 section 耦合) → primary_section + secondary + evidence(指针)
  描述标签：A=就用脚本那份；B=脚本那份 + Agent 额外开放打一遍（补充/参考）
  校验层：schema 合规 / span 指针存在 / 人工抽检（无置信度）

第三层 · 月报生成
  栏目归类(V4 五正式栏目) → 行业快讯/热点由报告Agent从各栏目挑≤10条 → 趋势分析 → 行动建议
  ★ 报告 Agent 精筛时参考打标 Agent 偶尔传来的 report_guidance（如标了 mention_only 则一句话带过）
  ★ 报告撰写 Agent 在这里做"精筛"：决定哪些进报告。产出：市场监测月报 HTML
```

唯一调整：**第二层的脚本字段全部前移到第一层**（你已提出），第二层 Agent 只剩"判断"。

---

## 2. 本轮测试目的（3 个 Goal）

- **Goal 1（核心）—— 标签是否拖累栏目**：比较 A、B 两组的 **primary_section 准确率**。
  若 A ≈ B（栏目准确率在误差内相当），说明"Agent 多打标签"不帮栏目 → **可以把标签从
  Agent 拿掉、降为脚本/展示**（你的判断成立）。若 A 明显 > B → 标签反而分散 Agent，更该拿掉；
  若 B 明显 > A → 打标过程帮助了 Agent 理解、标签有保留价值。
- **Goal 2 —— Agent 打的标签有没有增量价值**：B 组里同一篇同时有脚本标签和 Agent 补充标签，
  **并排对比**：Agent 比脚本多抓到什么（新成分、字典外概念）、又带来什么代价（开放词碎片化、
  成本）。判断 Agent 补充打标值不值，以及写报告 Agent 能否在这些标签里有效筛选。
- **Goal 3 —— relevance 宽进闸门是否成立**：以**召回**为主评 relevance，确认"少漏"，
  把精筛交给第三层。

附带（沿用）：验证 V4 下 **"活动不抢实质"** 仍成立（活动进 secondary，不抢 primary）。

---

## 3. 两组定义（精确版）

两组**共同点**：① 输入是第一层产出的"文章包"（含脚本字段 + spans）；② Agent **优先判
relevance**（一等准入，宽进）；③ Agent 判 **section**（primary 取 **5 个正式栏目**
competitor_watch / ingredient_innovation / ka_watch / market_event / regulation_policy
+ exclude / needs_review；**行业新闻快讯/热点由报告 Agent 下游编排，不在此打标**）+ secondary
+ 指针证据，不反推、不打置信度；④ 两组都支持**可选 `report_guidance`**（默认省略，仅在有必须
提醒报告 Agent 的点时补一句话单条字符串，不改栏目）；⑤ `value_chain_stage` 与活字典
`other:` 晋升**放二期**；⑥ 模型 Opus 4.8。

> **共同点补充**：两组**第一层脚本都打描述标签**（用 V4 字典词表 + 别名表关键词命中，
> 固定值，命中不了就空），随文章包带入。差别只在第二层 Agent 是否**额外**打标。

### 组 A —— Agent 只判 relevance + section
- Agent 输出：`relevance`、`section{primary, secondary, evidence}`。**不打任何标签。**
- 描述标签 = 第一层脚本那份（固定值）。
- 立场：**标签纯脚本点缀，Agent 不碰**。预期成分/公司/场景命中不错，story_type / 功效"是否真宣称"
  会偏弱——本轮看"偏弱到什么程度、够不够展示"。

### 组 B —— Agent 在 A 的基础上，额外打一遍开放语义标签（补充/参考）
- Agent 输出：`relevance`、`section{...}`，**外加**开放语义标签：`primary_story_type`、
  `ingredient_technology`、`functional_claim`、`product_application`、**`entity_role`**——
  **不参考字典固定值，按语义自行命名**。
- 第一层脚本标签**照常保留**；Agent 标签是**补充层**，与脚本标签并存，供写报告 Agent 筛选。
- 立场：**脚本点缀 + Agent 补充**。看 Agent 比脚本多抓到什么、代价是什么。
- 注意 `entity_role`：V4 默认由 Watchlist 匹配出角色；B 让 Agent 现场判，本轮额外测
  "Agent 判角色 vs Watchlist 匹配"谁更值（对照 Watchlist 已知角色）。

---

## 4. 测试流程

1. **造输入包（第一层）**：在 `make_pilot_sample.py` 基础上扩一个脚本，给 30 篇产出：
   - 通用：spans、company、ingredient_mentions、is_event/event_type；
   - A 专用：脚本版描述标签（关键词/别名命中 V4 词表）。
2. **跑 Agent（第二层，Opus 4.8）**：
   - A：prompt 只要 relevance + section；
   - B：prompt 要 relevance + section + 开放语义标签（明确"不要查字典、按语义自己命名"）。
3. **校验**：用 V4 版 validator（需把 schema/prompt/validator 从 V3 同步到 V4 的栏目枚举）
   查 schema/span/一致性。
4. **打分**：A、B 的 section 对照**重映射后的 V4 gold**（第 5 节）；标签质量按第 6 节。
5. **记录**：写入 `analysis/round3-*.md`，并在 `团队分享` 追加轮次 3。

> 前置依赖：V4 的 prompt/schema/validator 尚未产出（目前是 V3 版）。**跑本轮前需先把这三件
> 套同步到 V4**（primary_section 枚举 = 5 正式栏目 competitor_watch / ingredient_innovation /
> ka_watch / market_event / regulation_policy + exclude / needs_review；去掉 flags；
> **行业快讯不是打标标签**；新增 `report_guidance` 字段 + needs_review 隔离门槛）。

---

## 5. Gold 处理（沿用 Fable 那份，但必须重映射到 V4）

现有 gold 用的是 **V3 栏目标签**，与 V4 不一致，需按下表**确定性重映射**：

| V3 gold_primary | → V4 |
|---|---|
| `technology_innovation` | `ingredient_innovation` |
| `ingredient_trend` | `ingredient_innovation` |
| `market_brief` | → 按主导实质落正式栏目（§1.2；两篇汇编均判 `competitor_watch`） |
| `competitor_watch` | `competitor_watch` |
| `market_event` | `market_event` |
| `exclude` / `needs_review` | 不变 |

**4 篇落在 V4 新栏目边界、确定性映射不可靠的，已用 Opus 4.8 按 V4 字典重判**（其余 26 篇按上表自动映射）：

| 篇号 | 来源 | V3 gold | **Opus 4.8 V4 重判** | 理由 |
|---|---|---|---|---|
| [03] | 硅碳鼠（新原料备案趋势） | ingredient_trend | `ingredient_innovation`（次:regulation_policy,market_event） | 借备案数据读成分趋势，备案是数据底座 |
| [05] | FBeauty（HBN 科研双首秀） | technology_innovation | **`ka_watch`**（次:ingredient_innovation,market_event） | 下游 KA 品牌自研机制+功效，会场只是场合 |
| [14] | 品观（OTC 渠道+医保监管） | exclude | `exclude`（not_relevant） | 渠道/支付监管，无原料成分角度 |
| [17] | 个护前沿（长寿三巨头） | technology_innovation | `ingredient_innovation`（次:ka_watch） | 实质是长寿前沿技术/成分趋势，品牌只是视角 |

> 产物：`gold-standard/pilot-30-gold-v4.json`（脚本 `remap_gold_v4.py` 生成：26 确定性 + 4 Opus 重判）。
> 只有 [05] 的主栏目被 Opus 改动（→ ka_watch），其余 3 篇与确定性映射一致。
>
> **gold 策略（按你的决定）：本阶段不做人工 gold，信任模型。** gold = Fable 那份（V3→V4 重映射）
> + Opus 4.8 对 4 篇边界的重判。这是**模型自标的银标**，准确率读作"与该银标的吻合度"；
> 优点是快、零人工成本，代价是有同源循环（解读时记住：它衡量一致性/合理性，不是绝对真值）。

### 5.1 样本从 30 扩到 120（你的提议）

更正一个事实：你给的 `all-articles(1).json` 其实有 **499 篇**（不是 120），我们当时只抽了 30 篇。
**完全可以扩到 120**，而且**应该扩**——原因正是上面：30 篇里 `ka_watch=1`、`regulation_policy=0`，
**这两个 V4 新栏目在 30 篇上根本测不了**。扩到 120 的做法：

- 在 `make_pilot_sample.py` 上把配额从 30 提到 120，并**定向补齐弱栏目**：确保
  `regulation_policy`（法规/备案类）和 `ka_watch`（MNC/国内 KA 品牌涉成分类）各 ≥15–20 篇，
  否则单纯随机扩样这两类仍然稀疏。
- **Gold 策略（已定）**：不做人工 gold。120 篇全部用 **Opus 4.8 银标**当 gold——脚本/关键词分诊
  499 找出法规/KA 候选，编平衡 120，**Opus 4.8 判一版作 gold**，被测组（A/B）也是 Opus 跑。
  注意循环：被测和 gold 同源，所以这一版准确率读作"自洽性/合理性"，配合**模型间一致性**（如再加
  一个 Claude 档位）和**人工抽查**来交叉印证，而不是当绝对真值。
- 若 Alexi 能按时间窗口多抓，优先补 regulation/ka_watch 两类真实文章，比从现有 499 里硬凑更好。

---

## 6. 怎么衡量（指标）

### 6.1 栏目（Goal 1，核心）
- `primary_section_accuracy`（A vs B，各对 V4 gold）—— **本轮第一指标**。
- 差值显著性：30 篇样本小，差异 < ~3 篇（10%）视为"无显著差异"。
- per-section P/R/F1、混淆矩阵；特别看 `ingredient_innovation`（合并后）是否比 V3 的
  ingredient↔tech 分歧更干净。
- 沿用检查：活动类文章 primary 是否仍为实质（competitor/ingredient），market_event 在 secondary。

### 6.2 relevance + 隔离（Goal 3）
- `relevance_recall`（真相关里被放行进报告的比例）—— **主指标**（越高越好，少漏）。
- `wrongly_dropped`（被 exclude 错杀的有用文，**贵**）vs `wrongly_kept`（错放垃圾，**便宜**，下游精筛兜底）。
- `quarantine_rate`（needs_review/unclear 占比）—— **应很低**；这是人工周期审计的工作量。
- `false_quarantine_rate`（**关键**）：被隔离、但 gold 其实有明确栏目的比例 —— 量化"该判却被搁置"的
  代价（这类文章本可进报告却被扣下）。门槛设计若合理，这个值应接近 0。
- 隔离判定是否遵守"穷尽标题+脚本字段+来源画像"门槛（抽查 needs_review 案例的理由）。

### 6.2b report_guidance 使用情况（可选字段，低权重）
- **使用率**：应**低**（只在确有提醒时写）；若大面积出现说明 Agent 滥用、需收紧。
- **该提醒未提醒**：抽查路博润 teaser 这类"可落栏目但仅预告"的，是否补了 note（漏提醒率）。
- **note 是否有用**：抽查若干 note，是否真能帮报告 Agent 少读/少踩坑（人工判定）。

### 6.3 标签质量（Goal 2，展示用，低权重）—— 在 B 组内做同篇并排对比
B 组同一篇同时有"脚本标签"和"Agent 补充标签"，直接对照：
- **脚本标签**（A/B 共有）：对 gold 标签的 precision/recall，分字段报（预期 ingredient/company 高、
  story_type 低）。
- **Agent 补充标签**（仅 B）：
  - **增量**：Agent 抓到而脚本漏掉的（尤其字典外新成分、需语义判断的 story_type / "是否真宣称"）。
  - **碎片化**：开放词同一概念出现几种写法（不查字典的代价，直接影响搜索/聚合可用性）。
  - 对 gold 的**语义命中率**（开放词需模糊/人工匹配）。
- **结论指向**：脚本够不够 → 不够的部分 Agent 补得划不划算（增量 vs 碎片化+成本）。
- entity_role（B）：对 Watchlist 已知角色的准确率 —— 判"Agent 判角色 vs Watchlist 匹配"谁更值。
- 评判基调：标签是**展示点缀**，门槛是"够展示/够搜"，不是"全对"；写报告 Agent 会在标签里再筛。

### 6.4 成本与合规
- 输出体量（字符/篇）A vs B：A 只输出 section，预期**显著更省**；量化省多少。
- schema/span 合规率（V4 validator）。
- （可选）Opus 3× 重跑模糊簇，section flip-rate。

---

## 7. 执行产物
- 新增脚本：第一层"脚本描述标签生成器"（A 用）、A/B 跑批、`compare_runs.py` 复用/扩展。
- 结果：`analysis/round3-tag-weight-AB.md`、`runs/A-opus48.json`、`runs/B-opus48.json`。
- 文档：本方案 + 轮次 3 小结。

---

## 8. Goal 安排与决策规则（结果 → 架构动作）

按 Goal 优先级排，**Goal 1 是闸门，先看它**：

- **若 A 的 section 准确率 ≥ B（在误差内或更高）**　→　**标签降权落地**：Agent 只做
  relevance+section，描述标签交脚本/二期，报告上作展示点缀。**你的判断成立。**（预期最可能）
- **若 B 明显 > A**　→　打标过程确实帮 Agent 理解栏目，标签不能纯脚本化；保留 Agent 轻量打标
  （但仍可只为搜索，不为分类）。
- **Goal 2**：
  - 若 A 的脚本标签"够展示"（成分/公司/场景可用，story_type 弱但可接受或可不显示）→ 确认脚本路线。
  - 若 B 开放词**碎片化严重** → 证明"不查字典"会毁掉搜索价值 → **字典 picklist 必须保留**
    （即使标签降权，词表仍要用，只是由脚本套用而非 Agent 自由发挥）。
- **Goal 3**：relevance_recall 达标（少漏）即确认"宽进闸门 + 下游精筛"架构。
- **ka_watch / regulation_policy**：本轮不下结论，列入下一轮（需补样本）。

---

## 9. 风险与说明
- **新栏目样本不足**：30 篇里 ka_watch=1、regulation_policy=0，测不了这两个 V4 新栏目 →
  **必须扩到 120 并定向补样**（见 §5.1）。
- **30 篇精挑偏乐观**：准确率偏高；真实几千篇时长尾变广会回落。
- **gold 用模型银标（已定，本阶段不做人工 gold）**：被测组与 gold 同源（都是 Opus），存在循环，
  准确率读作"自洽/合理性"，靠模型间一致性 + 人工抽查交叉印证，不当绝对真值。后续若要绝对准确率，
  再上 ≥2 人 gold（尤其 ka_watch/regulation 新栏目）。
- **needs_review 隔离门槛要被检验**：若门槛太松，`false_quarantine_rate` 会偏高（该判的被扣下）；
  若太紧，会把判不了的硬塞进报告添乱。本轮用第 6.2 的两个指标校准这个门槛。
- **前置**：V4 prompt/schema/validator 需先从 V3 同步（栏目枚举变更，见第 4 节）。
