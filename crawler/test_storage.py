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

        storage.save_rejected(
            result,
            "example_com_rejected.json",
        )

        return

    raw_path = storage.save_raw(
        result,
        "example_com.json",
    )

    processed_path = storage.append_processed(
        result,
    )

    print(f"Raw observation: {raw_path}")
    print(f"Processed dataset: {processed_path}")
    print("Storage successful!")


if __name__ == "__main__":
    main()