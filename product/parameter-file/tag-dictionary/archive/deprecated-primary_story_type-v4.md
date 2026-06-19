# 已弃用 · `primary_story_type`（主故事类型）— 从 V4 字典 §3.1 归档

> **状态：弃用（DEPRECATED），不删除，存档备查。** 弃用日期 2026-06-18，用户决定。
>
> **弃用原因**：第三轮探针体检显示，`primary_story_type` 作为**纯关键词脚本标签几乎没有区分度**
> ——在 450 篇真实语料上 94% 文章至少命中一类、且大多数同时命中 3–4 类（市场 350 / 科研 320 /
> 新品 312 / 法规 259），等于"什么都匹配 = 什么都没说"。语义性太强，纯关键词做不准；而 AI 的
> `section.sections` 栏目判断已覆盖大部分原本要 story_type 表达的场景。故弃用，不再作为脚本派生标签。
>
> 若将来要恢复，需改为 AI 语义判断（而非脚本关键词），并重新评估其相对 section 的增量价值。

---

## 原 §3.1 内容（V4，含 event_news 已拆出的说明）

### 主故事类型 `primary_story_type`（多选≥1，不含 event_news）

| 标签值 | 中文名 | 典型场景 |
|--------|--------|------|
| `corporate_move` | 企业动态 | 并购、合作、产能/建厂、出海、投融资、IPO、组织调整、高校合作 |
| `product_launch_or_update` | 新原料/新品发布 | 新活性物、新配方方案、商业化发布或升级 |
| `technology_process_innovation` | 技术/工艺创新 | 递送系统、合成生物、发酵、AI 研发、绿色化学 |
| `research_science` | 科研/功效验证 | 学术研究、临床/功效测试、专利、机理验证 |
| `regulation_policy` | 政策法规 | 备案、法规、标准、认证、致敏原、监管动作 |
| `market_consumer_insight` | 市场/消费者洞察 | 市场规模、品类走势、成分热度、消费者偏好、趋势报告 |
| `other` | 其他 | 相关但无法归入 |

> `event_news` 已删除（活动 → 脚本字段 `is_event`/`event_type`）。

> 对应脚本配置已归档至：`product/parameter-file/archive/story-type/story_type_seed.json`。
