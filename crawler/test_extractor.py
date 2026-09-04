from crawler.pipeline import SEOPipeline


TEST_URLS = [
    "https://www.decathlon.fr/",
    "https://www.lemonde.fr/",
    "https://www.abondance.com/",
]


V4_FIELDS = [
    "canonical_exists",
    "robots_meta_exists",
    "viewport_exists",
    "lang_exists",
    "jsonld_count",
    "schema_org_count",
    "cta_count",
    "phone_count",
    "email_count",
    "external_unique_domain_count",
]


def main():
    print(
        "\n=== TRAFIQ AI — V4 FEATURE TEST ==="
    )

    pipeline = SEOPipeline()

    for url in TEST_URLS:

        print(
            f"\n--- {url} ---"
        )

        result = pipeline.analyze(
            url
        )

        if not result.get(
            "success",
            False,
        ):

            print(
                "❌ Crawl failed"
            )

            print(
                result.get(
                    "errors",
                    [],
                )
            )

            continue

        features = result[
            "features"
        ]

        print(
            f"HTML size: "
            f"{result.get('html_size_bytes')}"
        )

        print(
            f"Crawl quality: "
            f"{result.get('crawl_quality')}"
        )

        print(
            "\nV4 FEATURES:"
        )

        for field in V4_FIELDS:

            print(
                f"{field}: "
                f"{features.get(field)}"
            )

    print(
        "\n=== V4 FEATURE TEST COMPLETE ==="
    )


if __name__ == "__main__":
    main()