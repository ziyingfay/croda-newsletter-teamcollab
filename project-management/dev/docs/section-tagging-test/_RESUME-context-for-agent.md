# _RESUME — 栏目打标测试 上下文打包（给未来的 coding agent，自用）

> 这份是给"重新接手时的我自己"看的，不是给人看的分享稿。目标：读完这一页 + 它指的文件，
> 就能立刻知道做到哪、为什么这么定、怎么复现、下一步干什么。**先读本页，再按需点开链接。**

---

## 0. 最新状态（2026-06-17/18，看这条优先于下面旧条目）

两个**已定稿的大决定**（用户拍板），已落到字典 + skill 四件套：

1. **栏目改"平等多标签"**：取消 primary/secondary 主次分级 → `section.sections[]` 平等数组。
   一篇符合多个栏目就**全部平等打上、不判主次**；报告 Agent 下游再去重/择一。
   `exclude`/`needs_review` 为系统态，单独出现、不与正式栏目并列。
   → 这**从根上消掉了第三轮"主次轮换"不稳**（不再有 primary 可翻）。原"待定的边界规则去留"
   也随之化解：reg↔ingredient 两者都符合就都打；**只剩 ka_watch↔exclude 一条要把住**（必须有成分角度）。
2. **AI 只判 relevance + sections**；**所有描述标签下放脚本**（配置驱动）。
   - 脚本层**已开发并跑过 450 篇** → `product/output/result/tagging/待打标.json`
     （字段：company/company_normalized/company_detail[带role]/ingredient_mentions/ingredient_keys/
     is_event/event_type/spans/fact_hints；**无 section/relevance**，留给 AI）。
   - 配置文件已建并跑过：`product/parameter-file/{watchlist,ingredient-alias,event-keywords}/*_seed.json`
     （watchlist 73 实体）。**待建配置**：product_application / functional_claim / story_type。
   - 已知权衡：纯脚本抓不到字典外新成分/新功效（"活字典 other: 发现"能力下降，可接受，标签仅展示）。

**四件套已同步到上面两点**（dict V4 + prompt + schema + validator，2026-06-17）：
AI 输出只含 relevance + `section.sections[]` + per-section `evidence[]`(+可选 report_guidance)；
**禁** tags/confidence/primary_section/旧结构（validator 会报错）。已用正/负例测过。

**ka_watch 空的担忧 = 已缓解**：450 篇里命中 KA 实体 141 篇、KA+含成分(ka_watch 前置候选)**98 篇**
（pilot-30 只有 1）。能测、不空；窄是定义使然（纯品牌无成分→exclude，正确）。

**⚠️ 旧 run 文件作废**：`runs/A-/B-opus48-v4.json`、`probe*.json` 是旧 primary_section 格式，
**不过新 schema**。下次测试用新 prompt/schema 重跑（平等多选）。

**下一步候选**（替代旧 §6）：① 用新 schema 重跑一轮(平等多选)验证 multi-section 行为 + flip；
② 建 product_application/functional_claim/story_type 三个脚本配置 + 把 `待打标.json` 的脚本正式化
（脚本层设计文档 P0）；③ 评估 story_type/functional_claim 纯关键词够不够展示。

> 下面 §1–§8 是 2026-06-16 写的旧打包，**部分已被本 §0 覆盖**（尤其："primary/secondary""边界规则待定"
> "AI 打轻量标签"等已过时）；保留作历史脉络，冲突时以 §0 为准。

---

## 1. 一分钟状态

- **在做什么**：给禾大 Croda Beauty 月报做"文章→栏目落位 + 打标"的方案设计与验证测试。
- **现在在哪**：第三轮测试做完。结论已定：**栏目由 AI 整体判断**；**描述标签降权**（不让打标
  Agent 兼做，交脚本/展示）；两个 V4 新栏目（ka_watch/regulation_policy）**能测但边界天然模糊、
  主次会轮换**，靠 `secondary_sections` + 多数票消化，不靠加 prompt 规则。
- **当前定版方案**：见测试报告 **§0.6**（C+D 演化后的定版）。打标 Agent 只做 relevance + section
  (+可选 report_guidance)；脚本做事实字段 + 切句。
- **待用户拍板的 1 件事**：第三轮加的两条边界规则（reg↔ingredient、ka↔exclude）经测**无效**
  （flip 24%→30%）。我的建议：**保留 ka↔exclude，回退/弱化 reg↔ingredient**。用户未最终定。
- **平行已交付**：脚本层（清洗入库+脚本打标）的开发需求与设计（见 §5 链接），P0 可立即开发。

## 2. 心智模型（别再重新推导）

