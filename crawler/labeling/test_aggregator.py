from crawler.labeling import SEOClass
from crawler.labeling.aggregator import aggregate_labels


def main():
    labels = {
        "TITLE": SEOClass.POOR,
        "META": SEOClass.POOR,
        "HEADINGS": SEOClass.AVERAGE,
        "CONTENT": SEOClass.POOR,
        "IMAGES": SEOClass.ABSTAIN,
        "LINKS": SEOClass.POOR,
    }

    result = aggregate_labels(labels)

    print("\n=== TRAFIQ AI — AGGREGATOR TEST ===")

    print(f"Final label: {result['label']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Vote count: {result['vote_count']}")

    print("\n--- VOTES ---")

    for name, label in result["votes"].items():
        print(f"{name}: {label}")

    print("\n=== AMBIGUOUS CASE ===")

    ambiguous_labels = {
        "TITLE": SEOClass.GOOD,
        "META": SEOClass.POOR,
        "HEADINGS": SEOClass.GOOD,
        "CONTENT": SEOClass.POOR,
    }

    ambiguous_result = aggregate_labels(
        ambiguous_labels
    )

    print(
        f"Final label: "
        f"{ambiguous_result['label']}"
    )

    print(
        f"Confidence: "
        f"{ambiguous_result['confidence']}"
    )

    print(
        f"Ambiguous: "
        f"{ambiguous_result['ambiguous']}"
    )


if __name__ == "__main__":
    main()