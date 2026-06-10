import requests
import ssl
import certifi
import time
import re
from typing import Optional
from urllib.parse import urlparse

ssl_context = ssl.create_default_context(cafile=certifi.where())

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

class ArticleExtractor:
    def __init__(self, request_delay: float = 2.0):
        self.request_delay = request_delay
        self._last_request_time = {}
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.verify = certifi.where()

    def _throttle(self, netloc: str):
        if netloc in self._last_request_time:
            elapsed = time.time() - self._last_request_time[netloc]
            if elapsed < self.request_delay:
                time.sleep(self.request_delay - elapsed)
        self._last_request_time[netloc] = time.time()

    def extract(self, url: str, timeout: int = 20) -> Optional[str]:
        try:
            parsed = urlparse(url)
            self._throttle(parsed.netloc)

            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code != 200:
                return None

            html = resp.text
            text = self._extract_text(html, url)
            return text

        except Exception as e:
            print(f"    提取失败 [{url[:50]}]: {e}")
            return None

    def _extract_text(self, html: str, url: str) -> str:
        text = self._trafilatura_fallback(html)
        if text and len(text) > 200:
            return text

        text = self._readability_fallback(html)
        if text and len(text) > 200:
            return text

        return self._naive_extract(html)

    def _trafilatura_fallback(self, html: str) -> str:
        try:
            import trafilatura
            result = trafilatura.extract(html)
            if result:
                return result.strip()
        except ImportError:
            pass
        return ""

    def _readability_fallback(self, html: str) -> str:
        try:
            from readability import Document
            from bs4 import BeautifulSoup
            doc = Document(html)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except ImportError:
            pass
        return ""

    def _naive_extract(self, html: str) -> str:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|article|post', re.I))

        if article:
            text = article.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)

        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return ' '.join(lines)

    def extract_batch(self, urls: list, skip_existing: callable = None) -> dict:
        results = {}
        for i, url in enumerate(urls):
            if skip_existing and skip_existing(url):
                print(f"  跳过 (已有): {url[:60]}")
                continue
            print(f"  [{i+1}/{len(urls)}] 提取: {url[:60]}...")
            text = self.extract(url)
            results[url] = text
        return results