import csv

from crawler.schemas import SEOFeatures
from crawler.storage import DatasetStorage

from crawler.labeling.functions import (
    run_all_labeling_functions,
)

from crawler.labeling.aggregator import (
    aggregate_labels,
)


INPUT_FILE = "data/processed/seo_dataset.csv"


def parse_bool(value: str) -> bool:
    """Convert CSV boolean values to Python booleans."""

    return value.strip().lower() == "true"


def build_features(row: dict) -> SEOFeatures:
    """Convert a CSV row into validated SEOFeatures."""

    return SEOFeatures(
        title_exists=parse_bool(row["title_exists"]),
        title_length=int(row["title_length"]),
        title_word_count=int(row["title_word_count"]),

        meta_description_exists=parse_bool(
            row["meta_description_exists"]
        ),
        meta_description_length=int(
            row["meta_description_length"]
        ),
        meta_description_word_count=int(
            row["meta_description_word_count"]
        ),

        h1_count=int(row["h1_count"]),
        h2_count=int(row["h2_count"]),
        h3_count=int(row["h3_count"]),
        h4_count=int(row["h4_count"]),
        h5_count=int(row["h5_count"]),
        h6_count=int(row["h6_count"]),

        word_count=int(row["word_count"]),
        character_count=int(row["character_count"]),
        unique_word_count=int(
            row["unique_word_count"]
        ),

        unique_word_ratio=(
            float(row["unique_word_ratio"])
            if row["unique_word_ratio"]
            else None
        ),

        image_count=int(row["image_count"]),
        images_with_alt=int(
            row["images_with_alt"]
        ),
        images_without_alt=int(
            row["images_without_alt"]
        ),
        empty_alt_count=int(
            row["empty_alt_count"]
        ),

        total_link_count=int(
            row["total_link_count"]
        ),
        internal_link_count=int(
            row["internal_link_count"]
        ),
        external_link_count=int(
            row["external_link_count"]
        ),
        nofollow_link_count=int(
            row["nofollow_link_count"]
        ),
        sponsored_link_count=int(
            row["sponsored_link_count"]
        ),
        ugc_link_count=int(
            row["ugc_link_count"]
        ),
    )


def build_observation(row: dict) -> dict:
    """Convert a CSV row into the observation format used by storage."""

    feature_fields = {
        "title_exists",
        "title_length",
        "title_word_count",
        "meta_description_exists",
        "meta_description_length",
        "meta_description_word_count",
        "h1_count",
        "h2_count",
        "h3_count",
        "h4_count",
        "h5_count",
        "h6_count",
        "word_count",
        "character_count",
        "unique_word_count",
        "unique_word_ratio",
        "image_count",
        "images_with_alt",
        "images_without_alt",
        "empty_alt_count",
        "total_link_count",
        "internal_link_count",
        "external_link_count",
        "nofollow_link_count",
        "sponsored_link_count",
        "ugc_link_count",
    }

    features = {
        key: row[key]
        for key in feature_fields
    }

    return {
        "url": row["url"],
        "domain": row["domain"],
        "status_code": int(row["status_code"]),
        "response_time_ms": float(
            row["response_time_ms"]
        ),
        "redirect_count": int(
            row["redirect_count"]
        ),
        "features": features,
    }


def main():
    print(
        "\n=== TRAFIQ AI — DATASET LABELING TEST ==="
    )

    storage = DatasetStorage()

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    if not rows:
        print("Dataset is empty.")
        return

    processed = 0

    for row in rows:

        features = build_features(row)

        labels = run_all_labeling_functions(
            features
        )

        aggregation = aggregate_labels(
            labels
        )

        observation = build_observation(
            row
        )

        storage.append_labeled(
            observation=observation,
            labels=labels,
            aggregation=aggregation,
        )

        processed += 1

        print(
            f"\nURL: {row['url']}"
        )

        for name, label in labels.items():
            print(
                f"{name}: {label.value}"
            )

        print(
            f"Final label: "
            f"{aggregation['label']}"
        )

        print(
            f"Confidence: "
            f"{aggregation['confidence']}"
        )

        print(
            f"Training eligible: "
            f"{aggregation['training_eligible']}"
        )

    print(
        f"\nRows processed: {processed}"
    )

    print(
        "\nLabeled dataset created successfully!"
    )


if __name__ == "__main__":
    main()