# App

`app/` 是禾大 Croda 情报订阅 Agent 的正式应用代码区。

当前保持为空白生产区。上一代食品饮料项目代码已归档到 `reference/legacy-food-beverage/TradeMediaRSS/`，后续如需复用 RSS 抓取、正文抽取或数据清洗方法，应先迁移为禾大数据源配置后再进入本目录。

建议后续结构：

```text
app/
├── croda_intel/
│   ├── sources/
│   ├── ingestion/
│   ├── tagging/
│   ├── reporting/
│   └── db/
└── README.md
```
