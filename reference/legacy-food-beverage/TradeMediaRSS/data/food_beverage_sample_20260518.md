# TradeMediaRSS 食品饮料媒体文章样本

抓取时间：2026-05-18 16:33 Europe/Berlin

运行结果：`python3 run_fetch.py` 成功抓取 42 个 working/google_news RSS 源，共 1520 条记录，原始结果保存为 `data/rss_raw_20260518_163341.json`。项目自带正文抽取也跑通，前 5 篇 Food Ingredients First 文章均成功抽取正文。

说明：TradeMediaRSS 原仓库未内置微信公众号抓取源；微信公众号原文直连会跳转到验证码页。本样本中微信公众号覆盖采用“公开转载页 + 标注的微信原文链接”的方式落地，保留原微信链接以便人工浏览验证。

## 1. Food Ingredients First / 欧美媒体

- 标题：Sustainable Foods Summit 2026: Regenerative agriculture scales amid rising climate and trade risks
- 发布时间：2026-05-18
- 链接：https://www.foodingredientsfirst.com/news/sustainable-foods-summit-2026-regen-ag-netzero.html
- 正文抽取：成功，约 13138 字符
- 摘要：文章聚焦 2026 Sustainable Foods Summit，重点讨论再生农业、净零目标、气候和贸易风险对食品产业链的影响，以及企业如何通过可持续采购和供应链韧性应对不确定性。

## 2. FoodNavigator / 欧美媒体

- 标题：Oral GLP-1 breakthrough: What it means for impulse-driven food categories
- 发布时间：2026-05-18
- 链接：https://www.foodnavigator.com/Article/2026/05/18/the-impact-of-oral-glp-1s-on-the-food-and-beverage-industry/
- 正文抽取：成功，约 6185 字符
- 摘要：文章讨论口服 GLP-1 药物对食品饮料行业的潜在影响，尤其是冲动型食品品类、份量控制、营养密度和“更少但更好”的产品定位机会。

## 3. Beverage Daily / 欧美媒体

- 标题：Wine consumption declines: but enters new period of reconfiguration
- 发布时间：2026-05-15
- 链接：https://www.beveragedaily.com/Article/2026/05/15/wine-consumption-declines-but-new-consumption-occasions-emerge/
- 正文抽取：成功，约 2073 字符
- 摘要：文章指出 2025 年全球葡萄酒消费下降，背后有通胀、关税、供应链不确定性和低酒精消费趋势等因素；同时也提到葡萄酒消费场景正在重组。

## 4. SIAL 西雅展转载 / 微信公众号覆盖

- 标题：2025食饮行业“生死局”！AI变革、体重管理、出海热潮抓不抓？
- 页面日期：2025-03-21
- 转载页：https://www.sialchina.cn/media/pressrelease/2026-05-14/3727.html
- 微信原文：https://mp.weixin.qq.com/s/3ESiOELzgm-d7W-BZisalA
- 正文抽取：转载页成功，约 2862 字符；微信原文直连跳验证码
- 摘要：文章围绕食饮行业在 AI、健康/体重管理、出海、可持续等方向的结构性变化，介绍 SIAL 世界食品产业峰会议题和企业需要关注的破局方向。

## 5. 食品饮料行业观察 / 微信公众号覆盖

- 标题：2026年饮品市场主流风味趋势
- 页面日期：2025-12-23
- 转载页：https://www.sialchina.cn/media/industrynews/2026-04-20/4602.html
- 微信原文：https://mp.weixin.qq.com/s/XwgL-9_8kH8T0_FEpw8-Uw
- 正文抽取：转载页成功，约 2507 字符；微信原文直连跳验证码
- 摘要：文章梳理功能性饮料、抹茶和咖啡因替代、无酒精饮品、肠道健康、高蛋白、情绪调节和热带/小众风味等 2026 饮品趋势。

