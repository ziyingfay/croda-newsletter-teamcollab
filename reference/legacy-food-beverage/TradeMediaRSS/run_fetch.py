import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import MEDIA_CONFIG, WORKING
from src.rss_fetcher import RSSFetcher
from src.article_extractor import ArticleExtractor

import json
from datetime import datetime

def run():
    print("=" * 60)
    print("食品饮料 RSS 资讯抓取")
    print(f"运行时间: {datetime.now().isoformat()}")
    print("=" * 60)

    fetcher = RSSFetcher(request_delay=1.5)

    print(f"\n[1/2] 抓取 RSS Feeds...")
    print(f"    目标媒体 ({len(WORKING)} 家)")
    all_entries = fetcher.fetch_all_normal(MEDIA_CONFIG)
    print(f"    总计获取: {len(all_entries)} 条")

    if not all_entries:
        print("    未获取到任何内容，退出。")
        return

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rss_output = os.path.join(data_dir, f"rss_raw_{timestamp}.json")
    with open(rss_output, 'w', encoding='utf-8') as f:
        json.dump(
            [{"title": e.title, "link": e.link, "summary": e.summary,
              "published": e.published, "source": e.source_name}
             for e in all_entries],
            f, ensure_ascii=False, indent=2
        )
    print(f"\n    RSS 原始数据已保存: {rss_output}")

    print("\n[2/2] 提取文章正文 (前5篇演示)...")
    extractor = ArticleExtractor(request_delay=2.0)
    demo_urls = [e.link for e in all_entries[:5] if e.link]

    for url in demo_urls:
        print(f"    提取: {url[:60]}...")
        text = extractor.extract(url)
        if text:
            print(f"      -> 提取到 {len(text)} 字符")
        else:
            print(f"      -> 提取失败")

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)

if __name__ == "__main__":
    run()