import time
import random
import logging
import httpx
from config import SCRAPER_CONFIG

logger = logging.getLogger(__name__)


class BaseScraper:
    def __init__(self):
        self.rate_limit = SCRAPER_CONFIG["rate_limit"]
        self.max_retries = SCRAPER_CONFIG["max_retries"]
        self.retry_backoff = SCRAPER_CONFIG["retry_backoff"]
        self.timeout = SCRAPER_CONFIG["timeout"]
        self.user_agents = SCRAPER_CONFIG["user_agents"]
        self.last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < 1.0 / self.rate_limit:
            time.sleep(1.0 / self.rate_limit - elapsed + random.uniform(0, 0.5))

    def _headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def fetch(self, url: str, params: dict = None) -> str | None:
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                with httpx.Client(timeout=self.timeout, headers=self._headers(), follow_redirects=True) as client:
                    resp = client.get(url, params=params)
                    self.last_request = time.time()
                    if resp.status_code == 200:
                        return resp.text
                    logger.warning(f"HTTP {resp.status_code} for {url}, attempt {attempt + 1}")
            except Exception as e:
                logger.warning(f"Request failed for {url}: {e}, attempt {attempt + 1}")
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_backoff ** (attempt + 1))
        return None
