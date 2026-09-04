from crawler.pipeline import SEOPipeline
from crawler.storage import DatasetStorage


TEST_FILENAME = "seo_dedup_test.csv"


def main():
    pipeline = SEOPipeline()
    storage = DatasetStorage()

    print(
        "\n=== TRAFIQ AI — DEDUPLICATION WRITE TEST ==="
    )

    # First crawl of the real page.
    result = pipeline.analyze(
        "https://example.com/"
    )

    if not result["success"]:
        print("Pipeline failed:")

        for error in result["errors"]:
            print(f"- {error}")

        return

    print("\n--- ORIGINAL OBSERVATION ---")
    print(f"Page ID: {result['page_id']}")
    print(f"Content hash: {result['content_hash']}")

    # Create a synthetic new page state.
    # Same page_id, but a different content_hash.
    updated_observation = dict(result)

    updated_observation["content_hash"] = (
        "synthetic_updated_content_hash_001"
    )

    print("\n--- TEST 1: NEW CONTENT VERSION ---")

    first_write = storage.append_processed(
        updated_observation,
        filename=TEST_FILENAME,
    )

    if first_write is None:
        print(
            "❌ New version was incorrectly "
            "identified as a duplicate."
        )
        return

    print(
        f"✅ New version stored: {first_write}"
    )

    # Try to store the exact same version again.
    print("\n--- TEST 2: SAME CONTENT VERSION ---")

    second_write = storage.append_processed(
        updated_observation,
        filename=TEST_FILENAME,
    )

    if second_write is None:
        print(
            "✅ Duplicate version correctly skipped."
        )
    else:
        print(
            "❌ Duplicate version was stored again."
        )
        return

    print(
        "\n=== DEDUPLICATION WRITE TEST PASSED ==="
    )


if __name__ == "__main__":
    main()