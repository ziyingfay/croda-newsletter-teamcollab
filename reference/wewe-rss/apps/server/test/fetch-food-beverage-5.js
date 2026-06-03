const got = require('got');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

const articles = [
  {
    id: 'XwgL-9_8kH8T0_FEpw8-Uw',
    topic: '饮品趋势',
    fallbackUrl: 'https://www.sialchina.cn/media/industrynews/2026-04-20/4602.html',
  },
  {
    id: '3ESiOELzgm-d7W-BZisalA',
    topic: '食饮行业趋势',
    fallbackUrl: 'https://www.sialchina.cn/media/pressrelease/2026-05-14/3727.html',
  },
  {
    id: 'jFJzLwfkUsSDsd-87bzwwg',
    topic: '跨境电商食饮选品',
    fallbackUrl: 'https://www.sialchina.cn/media/pressrelease/2025-07-28/4243.html',
  },
  {
    id: 'LscsRMbLp_JM2kLgw2Cjgg',
    topic: '食品饮料新品',
    fallbackUrl: 'https://www.sialchina.cn/media/pressrelease/2026-05-15/3669.html',
  },
  {
    id: 'HW-rz8KWlGZmkWpw3osk0Q',
    topic: '亚洲食品饮料',
    fallbackUrl: 'https://www.sialchina.cn/media/pressrelease/2025-01-21/3555.html',
  },
];

const headers = {
  'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  Connection: 'keep-alive',
};

async function fetchWechatArticle(article) {
  const url = `https://mp.weixin.qq.com/s/${article.id}`;
  const startedAt = Date.now();

  try {
    const response = await got(url, { headers, timeout: 15000 });
    const $ = cheerio.load(response.body);
    const title = $('#activity-name').text().trim();
    const author = $('#js_name').text().trim();
    const publishTime = $('#publish_time').text().trim();
    const contentHtml = $('.rich_media_content').html() || '';
    const contentText = $('.rich_media_content').text().trim();
    const isCaptcha = response.url.includes('appmsgcaptcha') || response.body.includes('wappoc_appmsgcaptcha');

    return {
      ...article,
      sourceUrl: url,
      finalUrl: response.url,
      usedFallback: false,
      success: Boolean(contentText) && !isCaptcha,
      blockedByCaptcha: isCaptcha,
      title,
      author,
      publishTime,
      contentHtml,
      contentText,
      contentHtmlLength: contentHtml.length,
      contentTextLength: contentText.length,
      fetchMs: Date.now() - startedAt,
    };
  } catch (error) {
    return {
      ...article,
      sourceUrl: url,
      finalUrl: url,
      usedFallback: false,
      success: false,
      error: error.message,
      contentHtml: '',
      contentText: '',
      contentHtmlLength: 0,
      contentTextLength: 0,
      fetchMs: Date.now() - startedAt,
    };
  }
}

async function fetchFallback(result) {
  if (result.success || !result.fallbackUrl) return result;

  const startedAt = Date.now();
  try {
    const response = await got(result.fallbackUrl, { headers, timeout: 15000 });
    const $ = cheerio.load(response.body);
    const title = $('h1').first().text().trim() || result.topic;
    const contentRoot =
      $('.news_content, .content, .article, article, .main').first().length > 0
        ? $('.news_content, .content, .article, article, .main').first()
        : $('body');
    const contentHtml = contentRoot.html() || '';
    const contentText = contentRoot.text().replace(/\s+/g, ' ').trim();

    return {
      ...result,
      finalUrl: response.url,
      usedFallback: true,
      success: Boolean(contentText),
      title: result.title || title,
      contentHtml,
      contentText,
      contentHtmlLength: contentHtml.length,
      contentTextLength: contentText.length,
      fallbackFetchMs: Date.now() - startedAt,
    };
  } catch (error) {
    return {
      ...result,
      fallbackError: error.message,
      fallbackFetchMs: Date.now() - startedAt,
    };
  }
}

async function main() {
  const results = [];

  for (const article of articles) {
    const result = await fetchFallback(await fetchWechatArticle(article));
    results.push(result);
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }

  const output = {
    generatedAt: new Date().toISOString(),
    tool: 'wewe-rss got+cheerio fulltext-style fetch',
    note:
      'Direct mp.weixin.qq.com requests may be redirected to WeChat captcha. When that happens, this file keeps the WeChat sourceUrl and uses the indexed public repost fallbackUrl for content.',
    total: results.length,
    successCount: results.filter((item) => item.success).length,
    directWechatSuccessCount: results.filter((item) => item.success && !item.usedFallback).length,
    fallbackSuccessCount: results.filter((item) => item.success && item.usedFallback).length,
    articles: results,
  };

  const outputPath = path.join(__dirname, '../data/food-beverage-5-fulltext.json');
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

  console.log(`saved: ${outputPath}`);
  for (const item of results) {
    console.log(
      `${item.success ? 'OK' : 'FAIL'} ${item.usedFallback ? 'fallback' : 'wechat'} ${item.contentTextLength} ${item.title || item.topic}`,
    );
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
