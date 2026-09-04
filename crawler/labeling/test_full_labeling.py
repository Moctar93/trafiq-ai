from crawler.pipeline import SEOPipeline
from crawler.schemas import SEOFeatures

from crawler.labeling.functions import run_all_labeling_functions
from crawler.labeling.aggregator import aggregate_labels


def main():
    pipeline = SEOPipeline()

    result = pipeline.analyze(
        "https://example.com"
    )

    print("\n=== TRAFIQ AI — FULL LABELING PIPELINE TEST ===")

    if not result["success"]:
        print("Pipeline failed:")

        for error in result["errors"]:
            print(f"- {error}")

        return

    features = SEOFeatures(
        **result["features"]
    )

    labels = run_all_labeling_functions(
        features
    )

    aggregation = aggregate_labels(
        labels
    )

    print("\n--- LABELING ---")

    for name, label in labels.items():
        print(f"{name}: {label.value}")

    print("\n--- AGGREGATION ---")

    print(
        f"Final label: "
        f"{aggregation['label']}"
    )

    print(
        f"Confidence: "
        f"{aggregation['confidence']}"
    )

    print(
        f"Vote count: "
        f"{aggregation['vote_count']}"
    )

    print(
        f"Ambiguous: "
        f"{aggregation['ambiguous']}"
    )

    print(
        f"Training eligible: "
        f"{aggregation['training_eligible']}"
    )


if __name__ == "__main__":
    main()