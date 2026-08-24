import time
from urllib.parse import urlparse

import requests


class WebsiteCrawler:
    """Fetch webpages and collect HTTP-level information."""

    def __init__(
        self,
        timeout: int = 15,
    ):
        self.timeout = timeout

    def fetch(
        self,
        url: str,
    ) -> dict:
        """
        Fetch a webpage and return normalized crawl data.

        Network errors are converted into structured failures
        so one problematic URL does not stop the full collection.
        """

        start_time = time.perf_counter()

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(compatible; TrafiqAI/1.0)"
                    )
                },
            )

            response_time_ms = (
                time.perf_counter() - start_time
            ) * 1000

            parsed_url = urlparse(
                response.url
            )

            domain = (
                parsed_url.netloc.lower()
            )

            return {
                "success": True,
                "url": response.url,
                "domain": domain,
                "status_code": response.status_code,
                "headers": dict(
                    response.headers
                ),
                "html": response.text,
                "html_size_bytes": len(
                    response.content
                ),
                "response_time_ms": round(
                    response_time_ms,
                    2,
                ),
                "redirect_count": len(
                    response.history
                ),
                "error": None,
            }

        except requests.exceptions.RequestException as error:
            response_time_ms = (
                time.perf_counter() - start_time
            ) * 1000

            parsed_url = urlparse(url)

            return {
                "success": False,
                "url": url,
                "domain": (
                    parsed_url.netloc.lower()
                ),
                "status_code": None,
                "headers": {},
                "html": "",
                "html_size_bytes": 0,
                "response_time_ms": round(
                    response_time_ms,
                    2,
                ),
                "redirect_count": 0,
                "error": str(error),
            }

        except Exception as error:
            response_time_ms = (
                time.perf_counter() - start_time
            ) * 1000

            parsed_url = urlparse(url)

            return {
                "success": False,
                "url": url,
                "domain": (
                    parsed_url.netloc.lower()
                ),
                "status_code": None,
                "headers": {},
                "html": "",
                "html_size_bytes": 0,
                "response_time_ms": round(
                    response_time_ms,
                    2,
                ),
                "redirect_count": 0,
                "error": (
                    "Unexpected crawler error: "
                    f"{error}"
                ),
                "html_size_bytes": len(
                    response.content
                ),
            }