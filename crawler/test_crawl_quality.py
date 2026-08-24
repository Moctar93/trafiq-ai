from crawler.pipeline import SEOPipeline


def main():
    pipeline = SEOPipeline()

    urls = [
        "https://www.cdiscount.com/",
        "https://www.decathlon.fr/",
        "https://www.lemonde.fr/",
    ]

    print(
        "\n=== TRAFIQ AI — CRAWL QUALITY TEST ==="
    )

    for url in urls:
        print(
            f"\n--- {url} ---"
        )

        result = pipeline.analyze(url)

        print(
            f"Success: "
            f"{result['success']}"
        )

        print(
            f"Status code: "
            f"{result.get('status_code')}"
        )

        print(
            f"HTML size: "
            f"{result.get('html_size_bytes')}"
        )

        print(
            f"Crawl quality: "
            f"{result.get('crawl_quality')}"
        )

        if result["success"]:
            features = result["features"]

            print(
                f"Word count: "
                f"{features['word_count']}"
            )

            print(
                f"Headings: "
                f"{features['heading_total_count']}"
            )

            print(
                f"Links: "
                f"{features['total_link_count']}"
            )

    print(
        "\n=== TEST COMPLETE ==="
    )


if __name__ == "__main__":
    main()