from datetime import datetime, timezone

from crawler.crawler import WebsiteCrawler
from crawler.extractor import HTMLExtractor


class SEOPipeline:
    """Run crawling and SEO feature extraction."""

    def __init__(
        self,
        timeout: int = 15,
    ):
        self.crawler = WebsiteCrawler(
            timeout=timeout
        )

    @staticmethod
    def _build_crawl_id() -> str:
        """
        Build a unique crawl identifier.
        """

        timestamp = datetime.now(
            timezone.utc
        )

        return (
            "crawl_"
            f"{timestamp.strftime('%Y%m%d%H%M%S')}_"
            f"{timestamp.microsecond:06d}"
        )

    @staticmethod
    def _build_page_id(
        url: str,
    ) -> str:
        """
        Build a stable page identifier.

        The normalized URL is used so fragments such as
        #section do not create a different page.
        """

        import hashlib
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(
            url.strip()
        )

        normalized = urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip("/")
                or "/",
                "",
                parsed.query,
                "",
            )
        )

        return hashlib.sha256(
            normalized.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

    @staticmethod
    def _build_content_hash(
        html: str,
    ) -> str:
        """
        Build a stable content hash from HTML.
        """

        import hashlib

        return hashlib.sha256(
            html.encode(
                "utf-8",
                errors="ignore",
            )
        ).hexdigest()

    @staticmethod
    def _build_crawl_quality(
        crawl_result: dict,
        features: dict,
    ) -> str:
        """
        Determine capture quality.

        NORMAL:
            The page appears to have been captured normally.

        SUSPECT:
            The HTTP request succeeded, but the extracted
            page looks unusually empty or incomplete.

        FAILED:
            The HTTP request failed.
        """

        if not crawl_result.get(
            "success",
            False,
        ):
            return "FAILED"

        status_code = crawl_result.get(
            "status_code"
        )

        if status_code != 200:
            return "FAILED"

        word_count = features.get(
            "word_count",
            0,
        )

        heading_total_count = features.get(
            "heading_total_count",
            0,
        )

        total_link_count = features.get(
            "total_link_count",
            0,
        )

        image_count = features.get(
            "image_count",
            0,
        )

        title_word_count = features.get(
            "title_word_count",
            0,
        )

        meta_exists = features.get(
            "meta_description_exists",
            False,
        )

        html_size_bytes = crawl_result.get(
            "html_size_bytes",
            0,
        )

        suspicious_signals = 0

        if word_count <= 10:
            suspicious_signals += 1

        if heading_total_count == 0:
            suspicious_signals += 1

        if total_link_count == 0:
            suspicious_signals += 1

        if image_count == 0:
            suspicious_signals += 1

        if title_word_count <= 2:
            suspicious_signals += 1

        if not meta_exists:
            suspicious_signals += 1

        tiny_capture = (
            html_size_bytes > 0
            and html_size_bytes < 10_000
            and word_count <= 20
        )

        if tiny_capture:
            suspicious_signals += 2

        if suspicious_signals >= 5:
            return "SUSPECT"

        return "NORMAL"

    def analyze(
        self,
        url: str,
    ) -> dict:
        """
        Crawl and extract a complete SEO observation.
        """

        crawl_timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        crawl_id = (
            self._build_crawl_id()
        )

        crawl_result = self.crawler.fetch(
            url
        )

        # --------------------------------------------------
        # Network failure
        # --------------------------------------------------

        if not crawl_result.get(
            "success",
            False,
        ):
            return {
                "success": False,
                "crawl_id": crawl_id,
                "crawl_timestamp": crawl_timestamp,
                "url": url,
                "domain": crawl_result.get(
                    "domain",
                    "",
                ),
                "status_code": crawl_result.get(
                    "status_code"
                ),
                "response_time_ms": crawl_result.get(
                    "response_time_ms",
                    0,
                ),
                "redirect_count": crawl_result.get(
                    "redirect_count",
                    0,
                ),
                "html_size_bytes": crawl_result.get(
                    "html_size_bytes",
                    0,
                ),
                "crawl_quality": "FAILED",
                "errors": [
                    crawl_result.get(
                        "error",
                        "Crawler request failed.",
                    )
                ],
            }

        status_code = crawl_result.get(
            "status_code"
        )

        # --------------------------------------------------
        # HTTP failure
        # --------------------------------------------------

        if status_code != 200:
            return {
                "success": False,
                "crawl_id": crawl_id,
                "crawl_timestamp": crawl_timestamp,
                "url": url,
                "domain": crawl_result.get(
                    "domain",
                    "",
                ),
                "status_code": status_code,
                "response_time_ms": crawl_result.get(
                    "response_time_ms",
                    0,
                ),
                "redirect_count": crawl_result.get(
                    "redirect_count",
                    0,
                ),
                "html_size_bytes": crawl_result.get(
                    "html_size_bytes",
                    0,
                ),
                "crawl_quality": "FAILED",
                "errors": [
                    (
                        "HTTP request failed "
                        f"with status {status_code}"
                    )
                ],
            }

        # --------------------------------------------------
        # HTML extraction
        # --------------------------------------------------

        extractor = HTMLExtractor(
            html=crawl_result["html"],
            base_url=crawl_result["url"],
        )

        features = extractor.extract_all()

        # --------------------------------------------------
        # Crawl quality
        # --------------------------------------------------

        crawl_quality = (
            self._build_crawl_quality(
                crawl_result,
                features,
            )
        )

        # --------------------------------------------------
        # Page identity
        # --------------------------------------------------

        canonical_url = crawl_result[
            "url"
        ]

        page_id = (
            self._build_page_id(
                canonical_url
            )
        )

        content_hash = (
            self._build_content_hash(
                crawl_result["html"]
            )
        )

        # --------------------------------------------------
        # Final observation
        # --------------------------------------------------

        return {
            "success": True,

            # Identity
            "crawl_id": crawl_id,
            "page_id": page_id,
            "crawl_timestamp": crawl_timestamp,
            "content_hash": content_hash,

            # URL / HTTP
            "url": canonical_url,
            "domain": crawl_result[
                "domain"
            ],
            "status_code": status_code,
            "response_time_ms": crawl_result[
                "response_time_ms"
            ],
            "redirect_count": crawl_result[
                "redirect_count"
            ],

            # Crawl metadata
            "html_size_bytes": crawl_result.get(
                "html_size_bytes",
                0,
            ),
            "crawl_quality": crawl_quality,

            # SEO features
            "features": features,

            "errors": [],
        }