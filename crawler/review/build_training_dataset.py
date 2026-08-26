import csv
from pathlib import Path


REVIEW_FILE = Path(
    "data/reviewed/seo_human_review_v1.csv"
)

LABELED_FILE = Path(
    "data/processed/seo_labeled_dataset_v3.csv"
)

RAW_DATASET_FILE = Path(
    "data/processed/seo_dataset_v3.csv"
)

OUTPUT_FILE = Path(
    "data/processed/seo_training_dataset_v1.csv"
)


FEATURE_COLUMNS = [
    # Title
    "title_exists",
    "title_length",
    "title_word_count",

    # Meta
    "meta_description_exists",
    "meta_description_length",
    "meta_description_word_count",

    # Headings
    "h1_count",
    "h2_count",
    "h3_count",
    "h4_count",
    "h5_count",
    "h6_count",
    "heading_total_count",

    # Content
    "word_count",
    "character_count",
    "unique_word_count",
    "unique_word_ratio",

    # Images
    "image_count",
    "images_with_alt",
    "images_without_alt",
    "images_missing_alt_attribute",
    "empty_alt_count",
    "alt_coverage_ratio",

    # Links
    "total_link_count",
    "internal_link_count",
    "external_link_count",
    "nofollow_link_count",
    "sponsored_link_count",
    "ugc_link_count",
    "internal_link_ratio",
]


IDENTITY_COLUMNS = [
    "crawl_id",
    "page_id",
    "crawl_timestamp",
    "content_hash",
    "url",
    "domain",
]


METADATA_COLUMNS = [
    "calibration_group",
    "crawl_quality",
    "html_size_bytes",
    "status_code",
    "response_time_ms",
    "redirect_count",
]


OUTPUT_COLUMNS = (
    IDENTITY_COLUMNS
    + METADATA_COLUMNS
    + FEATURE_COLUMNS
    + [
        "human_review_label",
        "review_notes",
        "reviewed_at",
        "reviewer",
        "weak_label",
        "weak_confidence",
        "weak_vote_count",
        "weak_ambiguous",
        "weak_training_eligible",
    ]
)


def load_csv(
    path: Path,
) -> list[dict]:
    """Load a CSV file."""

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def validate_review_label(
    label: str,
) -> bool:
    """
    Validate the human label.

    Human-reviewed labels cannot be ABSTAIN.
    """

    return label in {
        "GOOD",
        "AVERAGE",
        "POOR",
    }


def build_index(
    rows: list[dict],
    key: str,
) -> dict[str, dict]:
    """Build an index by a given field."""

    return {
        row[key]: row
        for row in rows
        if row.get(key)
    }


def main():
    print(
        "\n=== TRAFIQ AI — BUILD TRAINING DATASET V1 ==="
    )

    review_rows = load_csv(
        REVIEW_FILE
    )

    raw_rows = load_csv(
        RAW_DATASET_FILE
    )

    labeled_rows = load_csv(
        LABELED_FILE
    )

    raw_by_page = build_index(
        raw_rows,
        "page_id",
    )

    labeled_by_page = build_index(
        labeled_rows,
        "page_id",
    )

    training_rows = []

    skipped_unreviewed = 0
    skipped_invalid = 0
    skipped_missing_raw = 0

    for review in review_rows:

        human_label = (
            review.get(
                "human_review_label",
                "",
            )
            .strip()
            .upper()
        )

        # ----------------------------------------------
        # Human review is mandatory
        # ----------------------------------------------

        if not human_label:
            skipped_unreviewed += 1
            continue

        if not validate_review_label(
            human_label
        ):
            skipped_invalid += 1
            continue

        page_id = review.get(
            "page_id",
            "",
        )

        raw = raw_by_page.get(
            page_id
        )

        if raw is None:
            skipped_missing_raw += 1
            continue

        weak = labeled_by_page.get(
            page_id
        )

        output_row = {}

        # ----------------------------------------------
        # Identity
        # ----------------------------------------------

        for column in IDENTITY_COLUMNS:
            output_row[column] = raw.get(
                column,
                "",
            )

        # ----------------------------------------------
        # Metadata
        # ----------------------------------------------

        for column in METADATA_COLUMNS:
            output_row[column] = raw.get(
                column,
                "",
            )

        # ----------------------------------------------
        # SEO features
        # ----------------------------------------------

        for column in FEATURE_COLUMNS:
            output_row[column] = raw.get(
                column,
                "",
            )

        # ----------------------------------------------
        # Human ground truth
        # ----------------------------------------------

        output_row[
            "human_review_label"
        ] = human_label

        output_row[
            "review_notes"
        ] = review.get(
            "review_notes",
            "",
        )

        output_row[
            "reviewed_at"
        ] = review.get(
            "reviewed_at",
            "",
        )

        output_row[
            "reviewer"
        ] = review.get(
            "reviewer",
            "",
        )

        # ----------------------------------------------
        # Weak-label information
        # ----------------------------------------------

        if weak is None:
            output_row[
                "weak_label"
            ] = ""

            output_row[
                "weak_confidence"
            ] = ""

            output_row[
                "weak_vote_count"
            ] = ""

            output_row[
                "weak_ambiguous"
            ] = ""

            output_row[
                "weak_training_eligible"
            ] = ""

        else:
            output_row[
                "weak_label"
            ] = weak.get(
                "final_label",
                "",
            )

            output_row[
                "weak_confidence"
            ] = weak.get(
                "confidence",
                "",
            )

            output_row[
                "weak_vote_count"
            ] = weak.get(
                "vote_count",
                "",
            )

            output_row[
                "weak_ambiguous"
            ] = weak.get(
                "ambiguous",
                "",
            )

            output_row[
                "weak_training_eligible"
            ] = weak.get(
                "training_eligible",
                "",
            )

        training_rows.append(
            output_row
        )

    # ----------------------------------------------
    # Save
    # ----------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()

        writer.writerows(
            training_rows
        )

    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    print(
        f"\nRows in review file: "
        f"{len(review_rows)}"
    )

    print(
        f"Training rows created: "
        f"{len(training_rows)}"
    )

    print(
        f"Unreviewed skipped: "
        f"{skipped_unreviewed}"
    )

    print(
        f"Invalid labels skipped: "
        f"{skipped_invalid}"
    )

    print(
        f"Missing raw observations skipped: "
        f"{skipped_missing_raw}"
    )

    print(
        f"\nTraining dataset: "
        f"{OUTPUT_FILE}"
    )

    print(
        "\nTraining dataset generated successfully."
    )


if __name__ == "__main__":
    main()