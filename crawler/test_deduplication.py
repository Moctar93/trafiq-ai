from crawler.pipeline import SEOPipeline
from crawler.storage import DatasetStorage


def main():
    pipeline = SEOPipeline()
    storage = DatasetStorage()

    result = pipeline.analyze(
        "https://example.com/"
    )

    print("\n=== TRAFIQ AI — DEDUPLICATION TEST ===")

    if not result["success"]:
        print("Pipeline failed:")

        for error in result["errors"]:
            print(f"- {error}")

        return

    page_id = result["page_id"]
    content_hash = result["content_hash"]

    print(f"Page ID: {page_id}")
    print(f"Content hash: {content_hash}")

    duplicate = storage.is_duplicate(
        page_id=page_id,
        content_hash=content_hash,
    )

    print(
        f"\nAlready stored: {duplicate}"
    )


if __name__ == "__main__":
    main()