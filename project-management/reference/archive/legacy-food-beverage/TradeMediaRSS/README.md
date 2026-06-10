# 食品饮料媒体 RSS 资讯抓取系统

## 一、项目背景与目标

本项目旨在构建一个自动化服务，定期从食品饮料行业的专业媒体网站抓取最新资讯，并对每篇资讯进行内容分析和二次加工（标签分类、摘要生成等）。

原始媒体名单来自 `食品饮料媒体链接.xlsx`，经多轮扩展，目前覆盖 **50 家**垂类媒体，其中 **42 家通过 RSS 正常获取**。

## 二、系统架构

```
媒体名单(Excel)
    │
    ▼
RSS 抓取层 (src/rss_fetcher.py)
    │ feedparser + requests
    ▼
原始数据存储 (data/rss_raw_*.json)
    │
    ▼
正文提取层 (src/article_extractor.py)
    │ BeautifulSoup + 多策略提取
    ▼
完整文章数据
    │
    ▼
内容分析层 (TODO: LLM标签分类)
```

## 三、目录结构

```
TradeMediaRSS/
├── 食品饮料媒体链接.xlsx       # 原始媒体名单
├── requirements.txt            # Python依赖
├── run_fetch.py               # 入口脚本
├── README.md                   # 项目文档
├── src/
│   ├── __init__.py
│   ├── config.py              # 媒体配置与状态管理
│   ├── rss_fetcher.py          # RSS抓取模块
│   └── article_extractor.py    # 文章正文提取模块
└── data/
    └── rss_raw_*.json          # 已抓取的原始RSS数据
```

## 四、模块说明

### 4.1 配置层 (src/config.py)

`MediaSource` 数据类定义每家媒体的基本信息：
- `name`: 媒体名称
- `website`: 官方网站域名
- `rss_url`: RSS订阅地址
- `status`: 当前状态（working / blocked_waf / blocked_404 / blocked_202 / no_rss）
- `note`: 备注说明

`MEDIA_CONFIG` 字典管理所有媒体配置，`WORKING` / `BLOCKED` / `NO_RSS` 列表提供快捷筛选。

### 4.2 RSS抓取层 (src/rss_fetcher.py)

`RSSFetcher` 类负责从各媒体 RSS 源获取资讯条目：
- 使用 `requests` 库发送 HTTP 请求（feedparser 的 parse() 不支持 timeout 参数）
- 内置请求频率限制（每源间隔 1.5 秒）
- `RSSEntry` 数据类封装单条资讯：标题、链接、摘要、发布时间、来源媒体、获取时间
- `_clean_summary()` 方法清除 RSS 摘要中的 HTML 标签，并截取前 500 字符

### 4.3 正文提取层 (src/article_extractor.py)

`ArticleExtractor` 类负责从文章 URL 提取完整正文：
- 内置三级提取策略，按优先级依次尝试：
  1. `trafilatura` 库（需单独安装）：最专业的正文提取库
  2. `readability-lxml`：基于 Mozilla Readability 算法的提取
  3. `BeautifulSoup` 朴素提取：以 `<article>` / `<main>` / content 相关 class 的 div 为基础提取
- 内置请求频率限制（每域名间隔 2 秒）
- 对单域名下多篇文章批量提取时自动去重

### 4.4 入口脚本 (run_fetch.py)

整合以上模块的执行脚本：
1. 抓取所有 working 状态的媒体 RSS
2. 将原始数据存入 `data/rss_raw_{timestamp}.json`
3. 演示性提取前 5 篇文章正文

## 五、媒体状态汇总

### 5.1 探查结论（总计50家）

#### ✅ 正常 RSS（42家）

