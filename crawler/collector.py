from crawler.pipeline import SEOPipeline
from crawler.storage import DatasetStorage


class SEOCollector:
    """Collect and store SEO observations from multiple URLs."""

    def __init__(self, timeout: int = 15):
        self.pipeline = SEOPipeline(
            timeout=timeout
        )
        self.storage = DatasetStorage()

    def collect(
        self,
        urls: list[str],
        calibration_group: str = "unknown",
    ) -> dict:
        """
        Crawl and store observations belonging to a
        calibration group.
        """

        summary = {
            "total": len(urls),
            "success": 0,
            "failed": 0,
            "duplicates": 0,
            "stored": 0,
        }

        for url in urls:
            print(
                f"\n--- Crawling: {url} ---"
            )

            result = self.pipeline.analyze(url)

            if not result["success"]:
                summary["failed"] += 1

                print("❌ Failed")

                for error in result["errors"]:
                    print(f"   - {error}")

                continue

            summary["success"] += 1

            result["calibration_group"] = (
                calibration_group
            )

            output = self.storage.append_processed(
                result
            )

            if output is None:
                summary["duplicates"] += 1

                print(
                    "↪ Duplicate skipped"
                )
            else:
                summary["stored"] += 1

                print(
                    f"✅ Stored: {output}"
                )

        return summary