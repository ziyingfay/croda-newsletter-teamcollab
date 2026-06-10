# 禾大 Croda 媒体源字段设计与 Seed 清单

> 基于 `project-management/reference/source-materials/croda-newsletter/WeChat Article Export.xlsx` 与 `标签字段字典-禾大美妆个护版-V2.md`。
> 本版按用户反馈收窄：不再同时保留 `source_channel` 与 `source_nature_default`；不使用 `source_type`，也不增加额外扩展字段。

---

## 一、字段取舍

上一版里：

- `source_channel` 表达“从哪个渠道来”：网页、微信公众号、RSS、Google News。
- `source_nature_default` 表达“来源是什么性质”：官方源、媒体报道、第三方分析。

二者确实会增加理解成本。现在建议合并为一个字段：`source`。

`source` 直接用一个值同时表达“渠道 + 来源性质”，例如：

| `source` | 中文解释 | 适用例子 |
|---|---|---|
| `web_official` | 官网 / 官方网页 | 巴斯夫官网、德之馨官网 |
| `wechat_official` | 官方微信公众号 | 巴斯夫护理化学品、德之馨公众号 |
| `wechat_domestic_media` | 微信国内媒体 | 美妆小报、青眼、聚美丽 |
| `wechat_event_official` | 展会 / 活动官方微信 | PCHi |
| `wechat_third_party_analysis` | 微信第三方分析 / 数据平台 | 美丽修行App |
| `rss_media` | RSS 媒体源 | 海外行业媒体 RSS |
| `google_news_media` | Google News 媒体源 | Google News RSS 替代源 |
| `manual_reference` | 人工 / 参考补充 | 客户手动补充来源 |

这样可以保留用户需要的区分：

- 巴斯夫官网：`source=web_official`，`source_name=巴斯夫官网`
- 巴斯夫微信公众号：`source=wechat_official`，`source_name=巴斯夫护理化学品`
- 美妆小报：`source=wechat_domestic_media`，`source_name=美妆小报`

---

## 二、推荐保留字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_key` | string | 稳定内部 ID，例如 `wechat_meizhuang_xiaobao` |
| `source` | enum | 合并后的来源分类，见上方枚举 |
| `source_name` | string | 具体来源名称，例如“美妆小报”“巴斯夫官网” |
| `source_list` | string[] | 来源所属清单，例如客户 Excel 行业媒体清单 |
| `url` | string/null | 抓取入口、官网、公开转载页或列表页 |
| `rss_url` | string/null | RSS / Atom / Google News RSS URL |
| `ingest_method` | enum | 技术抓取方式：`wechat_account`、`web_scraper`、`direct_rss`、`google_news_rss`、`manual_or_reference` |
| `market_region` | string[] | 默认覆盖地区，如 `china`、`global` |
| `language` | string[] | 默认语言，如 `zh`、`en` |
| `priority` | integer | 监测优先级，1 高、2 中、3 低 |
| `status` | enum | `active`、`pending`、`paused`、`archived` |
| `note` | string | 备注 |

不再保留：

- `source_channel`
- `source_nature_default`
- `source_type`
- `owner_entity_id`
- `wechat_account_name`
- `wechat_id`
- `homepage_url`

如果未来确实要接入自动抓取，微信号、账号 ID、owner entity 可以放到抓取器配置里，不进入这张轻量媒体源表。

---

## 三、典型 JSON 示例

### 3.1 巴斯夫官网

```json
{
  "source_key": "web_basf_official_cn",
  "source": "web_official",
  "source_name": "巴斯夫官网",
  "source_list": ["croda_beauty_competitor_official_sources"],
  "url": "https://www.basf.com/cn/zh/media/news-releases.html",
  "rss_url": null,
  "ingest_method": "web_scraper",
  "market_region": ["china", "global"],
  "language": ["zh"],
  "priority": 1,
  "status": "active",
  "note": "官方网页来源"
}
```

### 3.2 巴斯夫微信公众号

```json
{
  "source_key": "wechat_basf_care_chemicals_cn",
  "source": "wechat_official",
  "source_name": "巴斯夫护理化学品",
  "source_list": ["croda_beauty_competitor_wechat_sources"],
  "url": null,
  "rss_url": null,
  "ingest_method": "wechat_account",
  "market_region": ["china"],
  "language": ["zh"],
  "priority": 1,
  "status": "pending",
  "note": "官方微信公众号来源；抓取入口待补齐"
}
```

