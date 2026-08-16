import csv
from pathlib import Path

from crawler.schemas import SEOFeatures
from crawler.labeling.functions import run_all_labeling_functions
from crawler.labeling.aggregator import aggregate_labels


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "seo_dataset.csv"
OUTPUT_FILE = BASE_DIR / "seo_labeled_dataset.csv"


FEATURE_FIELDS = [
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
]


LABEL_FIELDS = [
    "title_label",
    "meta_label",
    "headings_label",
    "content_label",
    "images_label",
    "links_label",
    "final_label",
    "confidence",
    "vote_count",
    "ambiguous",
    "training_eligible",
]


def parse_bool(value: str) -> bool:
    """Convert a CSV boolean value into a Python bool."""

    return value.strip().lower() == "true"


def build_features(row: dict) -> SEOFeatures:
    """Build a validated SEOFeatures object from a CSV row."""

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
        unique_word_count=int(row["unique_word_count"]),

        unique_word_ratio=(
            float(row["unique_word_ratio"])
            if row["unique_word_ratio"] != ""
            else None
        ),

        image_count=int(row["image_count"]),
        images_with_alt=int(row["images_with_alt"]),
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


def label_row(row: dict) -> dict:
    """
    Generate labeling-function votes and aggregation
    results for one dataset row.
    """

    features = build_features(row)

    labels = run_all_labeling_functions(
        features
    )

    aggregation = aggregate_labels(
        labels
    )

    labeled = dict(row)

    labeled.update(
        {
            "title_label": labels[
                "TITLE"
            ].value,

            "meta_label": labels[
                "META"
            ].value,

            "headings_label": labels[
                "HEADINGS"
            ].value,

            "content_label": labels[
                "CONTENT"
            ].value,

            "images_label": labels[
                "IMAGES"
            ].value,

            "links_label": labels[
                "LINKS"
            ].value,

            "final_label": aggregation[
                "label"
            ],

            "confidence": aggregation[
                "confidence"
            ],

            "vote_count": aggregation[
                "vote_count"
            ],

            "ambiguous": aggregation[
                "ambiguous"
            ],

            "training_eligible": aggregation[
                "training_eligible"
            ],
        }
    )

    return labeled


def process_dataset():
    """Read the raw SEO dataset and create the labeled dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        rows = list(reader)

        if not rows:
            raise ValueError(
                "The input dataset is empty."
            )

        original_fields = reader.fieldnames or []

    labeled_rows = []

    for row in rows:
        labeled_rows.append(
            label_row(row)
        )

    output_fields = (
        original_fields
        + LABEL_FIELDS
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=output_fields,
        )

        writer.writeheader()

        writer.writerows(
            labeled_rows
        )

    return OUTPUT_FILE, labeled_rows


def main():
    print(
        "\n=== TRAFIQ AI — DATASET LABELING TEST ==="
    )

    output_file, rows = process_dataset()

    print(
        f"Input dataset: {INPUT_FILE}"
    )

    print(
        f"Labeled dataset: {output_file}"
    )

    print(
        f"Rows processed: {len(rows)}"
    )

    print("\n--- FIRST RESULT ---")

    first = rows[0]

    print(
        f"URL: {first['url']}"
    )

    print(
        f"Final label: "
        f"{first['final_label']}"
    )

    print(
        f"Confidence: "
        f"{first['confidence']}"
    )

    print(
        f"Training eligible: "
        f"{first['training_eligible']}"
    )

    print(
        "\nDataset labeling successful!"
    )


if __name__ == "__main__":
    main()