import feedparser
import requests
import ssl
import certifi
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

ssl_context = ssl.create_default_context(cafile=certifi.where())

@dataclass
class RSSEntry:
    title: str
    link: str
    summary: str
    published: Optional[str]
    source_name: str
    source_key: str
    fetched_at: str

class RSSFetcher:
    def __init__(self, request_delay: float = 1.0):
        self.request_delay = request_delay
        self._last_request_time = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        })
        self.session.verify = certifi.where()

    def _throttle(self, source_key: str):
        if source_key in self._last_request_time:
            elapsed = time.time() - self._last_request_time[source_key]
            if elapsed < self.request_delay:
                time.sleep(self.request_delay - elapsed)
        self._last_request_time[source_key] = time.time()

    def fetch_feed(self, source_key: str, rss_url: str, source_name: str) -> List[RSSEntry]:
        self._throttle(source_key)

        try:
            resp = self.session.get(rss_url, timeout=20)
            if resp.status_code != 200:
                raise ValueError(f"HTTP {resp.status_code}")
            feed_data = resp.content
        except Exception as e:
            raise ValueError(f"请求失败: {e}")

        feed = feedparser.parse(feed_data)

        if feed.bozo and not feed.entries:
            raise ValueError(f"RSS解析异常: {feed.bozo_exception}")

        if not feed.entries:
            return []

        return [
            RSSEntry(
                title=entry.get("title", "").strip(),
                link=entry.get("link", "").strip(),
                summary=self._clean_summary(entry),
                published=entry.get("published") or entry.get("updated", ""),
                source_name=source_name,
                source_key=source_key,
                fetched_at=datetime.now().isoformat(),
            )
            for entry in feed.entries
        ]

    def _clean_summary(self, entry) -> str:
        if hasattr(entry, "summary"):
            return self._strip_html(entry.summary)
        if hasattr(entry, "description"):
            return self._strip_html(entry.description)
        if hasattr(entry, "content") and entry.content:
            return self._strip_html(entry.content[0].value)
        return ""

    def _strip_html(self, text: str) -> str:
        import re
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()[:500]

    def fetch_all_normal(self, media_config: dict) -> List[RSSEntry]:
        all_entries = []
        for key, media in media_config.items():
            if media.status not in ("working", "google_news") or not media.rss_url:
                continue
            try:
                entries = self.fetch_feed(key, media.rss_url, media.name)
                all_entries.extend(entries)
                print(f"  OK [{media.name}] 获取到 {len(entries)} 条")
            except Exception as e:
                print(f"  ERR [{media.name}] {e}")
        return all_entries