# 第三轮补充 · 新栏目探针（regulation_policy / ka_watch）

运行：2026-06-16 ｜ Opus 4.8 ×3 ｜ V4 字典 ｜ 33 篇定向探针（16 法规 + 17 KA，从 499 标题强信号筛出）

> 方法：关键词标题强信号 → 33 篇候选 → Opus 跑 3 次 section 判断（group A）。无人工 gold；
> 候选池标签（regulation/ka_watch）只是"标题看起来像"，**不是答案**——用来看模型实判的**去向/漏判**与**稳定性**。

## 1. 路由/漏判：模型接不接得住这两个新栏目

| 候选池 | 多数判进目标栏目 | 漏到哪了 |
|---|---|---|
| **regulation（16 篇标题含 备案/法规/监管/标准…）** | **9/16 = 56%** → regulation_policy | 5→ingredient_innovation、1→competitor_watch、1→market_event |
| **ka_watch（17 篇标题含 KA 品牌 + 成分）** | **4/17 = 24%** → ka_watch | **8→exclude**、3→regulation_policy、2→market_event |

**两个核心发现：**
- **regulation_policy 向 ingredient_innovation"漏"得厉害**：当法规文是围绕某个成分写的（新原料备案趋势、
  PDRN 团体标准、植物新原料监测期、撤回潮），模型常判成"成分趋势"而非"法规"。reg↔ingredient 边界模糊。
- **ka_watch 是个很窄的筐**：17 篇 KA 品牌文里只有 4 篇进 ka_watch；**8 篇被正确排除**（纯品牌/公益/
  诉讼/带货/可持续，无成分角度），其余被拉去 ingredient/regulation。说明 **KA 品牌文大多本就不该进
  ka_watch**——这个栏目在实际月份里很可能样本很少（呼应第二轮"客户/KA 很薄"的发现）。

## 2. 稳定性：同模型 3 次重跑的 flip-rate（直接回答"同模型会不会翻"）

- **25/33 = 76% 三次完全一致；8 篇至少翻过一次（≈24% flip）。**
- 翻动**全部集中在两个新栏目的边界**：
  - regulation_policy ↔ ingredient_innovation：撤回潮 / PDRN团体标准 / 140款植物新原料（3 篇）
  - ka_watch ↔ exclude：HBN×白敬亭、自然堂可持续（2 篇）
  - ka_watch ↔ regulation_policy：韩束抗衰共识（1 篇）
  - market_event 边界：安评防腐剂研讨会、杨浦合规科普（2 篇）
- 各 run 计数也在飘：regulation_policy 10–14、ka_watch 2–5。

**结论**：同一个 Opus 在**边界文章**上确实会两次判不同（这里 ~24%），且**专门发生在这两个新栏目与
相邻栏目的边界**；清晰文章稳定。这正是前面那个"为什么不是 100%"问题的直接证据——不稳主要来自
**边界语义**，不是随机噪声。

## 3. 含义与待办

- **这两个新栏目能测、有真实样本，但边界未定、稳定性偏低**（reg↔ingredient、ka↔exclude）。
- **优先补字典里的边界规则**（这是提升二者准确率/稳定性的关键）：
  - regulation：**"备案/标准/监管动作本身为主线"→regulation_policy；"借备案数据讲成分趋势"→ingredient_innovation。**
  - ka_watch：**KA 品牌文必须"涉成分/配方/功效/采购"才进；纯品牌/公益/诉讼/带货→exclude。** 并提示客户
    ka_watch 在某些月份可能很少甚至为空。
- 改完边界规则后，重跑这 33 篇探针看 flip-rate 是否下降，是验证规则有效的直接指标。
- 仍是模型银标、单评测者、定向探针（选择偏差）；要绝对数字仍需人工 gold。

产物：`runs/probe-run{1,2,3}.json`、`fixtures/probe-candidates.json`、`scripts/build_probe_candidates.py`。

---

## 4. 收紧边界规则后重跑（probe2）——诚实的负面结果

往字典 + prompt 写了两条边界细则（reg↔ingredient 看"讲规则还是借规则讲成分"；ka↔exclude 从严），
同 33 篇 Opus ×3 重跑（`probe2-run{1,2,3}.json`）：

| 指标 | 原规则 | 收紧后 |
|---|---|---|
| regulation 池 → regulation_policy（多数） | 56% | **56%（没变）** |
| ka 池 → ka_watch（多数） | 24% | **24%（没变）** |
| flip(至少翻一次)/33 | 24% | **30%（略升，在噪声内）** |

**规则没有改善路由，也没降 flip。** 但深挖原因后，发现这是个**有价值的结构性结论**：

### 4.1 翻动的本质不是"判错栏目"，是"多栏目里挑哪个当主"

对收紧后仍翻的 10 篇，逐一检查：**翻动的 primary 100% 落在该文自己的(主+次)栏目并集内**
（`primary都在并集=True` 全部成立）。也就是说：
- 模型**始终识别出同一组 2–3 个共属栏目**，只是每次轮流把其中一个当 primary。
- 不是"乱跳到不相关栏目"，而是这些文章**本就同时属于多个栏目**。

典型：克琴/德之馨/辉文这类——**原料商(竞品) 发/备案 新成分**——它**同时是** competitor_watch（竞品动作）
**又是** ingredient_innovation（新成分）**还沾** regulation_policy（备案/标准）。三者皆成立，"主"是近似平手。

### 4.2 真正的主轴不稳是 competitor_watch ↔ ingredient_innovation（供应商文）

我加的 reg↔ingredient 规则没打中要害——**最大的摇摆是"供应商发新成分 = 竞品动态 还是 成分趋势"**，
这条轴我没规则、也很难用一条规则切干净（因为它本就是二者皆是）。

### 4.3 结论：别再用 prompt 规则追"单一 primary 确定性"

- 这类**多栏目文章的不稳是固有的**，不是定义缺口，**加规则按不下去**。
- 正确机制是**结构性**的，V4 已经有：用 **`secondary_sections` 承载共属栏目**，让报告 Agent 去重/落位；
  primary 在共属集合内轮换**不影响文章出现在正确的栏目下**。
- **度量也要改**：对多栏目文章，看 **section 集合 / top-2 命中**，而不是 primary 精确匹配——
  本轮 primary 一致 70%，但"primary 落在并集内" **73%**、集合一致 67%，说明大部分"翻动"是无害的主次轮换。
- ka↔exclude 规则**方向上略有帮助**（HBN/韩束这次 2/3 run 落 ka_watch，原来是 exclude/regulation），
  但仍 1 run 抖动——同样是"该文既像 ka 又像 ingredient"的共属问题。

### 4.4 建议下一步（不是再加规则）

1. 把"供应商发新成分"明确为**允许 competitor_watch 主 + ingredient_innovation 次（或反之）**，
   并在度量上接受二者等价，不算错。
2. 报告 Agent 端做**栏目去重/择一展示**（一篇多栏目时按报告需要落位），把"主次轮换"消化在下游。
3. 真要压 primary 抖动，靠**多次取多数票(majority vote)**比靠 prompt 规则更实在。

产物：`runs/probe2-run{1,2,3}.json`。
