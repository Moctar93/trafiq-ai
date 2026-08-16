from crawler.pipeline import SEOPipeline


def main():
    pipeline = SEOPipeline()

    result = pipeline.analyze(
        "https://example.com"
    )

    print("\n=== TRAFIQ AI — FULL PIPELINE TEST ===")

    print(f"Success: {result['success']}")
    print(f"URL: {result['url']}")

    if result["success"]:
        print(f"Domain: {result['domain']}")
        print(f"Status code: {result['status_code']}")
        print(
            f"Response time: "
            f"{result['response_time_ms']} ms"
        )
        print(
            f"Redirect count: "
            f"{result['redirect_count']}"
        )

        print("\n--- SEO FEATURES ---")

        for key, value in result["features"].items():
            print(f"{key}: {value}")

    else:
        print("\n--- ERRORS ---")

        for error in result["errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()