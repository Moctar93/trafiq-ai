from crawler.crawler import WebsiteCrawler
from crawler.extractor import HTMLExtractor
from crawler.schemas import SEOFeatures
from crawler.validators import validate_seo_features

from crawler.identity import (
    generate_page_id,
    generate_content_hash,
    generate_crawl_id,
    generate_crawl_timestamp,
)


class SEOPipeline:
    """Run the complete SEO data collection pipeline."""

    def __init__(self, timeout: int = 15):
        self.crawler = WebsiteCrawler(
            timeout=timeout
        )

    def analyze(self, url: str) -> dict:
        """
        Crawl, extract, validate, and identify
        a webpage observation.
        """

        # Identity of this crawl execution.
        crawl_id = generate_crawl_id()
        crawl_timestamp = generate_crawl_timestamp()

        # 1. Crawl
        crawl_result = self.crawler.fetch(url)

        status_code = crawl_result.get(
            "status_code"
        )

        if status_code != 200:
            return {
                "success": False,
                "crawl_id": crawl_id,
                "crawl_timestamp": crawl_timestamp,
                "url": url,
                "errors": [
                    (
                        "HTTP request failed with "
                        f"status {status_code}"
                    )
                ],
            }

        # 2. Extract the final URL and HTML.
        final_url = crawl_result["url"]
        html = crawl_result["html"]

        # 3. Generate page and content identities.
        page_id = generate_page_id(
            final_url
        )

        content_hash = generate_content_hash(
            html
        )

        # 4. HTML extraction.
        extractor = HTMLExtractor(
            html=html,
            base_url=final_url,
        )

        raw_features = extractor.extract_all()

        # 5. Schema validation.
        try:
            features = SEOFeatures(
                **raw_features
            )

        except Exception as error:
            return {
                "success": False,
                "crawl_id": crawl_id,
                "crawl_timestamp": crawl_timestamp,
                "page_id": page_id,
                "content_hash": content_hash,
                "url": final_url,
                "errors": [
                    f"Schema validation failed: {error}"
                ],
            }

        # 6. Logical data-quality validation.
        validation_errors = (
            validate_seo_features(features)
        )

        if validation_errors:
            return {
                "success": False,
                "crawl_id": crawl_id,
                "crawl_timestamp": crawl_timestamp,
                "page_id": page_id,
                "content_hash": content_hash,
                "url": final_url,
                "errors": validation_errors,
            }

        # 7. Valid observation.
        return {
            "success": True,
            "crawl_id": crawl_id,
            "crawl_timestamp": crawl_timestamp,
            "page_id": page_id,
            "content_hash": content_hash,
            "url": final_url,
            "domain": crawl_result["domain"],
            "status_code": crawl_result["status_code"],
            "response_time_ms": crawl_result[
                "response_time_ms"
            ],
            "redirect_count": crawl_result[
                "redirect_count"
            ],
            "features": features.model_dump(),
            "errors": [],
        }