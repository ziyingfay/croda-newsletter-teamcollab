# 第三轮 · 标签权重 A/B 结果（Opus 4.8，V4 字典）

运行：2026-06-16 ｜ 打标 Opus 4.8 ｜ 30 篇 V4 输入包 ｜ gold = `pilot-30-gold-v4.json`（模型银标）

> ⚠️ gold 是 Opus 自标银标，打标也是 Opus → **绝对准确率读作"自洽性/合理性"，非真值**。
> 30 篇精挑且 ka_watch=1/regulation_policy=0，新栏目测不准。**稳健的是 A-vs-B 的相对差、成本、碎片化。**

## 1. Goal 1 — 标签是否拖累栏目（核心）

| 组 | 主栏目准确率 vs gold | top-2 | 输出体量(字符/篇) |
|---|---:|---:|---:|
| **A 仅判栏目** | **21/30 = 70%** | 87% | **629** |
| **B 栏目+开放标签** | 20/30 = 67% | 80% | 1167 |

- **差异仅 1 篇（<3 篇 = 无显著差异）**；A vs B 主栏目一致 **90%**（27/30）。
- **结论**：让 Agent 在判栏目之外**额外打标签，并不提升栏目准确率**（甚至略降），却把**输出成本
  几乎翻倍**（629→1167，约 1.85×）。**→ 支持"把标签从 Agent 拿掉、降为脚本/展示"**（你的判断成立）。

3 篇 A/B 分歧（都落在已知模糊边界）：
- 青眼(敏感肌市场洞察)：A=ka_watch / B=market_event / gold=ingredient_innovation（都偏）
- 唯铂莱 FIC：A=competitor_watch（=gold） / B=ingredient_innovation（B 偏）
- 品观 OTC 医保：A=regulation_policy / B=market_event / gold=exclude（regulation↔exclude 边界）

## 2. Goal 2 — B 的开放标签：碎片化严重

- 平均 5.2 标签/篇（4 字段）。
- **`ingredient_technology` 30 篇里出现 38 个不同值** —— 大量单例（synthetic_biology / fermentation /
  neurotransmitter_signaling / dopamine / plant_extract / marine_peptide …）。**开放词不查字典 → 同类
  概念多种写法，直接损害标签唯一用途（搜索/聚合）。**
- `entity_role`（Agent 现场判）分布合理：competitor 17 / customer 8 / ecosystem 8 / channel 3 / self 1。
- **结论**：若保留标签，**必须用字典 picklist**（脚本套用），不能让 Agent 自由发挥——否则搜索价值碎掉。

## 3. Goal 3 — relevance 宽进 + 隔离门槛

- relevance vs gold：A/B 均 28/30 = 93%；**错杀有用文章 0**（宽进闸门成立，少漏）。
- **隔离(needs_review) 率 = 0/30**：Opus 对所有薄/空文都从标题+脚本字段+来源判出了栏目，
  没有触发隔离——**"穷尽信号才隔离"的门槛有效，needs_review 确实罕见**（设计达标）。

## 4. report_guidance（可选字段）

- 使用率：A 5/30、B 7/30（约 17–23%）——**用得克制，没滥用**；符合"仅在该提醒时写"。

## 5. 小结与决策

- **Goal 1 通过 → 标签降权落地**：Agent 只做 relevance + section（A 路线）；描述标签交脚本/展示，
  不必让 Agent 在打标时兼做。栏目准确率不降、成本砍半。
- **若保留标签 → 用字典 picklist**：B 的开放词碎片化（38 值/30 篇）证明自由词会毁搜索；脚本套字典更稳。
- **relevance 宽进 + 隔离门槛 + report_guidance** 三个机制都按预期工作。
- **待补**：ka_watch/regulation_policy 样本不足，需扩 120 定向补样后才能评这两个新栏目；
  绝对准确率需人工 gold（本阶段按你的决定用模型银标，只看相对结论）。
