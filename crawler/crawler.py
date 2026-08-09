import time
from urllib.parse import urlparse

import requests


class WebsiteCrawler:

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

        self.headers = {
            "User-Agent": (
                "TrafiqAI-Bot/0.1 "
                "(SEO research and website analysis)"
            )
        }

    def fetch(self, url: str) -> dict:
        start_time = time.perf_counter()

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
            allow_redirects=True,
        )

        elapsed = time.perf_counter() - start_time

        parsed_url = urlparse(response.url)

        return {
            "url": response.url,
            "domain": parsed_url.netloc,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "html": response.text,
            "html_size_bytes": len(response.content),
            "response_time_ms": round(elapsed * 1000, 2),
            "redirect_count": len(response.history),
        }