- 三层工作流：① 数据采集(spider，空，Alexi 侧) → ② 打标引擎(脚本字段 + AI 判 relevance/section) → ③ 月报生成(报告 Agent)。
- **C+D 已演化**：旧 C+D = AI 判栏目 + 打轻量标签；**第三轮把"AI 打标"砍了** → AI 只判 relevance+section。
- **V4 字典 = V3 工程决策 + 客户 v260605 反馈**。5 个正式打标栏目：
  `competitor_watch / ingredient_innovation / ka_watch / market_event / regulation_policy`（+ exclude/needs_review）。
  **行业新闻快讯/热点不是打标标签**，由报告 Agent 下游从这 5 栏目里挑 ≤10 条编排。

## 3. 关键决策日志（含理由，避免重新纠结）

1. **栏目=AI 整体判断，不用标签公式反推**（轮1：公式 A 仅 0.40、错留垃圾 9/30）。
2. **event 从 story_type 拆成脚本字段 is_event/event_type**（轮1"活动劫持"；轮2 验证劫持消失）。
3. **证据=脚本切句 spans + AI `trigger_span_id` 指针**，不转写原文（省 token、防幻觉）。
4. **取消置信度**，质量靠人工抽检；`needs_review`=客观状态(隔离)，不是自评不确定。
5. **needs_review 隔离门槛**：必须穷尽 正文→标题→脚本字段→来源画像 才允许；隔离件不传下游、待人工周期审计。
6. **标签降权（轮3 A/B）**：A(仅栏目)70% vs B(栏目+开放标签)67%，差1篇无显著差异，但 A 输出体量只一半 → 标签从 Agent 拿掉。
7. **若保留标签必须套字典 picklist**：B 开放词 ingredient 30 篇出 38 个值，碎片化毁搜索。
8. **多栏目是固有的**（轮3c）：供应商发新成分 = competitor_watch + ingredient_innovation 皆成立；
   翻动的 primary 100% 落在该文自身栏目并集内 → 用 secondary + 多数票，不靠加规则。度量看 section 集合/top-2，不死磕 primary 精确匹配。
9. **gold = 模型银标，不做人工 gold**（用户决定，信任模型）：准确率读作"自洽/合理性"，非真值。
10. **模型**：本环境只能 Claude 家族。轮2 用 Opus 4.8 + Sonnet；轮3 用 Opus 4.8。**Kimi/MiniMax 接不到**，需团队外部跑后导入。破循环靠人工 gold（未做），不是换模型。
11. **report_guidance**：可选单条字符串，默认省略，仅在有必须提醒报告 Agent 的点时写。
12. **行业快讯/ka_watch/market_brief**：market_brief/行业快讯→报告 Agent 编排；customer_watch→升为正式栏目 ka_watch（客户要求）。轮3 发现 ka_watch 很窄（KA 品牌文多数无成分角度→exclude），需提醒客户它可能常态偏空。

## 4. 结果快照（不用重跑就能回忆）

- **轮1 Pilot-30**（单评测者 Fable，A/B/C/D 选型）：A 公式=0.40、错留垃圾9；B/C/D=1.00(循环)；成本 A=100/C=42/B=32。→ 判断派胜。
- **轮2**（Opus4.8 vs Sonnet，V3 输入，无 gold）：主栏目一致 57%；活动劫持消失；指针 0 非法；标志位稳(customer 93%/brief 83%)；Opus 0 schema 错 / Sonnet 漏每标签证据。
- **轮3a A/B**（Opus4.8，V4，vs V4银标）：A 70% / B 67%；A/B 一致 90%；输出 A 629 / B 1167 字符/篇；relevance 93%、错杀0；needs_review 0；report_guidance A5/B7。
- **轮3b 新栏目探针**（33篇=16reg+17ka，Opus×3）：reg 命中 56%(5漏到 ingredient)、ka 命中 24%(8进exclude)；flip 24%(76%稳)，翻动全在新栏目边界。
- **轮3c 写边界规则重跑**（probe2，Opus×3）：路由没变(56%/24%)，flip 24%→30%(更差)；根因=多栏目固有平手(primary 都在并集内)。

## 5. 文件地图（canonical 路径）

测试树根：`product/output/test-results/section-tagging-test/`
- `scripts/make_pilot_sample.py` — 抽样+切spans+脚本字段，产 fixtures（确定性，md5排序）
- `scripts/remap_gold_v4.py` — V3 gold→V4 银标（26确定性+4 Opus重判+2汇编）
- `scripts/score_round3.py` — A/B vs V4 gold 打分
- `scripts/build_probe_candidates.py` — 从499定向筛 reg/ka 探针（标题强信号）
- `fixtures/pilot-30-input-v3.json`（30篇带spans/脚本字段，主测集）、`probe-candidates.json`（33篇探针）
- `gold-standard/pilot-30-annotations.json`（V3 gold，Fable）、`pilot-30-gold-v4.json`（V4 银标）
- `runs/` — `A-opus48-v4.json` `B-opus48-v4.json`（轮3a）、`probe-run{1,2,3}.json`（轮3b）、`probe2-run{1,2,3}.json`（轮3c）
- `analysis/round3-tag-weight-AB.md`、`analysis/round3b-newsection-probe.md`（含3c）