| 媒体 | RSS URL | 条目/次 | 说明 |
|------|---------|---------|------|
| Food Ingredients First | resource.innovadatabase.com/rss/fifnews.xml | 50 | |
| FoodNavigator | foodnavigator.com/arc/outboundfeeds/rss/ | 20 | |
| FoodNavigator-USA | foodnavigator-usa.com/arc/outboundfeeds/rss/ | 20 | 偶发超时 |
| FoodNavigator Asia | foodnavigator-asia.com/arc/outboundfeeds/rss/ | 20 | 亚太 |
| Bakery&Snacks | bakeryandsnacks.com/arc/outboundfeeds/rss/ | 20 | |
| NutraIngredients | nutraingredients.com/arc/outboundfeeds/rss/ | 20 | |
| NutraIngredients Asia | nutraingredients-asia.com/arc/outboundfeeds/rss/ | 20 | 亚太 |
| ConfectioneryNews | confectionerynews.com/arc/outboundfeeds/rss/ | 20 | |
| Dairy Reporter | dairyreporter.com/arc/outboundfeeds/rss/ | 20 | 乳制品 |
| Beverage Daily | beveragedaily.com/arc/outboundfeeds/rss/ | 20 | 饮料 |
| Food (Harnisch) | harnisch.com/food/en/feed/ | 10 | Dr Harnisch出版集团 |
| Food Technologie (Harnisch) | harnisch.com/food-technologie/feed/ | 10 | Dr Harnisch出版集团 |
| Petfood Pro (Harnisch) | harnisch.com/petfoodpro/en/comments/feed/ | 0 | 评论feed |
| FMCG Gurus | fmcggurus.com/rss | 10 | |
| Fi Global Insights | insights.figlobal.com/rss.xml | 50 | Informa自有生态 |
| Mintel | mintel.com/feed/ | 12 | 市场研究/消费趋势 |
| (Inside) Food & Drink | insidefoodanddrink.com/feed/ | 10 | |
| HPCI Nutraceutical Business Review | nutraceuticalbusinessreview.com/rss | 20 | |
| Just Food | just-food.com/feed/ | 10 | 食品商业 |
| Pet Food Media | petfoodmedia.com/feed/ | 10 | |
| Pet Worldwide | petworldwide.net/petworldwide/rss.feed | 30 | |
| Pet Online (DE) | petonline.de/pet/rss.feed | 30 | 德语 |
| Food & Beverage Business | foodandbeverage.business/feed/ | 10 | |
| CEC Editore | ceceditor.com/feed/ | 10 | 意大利出版 |
| Food Tech & Manufacturing (AU) | foodprocessing.com.au/feed | 20 | 澳大利亚 |
| Asia Food & Beverages | asiafoodbeverages.com/feed/atom/ | 10 | 亚太 |
| Asia & Middle East Food Trade | ameft.com/feed/ | 15 | 中东 |
| AP Food Industry | apfoodonline.com/comments/feed/ | 10 | 亚太（评论feed） |
| **Prepared Foods** | Google News RSS | 100 | WAF封锁，通过Google News绕过 |
| **Food Business News** | Google News RSS | 100 | WAF封锁，通过Google News绕过 |
| **FoodBev** | Google News RSS | 100 | 原RSS 404，通过Google News绕过 |
| **New Food Magazine** | Google News RSS | 100 | HTTP 202，通过Google News绕过 |
| **Ingredients Network** | Google News RSS | 100 | 网站不可访问，通过Google News绕过 |
| **Vitafoods Insights** | Google News RSS | 100 | 网站不可访问，通过Google News绕过 |
| **Innova Market Insights** | Google News RSS | 100 | 原RSS 500，通过Google News绕过 |
| **Meat+Poultry** | Google News RSS | 100 | WAF封锁，通过Google News绕过 |
| **IFT / Food Technology** | Google News RSS | 100 | 原官网无RSS，通过Google News绕过 |
| **Food & Beverage Tech Review** | Google News RSS | 100 | 原域名RSS重定向，通过Google News绕过 |
| **Agro Food Industry Hi-tech** | Google News RSS | 2 | 原网站无RSS，Google News条目少 |
| **Pet Food Processing** | Google News RSS | 1 | 宠物食品，Google News仅1条 |
| **Food Review Indonesia** | Google News RSS | 13 | 印尼语，Google News绕过 |

#### ❌ 被封锁（3家）

| 媒体 | 问题 | 说明 |
|------|------|------|
| Beverage Industry | WAF 403 + Google News无结果 | 主页和RSS均返回403 |
| International Petfood | HTTP 401 + Google News无结果 | 需要认证 |
| GlobalPETS | WAF 403 + Google News无结果 | HTTP 403封锁 |
| Innovation in Food Technology | HTTP 401 + Google News无结果 | 需要认证 |
| Food Beverage Insider | WAF 403 + Google News无结果 | HTTP 403封锁 |

#### ⚠️ 无 RSS（5家）

| 媒体 | 说明 |
|------|------|
| Funzionali (IT) | 网站不可访问，Google News也无结果 |
| Ingredienti Alimentari (IT) | 网站不可访问，Google News也无结果 |
| The Spoon | 仅有评论feed，无主内容 |
| Petfood Pro (Harnisch) | 仅有评论feed，无主内容 |
| AP Food Industry | 仅有评论feed，无主内容 |

**总结**：50家媒体中，42家RSS正常工作（直接RSS 27家 + Google News RSS 15家），每次运行可获取约 **1500+ 条** 资讯。

### 5.2 媒体来源体系

本项目媒体来自以下合作体系：

