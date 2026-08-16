from crawler.crawler import WebsiteCrawler
from crawler.extractor import HTMLExtractor
from crawler.schemas import SEOFeatures
from crawler.validators import validate_seo_features


class SEOPipeline:
    """Run the complete SEO data collection and validation pipeline."""

    def __init__(self, timeout: int = 15):
        self.crawler = WebsiteCrawler(timeout=timeout)

    def analyze(self, url: str) -> dict:
        """
        Crawl, extract and validate a website.

        Returns:
            A structured analysis result.
        """

        # Step 1: Crawl
        crawl_result = self.crawler.fetch(url)

        # The current crawler returns a result without a success flag.
        # We therefore use the HTTP status code to determine whether
        # the request succeeded.
        if crawl_result.get("status_code") != 200:
            return {
                "success": False,
                "url": url,
                "errors": [
                    f"HTTP request failed with status "
                    f"{crawl_result.get('status_code')}"
                ],
            }

        # Step 2: Extract
        extractor = HTMLExtractor(
            html=crawl_result["html"],
            base_url=crawl_result["url"],
        )

        raw_features = extractor.extract_all()

        # Step 3: Schema validation
        try:
            features = SEOFeatures(**raw_features)
        except Exception as error:
            return {
                "success": False,
                "url": crawl_result["url"],
                "errors": [
                    f"Schema validation failed: {error}"
                ],
            }

        # Step 4: Data quality validation
        validation_errors = validate_seo_features(features)

        if validation_errors:
            return {
                "success": False,
                "url": crawl_result["url"],
                "errors": validation_errors,
            }

        # Step 5: Valid observation
        return {
            "success": True,
            "url": crawl_result["url"],
            "domain": crawl_result["domain"],
            "status_code": crawl_result["status_code"],
            "response_time_ms": crawl_result["response_time_ms"],
            "redirect_count": crawl_result["redirect_count"],
            "features": features.model_dump(),
            "errors": [],
        }