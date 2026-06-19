# 字典外新词补充机制 PRD

> 状态：Superseded / historical draft  
> 日期：2026-06-18  
> 范围：小龙虾 1 栏目打标 Agent 在判断 `relevance` / `section` 时，顺手补充字典外重要新成分、新技术或新功效。  
> 非范围：不改变 script-tagger 固定词表匹配，不引入独立审核 Agent，不做完整活字典运营系统。

> 2026-06-20 更新：本文的 `other_terms` 方案已被 V4 字典 §九和
> `前端PRD-HTML审阅版-标签与其他确认.md` 取代。当前实现方向是：
> AI 只输出 `relevance` + `section.sections`，脚本输出固定标签，后处理根据
> "栏目 + 脚本标签缺口"补 `其他-X 待确认` 通用占位；前端审阅版支持人工保留、删除、
> 注明具体内容和建议入字典。本文保留为历史设计，不作为实现依据。

---

## 1. 背景

当前 V4 打标设计中，除 `relevance` 和栏目判断外，大部分标签由脚本完成。脚本适合处理固定词表和别名表，例如多肽、玻尿酸、PDRN、包封递送、合成生物、抗糖化等已知标签。

但美妆个护原料和技术迭代很快，文章可能围绕一个尚未进入字典的新成分、新技术或新功效展开。如果只依赖固定脚本词表，这类新信息会在标签层丢失，报告卡片里也不容易体现“这篇文章真正新在哪里”。

因此需要一个轻量、可控的字典外新词补充机制。

---

## 2. 目标

在不增加复杂审核链路的前提下，让系统能够捕捉文章主线中的字典外重要新词：

- 新成分 / 新原料
- 新技术 / 新平台 / 新递送体系
- 新功效 / 新宣称方向

这些新词以 `other:<slug>` 的形式留存在内部 JSON 中，并在报告中展示具体名称，而不是展示“其他”。

---

## 3. 核心决策

### 3.1 脚本仍然负责固定词表标签

script-tagger 继续负责确定性匹配：

- `ingredient_technology` 固定标签
- `functional_claim` 固定标签
- `product_application` 固定标签
- company / watchlist
- source / media list
- spans / fact hints

脚本不负责发现字典外新词。

### 3.2 栏目打标 Agent 只做增量补充

栏目打标 Agent 本来就需要读全文，并判断：

- `relevance`
- `section.primary_section`
- `section.secondary_sections`
- `section.evidence`

因此字典外新词补充放在这一趟里完成。Agent 只做增量补充，不审核脚本已经命中的固定标签，不修改脚本标签。

### 3.3 每篇文章最多补 1 个 primary `other:`

Agent 只补“文章主角级”的字典外新词。即使文章中出现多个未收录成分，也只选择最核心的一个；如果没有明确主角新词，则不补。

### 3.4 `product_application` 不做 `other:`

字典外补充只允许两个字段：

| 字段 | 是否允许 `other:` 补充 | 说明 |
|------|------------------------|------|
| `ingredient_technology` | 是 | 新成分、新原料、新技术、新平台、新递送体系 |
| `functional_claim` | 是 | 新功效、新宣称方向 |
| `product_application` | 否 | 只使用固定词表；未命中则为空 |

---

## 4. 工作流设计

```text
RSS / WeChat / Website 抓取
        │
        ▼
cleaner 清洗基础字段
        │
        ▼
script-tagger 固定词表匹配
        │
        ├─ 输出 script_tags / company / ingredient_mentions / spans / fact_hints
        │
        ▼
小龙虾 1 栏目打标 Agent
        │
        ├─ 判断 relevance
        ├─ 判断 section
        └─ 可选补充 1 个 primary other term
        │
        ▼
merge / validator 合并校验
        │
        ├─ 固定标签来自脚本
        ├─ relevance + section 来自 Agent
        └─ other term 来自 Agent
        │
        ▼
小龙虾 2 报告 Agent
        │
        └─ 报告展示 display_name，不展示“其他”
```

---

## 5. 触发规则

Agent 只有在满足以下条件时，才输出 `other_terms`：