V4 草稿（字典 + skill 四件套）：
- `product/parameter-file/tag-dictionary/标签字段字典-禾大美妆个护版-V4-draft.md`（**当前最新字典**；§一栏目、§2.2 report_guidance、§优先级两条边界细则）
- `product/skills/newsletter-tagging/references/llm_prompt-v4-draft.md`
- `product/skills/newsletter-tagging/schemas/tag_output-v4-draft.schema.json`
- `product/skills/newsletter-tagging/scripts/validate_tags_v4_draft.py`（`--open-tags` 给 group B；`--article` 查 span）

人看的文档（dev/docs/section-tagging-test/）：
- `测试报告-栏目打标-20260611.md` — **主报告，三轮全在里面，§0.6=当前定版**
- `团队分享-栏目打标测试.md` — 活文档轮次1/2/3
- `测试方案-第三轮-标签权重AB.md`、`测试方案-第二轮-V3验证.md`、`README-revisions-v2.md`、`标签体系优化建议-v2.md`

脚本层开发设计：`project-management/dev/docs/mvp/脚本层-清洗入库与脚本打标-开发需求与设计.md`
项目契约：`project-management/dev/docs/mvp/MVP关键工件契约.md`（rss_clean.json 契约）、`product/parameter-file/source-profiles/source_profiles_seed.json`（仅13条，需补到~42）

## 6. 下一步（按优先级，挑一个开干）

1. **定边界规则去留**（等用户）：保留 ka↔exclude、回退 reg↔ingredient；改完重跑 probe2 看 flip 是否降。
2. **把"供应商发新成分"定为 competitor_watch≡ingredient_innovation 等价**（度量不算错），主次交 secondary + 报告 Agent 去重。
3. **度量改用 section 集合/top-2 + 多数票**（score 脚本加一版集合口径）。
4. **扩 120 + 定向补 reg/ka 真样本**（待 Alexi 多抓；现 499 里关键词命中多但脏，需模型分诊）。
5. **脚本层 P0**：把 script-tagger 正式化（配置驱动），见脚本层设计文档 §四 P0。不卡 spider。

## 7. GOTCHA（务必先读，踩过的坑）

- ⚠️ **整个 test-results 树是 git 未跟踪的**（`git ls-files` 为空）。**删了就没了**，git 救不回。
  曾因 `rm -rf product/parameter-file/test-results` 误删过一次，靠会话记录+all-articles 重建。
  → 动这棵树前先确认；重要产物考虑 `git add` 或先备份。
- ⚠️ **仓库被重构过**（Codex 工作日志 0613/14/16），test-results 一度从 `output/` 被移到
  `parameter-file/`。subagent 写文件时可能写错位置（写到 parameter-file）。**跑完批量 agent 后
  先 `find . -name "<outfile>"` 确认落点**，再处理。
- **gold 是重建的**：`pilot-30-annotations.json` 的 note 字段是简版（重建时压缩过），gold_primary/
  secondary/relevance 是准的；如需完整 tags/roles（轮1 score_frameworks 用）需重造。
- **fixtures 确定性可复现**：丢了就 `python3 .../scripts/make_pilot_sample.py`（md5 排序→同样30篇ID）。
  gold v4 丢了：`python3 .../scripts/remap_gold_v4.py`。
- **跑 A/B/探针的方式**：用 Agent 工具 model=opus，让它读 fixtures + llm_prompt-v4 + schema-v4，
  写 runs/*.json，再用 validate_tags_v4_draft.py 校验、score_round3.py / 内联 Bash 分析。
- **all-articles 源**：`project-management/reference/examples/all-articles(1).json`（499篇，33MB，现存）。
- **score_round3.py 的 ROOT=parents[5]**，依赖脚本在 `…/section-tagging-test/scripts/` 下；移动脚本要改。

## 8. 复现命令（从干净状态重建到可分析）

```bash
cd "<repo>/newsletter 字典"
python3 product/output/test-results/section-tagging-test/scripts/make_pilot_sample.py        # fixtures
python3 product/output/test-results/section-tagging-test/scripts/remap_gold_v4.py            # V4 gold
python3 product/output/test-results/section-tagging-test/scripts/build_probe_candidates.py   # 探针33
# A/B 与探针 runs 需用 Opus agent 重跑（非确定性；现有 runs/*.json 是已跑结果）
python3 product/skills/newsletter-tagging/scripts/validate_tags_v4_draft.py \
  product/output/test-results/section-tagging-test/runs/A-opus48-v4.json \
  --article product/output/test-results/section-tagging-test/fixtures/pilot-30-input-v3.json
python3 product/output/test-results/section-tagging-test/scripts/score_round3.py
```