- **Fi Europe/Fi Asia 官方媒体伙伴**：Informa Markets 展会合作媒体
- **Dr Harnisch 出版集团**：国际食品/宠物食品垂类出版
- **Informa 自有内容生态**：Fi Global Insights
- **亚太媒体扩展**：从 ReachLane 清单和行业文档中发现的区域媒体
- **全球一线配料媒体**：FoodNavigator、NutraIngredients 等

## 六、重要尝试与发现

### 6.1 关于 feedparser 的 timeout 参数

**发现**：feedparser 的 `parse()` 函数不接受 `timeout` 关键字参数，传入会导致 `TypeError`。

**解决**：先用 `requests.get(timeout=N)` 获取响应体，再将 `response.content` 传给 `feedparser.parse()`。这样既能控制超时，又能利用 requests 的自动编码处理。

### 6.2 关于 403 封锁的绕过尝试

测试了以下方案，均告失败：

| 方案 | 尝试内容 | 结果 |
|------|---------|------|
| 模拟浏览器 Headers | 添加完整的 User-Agent、Accept、Accept-Language 等 | 失败，Prepared Foods / Beverage Industry 主页仍403 |
| 先访问主页获取Cookies再请求RSS | 两步请求，携带完整Cookie | 失败，Cookies为空（WAF未设置Cookie） |
| cloudscraper 库 | 模拟 Chrome 浏览器绕过 CloudFlare | 失败，仍返回403 |

**结论**：这三家媒体使用了较为严格的企业级 WAF 保护（可能是 CloudFlare Enterprise 或类似方案），常规 HTTP 客户端无法模拟通过。

**可能的解决方向**：
- 使用 Playwright/Selenium 等无头浏览器（保留完整浏览器指纹）
- 手动联系媒体确认是否有其他RSS订阅地址
- 等网站政策变化后重试

### 6.3 关于 Brotli 压缩问题

FoodBev 网站返回的响应使用了 `Content-Encoding: br`（Brotli压缩），但测试环境的 `requests` 库未能自动解码（报错 "brotli decoder not available"）。不过最终确认该媒体 RSS URL 本身就返回 404，此问题已无实际意义。

### 6.4 关于正文提取策略

朴素 BeautifulSoup 提取在多数情况下已可获得较好效果（提取到 9000-14000 字/篇），但对于结构复杂或大量广告/脚本嵌套的页面，效果会打折扣。设计上预留了 `trafilatura` 和 `readability-lxml` 作为高级备选，实际使用时可根据需要安装。

## 七、当前进展

| 模块 | 状态 | 说明 |
|------|------|------|
| RSS 抓取 | ✅ 完成 | 42家媒体稳定运行（含15家Google News RSS） |
| 正文提取 | ✅ 完成 | 多策略提取，已验证可行 |
| 数据持久化 | ✅ 完成 | JSON格式存入data目录 |
| 定时调度 | ⏳ 待做 | 可用 APScheduler 或系统 cron |
| 内容分类/标签 | ⏳ 待做 | 需接入 LLM API |
| 封锁媒体（16家） | ⏳ 部分可解决 | WAF封锁较难突破，401认证可尝试 |

## 八、依赖安装

```bash
pip install -r requirements.txt
```

核心依赖：
- `feedparser` - RSS解析
- `requests` - HTTP请求
- `certifi` - SSL证书
- `beautifulsoup4` - HTML解析
- `lxml` - XML/HTML处理器
- `cloudscraper` - 备选的CloudFlare绕过（目前未成功但保留）

可选增强依赖（用于提升正文提取质量）：
- `trafilatura` - 专业正文提取
- `readability-lxml` - Readability算法

## 九、运行方式

```bash
python run_fetch.py
```

输出示例：
```
============================================================
食品饮料 RSS 资讯抓取
运行时间: 2026-04-29T13:35:58.534228
============================================================

[1/2] 抓取 RSS Feeds...
    目标媒体 (26 家)
  OK [Food Ingredients First] 获取到 50 条
  OK [FoodNavigator] 获取到 20 条
  ...
    总计获取: 467 条

    RSS 原始数据已保存: data/rss_raw_20260429_133558.json

[2/2] 提取文章正文 (前5篇演示)...
    提取: https://www.foodingredientsfirst.com/news/fiber-formulation-...
      -> 提取到 14374 字符
    ...
============================================================
完成!
============================================================
```

## 十、下一步方向

1. **定时任务化**：接入 APScheduler，实现每小时/每天自动运行
2. **内容分类**：接入 LLM API（如 Claude/Kimi/GPT），对每篇资讯生成标签和分类
3. **去重机制**：基于文章 URL 或标题 hash 做去重，避免重复处理
4. **数据导出**：支持导出为 Excel 或其他格式便于查阅
5. **封锁媒体**：评估是否值得用 Playwright 无头浏览器方案尝试突破 WAF