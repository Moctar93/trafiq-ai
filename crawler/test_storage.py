from crawler.pipeline import SEOPipeline
from crawler.storage import DatasetStorage


def main():
    pipeline = SEOPipeline()
    storage = DatasetStorage()

    result = pipeline.analyze(
        "https://example.com"
    )

    print("\n=== TRAFIQ AI — STORAGE TEST ===")

    if not result["success"]:
        print("Pipeline failed:")

        for error in result["errors"]:
            print(f"- {error}")

        return

    print("\n--- OBSERVATION IDENTITY ---")
    print(f"Crawl ID: {result['crawl_id']}")
    print(f"Page ID: {result['page_id']}")
    print(
        f"Crawl timestamp: "
        f"{result['crawl_timestamp']}"
    )
    print(
        f"Content hash: "
        f"{result['content_hash']}"
    )

    raw_path = storage.save_raw(
        result,
        "example_com.json",
    )

    processed_path = storage.append_processed(
        result,
    )

    print(
        f"\nRaw observation: {raw_path}"
    )

    if processed_path is None:
        print(
            "Processed observation skipped: duplicate."
        )
    else:
        print(
            f"Processed dataset: "
            f"{processed_path}"
        )

    print("\nStorage test completed!")


if __name__ == "__main__":
    main()