1. 文章是 `relevant`，且正文足够判断。
2. 文章主线明显围绕一个新成分、新技术或新功效展开。
3. 该新词没有被当前固定词表覆盖。
4. 该新词不是成分表、配方清单或长列表中的低信号词。
5. 新词属于 `ingredient_technology` 或 `functional_claim`。

如果文章只是提到大量原料或配方长列表，Agent 不应把它们逐个写成 `other:`。

---

## 6. Agent 输出结构

`other_terms` 是栏目打标 Agent 的可选增量字段。没有合格新词时输出空数组。

```json
{
  "relevance": "relevant",
  "section": {
    "primary_section": "ingredient_innovation",
    "secondary_sections": ["competitor_watch"],
    "evidence": {
      "trigger_span_id": "s2",
      "inferred_because": "新递送技术发布"
    }
  },
  "other_terms": [
    {
      "field": "ingredient_technology",
      "label": "other:bio_retinol_complex",
      "display_name": "Bio-Retinol Complex",
      "trigger_span_id": "s4",
      "reason": "文章主线围绕该新活性物发布"
    }
  ]
}
```

### 6.1 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `field` | enum | 只能是 `ingredient_technology` 或 `functional_claim` |
| `label` | string | `other:<slug>`，全小写 snake_case |
| `display_name` | string | 报告展示名称，保留原文写法 |
| `trigger_span_id` | string | 支撑新词判断的 span id |
| `reason` | string | 为什么认为它是文章主角级新词 |

---

## 7. 合并规则

merge / validator 在 Agent 输出后执行：

1. 固定标签仍以 script-tagger 输出为准。
2. `other_terms` 只追加到内部增量字段，不覆盖脚本标签。
3. 如果 `other_terms[0].field` 不在允许字段中，拒绝该项。
4. 如果 `other_terms` 超过 1 个，只保留第一个合规项或直接报错，具体实现二选一；建议 MVP 先报错，方便发现 prompt 越界。
5. 如果 `other:<slug>` 与固定词表标签或别名明显重复，丢弃 `other:`。
6. 如果 `trigger_span_id` 不存在，拒绝该项。
7. `product_application` 不接受 `other:`；如 Agent 输出，应报错。

---

## 8. 报告展示规则

报告 Agent 读取最终 JSON 时：

- 固定标签按原有标签展示。
- `other_terms` 有值时，展示 `display_name`。
- 不展示“其他”字样。
- 可在内部详情或调试层保留 `other:<slug>`，用于后续人工整理。

示例：

```text
展示：Bio-Retinol Complex
内部：other:bio_retinol_complex
```

---

## 9. 不做的事

MVP 不做以下内容：

- 不引入单独的新词审核 Agent。
- 不让 AI 复核脚本已经命中的固定标签。
- 不让 AI 修改栏目之外的固定标签。
- 不抽取成分表或长列表里的全部未知词。
- 不补 secondary `other:`。
- 不对 `product_application` 做 `other:`。
- 不立即实现完整活字典晋升流程。

---

## 10. 后续人工整理

`other_terms` 暂时只作为内部留存字段。后续如需要，可以每隔数月人工查看出现过的 `other:<slug>`：

- 高频且业务重要的，晋升为正式字典标签。
- 低频或噪音的，继续留存或忽略。
- 与已有标签重复的，合并到别名表。

这属于第二阶段活字典运营，不阻塞 MVP。

---

## 11. 验收标准

1. Agent schema 支持可选 `other_terms`。
2. `other_terms` 最多 1 条。
3. `field` 只能为 `ingredient_technology` 或 `functional_claim`。
4. `product_application` 的 `other:` 会被 validator 拒绝。
5. 无合格新词时输出 `other_terms: []`。
6. 报告展示 `display_name`，不展示“其他”。
7. 脚本固定标签、Agent 栏目判断、Agent `other_terms` 三者边界清楚，不互相覆盖。

---

## 12. 一句话方案

脚本打固定词表标签；栏目打标 Agent 在判断 `relevance` 和栏目时，顺手补充最多 1 个“文章主角级”的字典外 `other:` 新词；只覆盖 `ingredient_technology` 和 `functional_claim`，报告展示具体名称，内部保留 `other:<slug>` 供后续人工整理。