### 3.3 美妆小报

```json
{
  "source_key": "wechat_meizhuang_xiaobao",
  "source": "wechat_domestic_media",
  "source_name": "美妆小报",
  "source_list": ["croda_beauty_customer_excel_industry_media"],
  "url": null,
  "rss_url": null,
  "ingest_method": "wechat_account",
  "market_region": ["china"],
  "language": ["zh"],
  "priority": 1,
  "status": "pending",
  "note": "客户 Excel 行业媒体；抓取入口待补齐"
}
```

---

## 四、Excel 中“行业媒体”初始清单

`WeChat Article Export.xlsx` 中“行业媒体”共 13 个，建议先作为微信媒体来源 seed。

| 来源名 | source_key | source | status |
|---|---|---|---|
| 硅碳鼠日化圈 | `wechat_guitanshu_rihuaquan` | `wechat_domestic_media` | `pending` |
| 美浪CBEAUTY | `wechat_meilang_cbeauty` | `wechat_domestic_media` | `pending` |
| Fbeauty未来迹 | `wechat_fbeauty_weilaiji` | `wechat_domestic_media` | `pending` |
| 美妆小报 | `wechat_meizhuang_xiaobao` | `wechat_domestic_media` | `pending` |
| 美妆产品观 | `wechat_meizhuang_chanpinguan` | `wechat_domestic_media` | `pending` |
| 荣格个人护理 | `wechat_ringier_personal_care` | `wechat_domestic_media` | `pending` |
| 美丽修行App | `wechat_meili_xiuxing_app` | `wechat_third_party_analysis` | `pending` |
| PCHi | `wechat_pchi` | `wechat_event_official` | `pending` |
| 青眼 | `wechat_qingyan` | `wechat_domestic_media` | `pending` |
| 聚美丽 | `wechat_jumeili` | `wechat_domestic_media` | `pending` |
| 中国化妆品 | `wechat_china_cosmetics` | `wechat_domestic_media` | `pending` |
| 化妆品观察 品观 | `wechat_pinguan_cosmetics_observer` | `wechat_domestic_media` | `pending` |
| i美妆头条 | `wechat_i_meizhuang_toutiao` | `wechat_domestic_media` | `pending` |

---

## 五、与文章 JSON 的关系

`source_profiles` 是来源配置；文章入库后，脚本可把必要字段写入文章快照：

```json
{
  "article_id": "stable_hash_or_uuid",
  "raw_ref": {
    "raw_file": "raw/rss_raw_wechat_meizhuang_xiaobao.json",
    "raw_item_index": 0
  },
  "title": "文章标题",
  "summary": "文章摘要",
  "content": "正文",
  "content_length": 1200,
  "url": "https://example.com/article",
  "canonical_url": "https://example.com/article",
  "published_at": "2026-06-04T08:00:00+08:00",
  "fetched_at": "2026-06-04T12:00:00+08:00",
  "source_key": "wechat_meizhuang_xiaobao",
  "source": "wechat_domestic_media",
  "source_name": "美妆小报",
  "ingest_method": "wechat_account",
  "source_list": ["croda_beauty_customer_excel_industry_media"],
  "content_language": "zh",
  "market_region": ["china"],
  "extraction_status": "success",
  "raw_tags": []
}
```

`source_name/source_key` 负责命中 media list 中的一条 `source_profile`，并自动带出 `source`、`source_list`、`ingest_method`、默认地区和默认语言。`article_id` 负责串联 `rss_clean.json`、`tagging.json` 和 `report_content.json`；`raw_ref` 只负责回溯原始抓取记录。Agent 打标时读取这些基础字段作为上下文，但不把它们写进 `tags`。

---

## 六、后续补齐项

1. 为 13 个微信公众号补齐实际抓取入口，例如 wewe-rss feed、公开转载页或手工导出文件。
2. Excel 中“国内原料商 / 国际原料商 / 国内代理商 / MNC客户品牌 / 国内品牌”优先作为 watchlist；只有它们的官网、官方公众号、新闻中心才另建媒体源记录。
