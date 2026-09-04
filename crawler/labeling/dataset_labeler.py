import csv

from crawler.schemas import SEOFeatures
from crawler.storage import DatasetStorage

from crawler.labeling.functions import (
    run_all_labeling_functions,
)

from crawler.labeling.aggregator import (
    aggregate_labels,
)


INPUT_FILE = (
    "data/processed/seo_dataset_v3.csv"
)

OUTPUT_FILE = (
    "seo_labeled_dataset_v3.csv"
)


def parse_bool(value: str) -> bool:
    """Convert a CSV boolean value to Python bool."""

    return value.strip().lower() == "true"


def parse_optional_float(
    value: str,
):
    """Convert an optional CSV float value."""

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    return float(value)


def build_features(
    row: dict,
) -> SEOFeatures:
    """
    Build a validated SEOFeatures object
    from one V3 CSV row.
    """

    return SEOFeatures(
        # ==================================================
        # TITLE
        # ==================================================
        title_exists=parse_bool(
            row["title_exists"]
        ),
        title_length=int(
            row["title_length"]
        ),
        title_word_count=int(
            row["title_word_count"]
        ),

        # ==================================================
        # META DESCRIPTION
        # ==================================================
        meta_description_exists=parse_bool(
            row["meta_description_exists"]
        ),
        meta_description_length=int(
            row["meta_description_length"]
        ),
        meta_description_word_count=int(
            row["meta_description_word_count"]
        ),

        # ==================================================
        # HEADINGS
        # ==================================================
        h1_count=int(
            row["h1_count"]
        ),
        h2_count=int(
            row["h2_count"]
        ),
        h3_count=int(
            row["h3_count"]
        ),
        h4_count=int(
            row["h4_count"]
        ),
        h5_count=int(
            row["h5_count"]
        ),
        h6_count=int(
            row["h6_count"]
        ),
        heading_total_count=int(
            row["heading_total_count"]
        ),

        # ==================================================
        # CONTENT
        # ==================================================
        word_count=int(
            row["word_count"]
        ),
        character_count=int(
            row["character_count"]
        ),
        unique_word_count=int(
            row["unique_word_count"]
        ),
        unique_word_ratio=parse_optional_float(
            row["unique_word_ratio"]
        ),

        # ==================================================
        # IMAGES
        # ==================================================
        image_count=int(
            row["image_count"]
        ),
        images_with_alt=int(
            row["images_with_alt"]
        ),
        images_without_alt=int(
            row["images_without_alt"]
        ),
        images_missing_alt_attribute=int(
            row[
                "images_missing_alt_attribute"
            ]
        ),
        empty_alt_count=int(
            row["empty_alt_count"]
        ),
        alt_coverage_ratio=parse_optional_float(
            row["alt_coverage_ratio"]
        ),

        # ==================================================
        # LINKS
        # ==================================================
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
        internal_link_ratio=parse_optional_float(
            row["internal_link_ratio"]
        ),
    )


def build_observation(
    row: dict,
) -> dict:
    """
    Convert one V3 CSV row into the observation
    format expected by DatasetStorage.
    """

    feature_fields = {
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
    }

    features = {
        key: row[key]
        for key in feature_fields
    }

    return {
        # ==================================================
        # IDENTITY
        # ==================================================
        "crawl_id": row["crawl_id"],
        "page_id": row["page_id"],
        "crawl_timestamp": row[
            "crawl_timestamp"
        ],
        "content_hash": row[
            "content_hash"
        ],

        # ==================================================
        # CALIBRATION METADATA
        # ==================================================
        "calibration_group": row.get(
            "calibration_group",
            "unknown",
        ),

        # ==================================================
        # CRAWL QUALITY
        # ==================================================
        "crawl_quality": row.get(
            "crawl_quality",
            "NORMAL",
        ),

        "html_size_bytes": int(
            row.get(
                "html_size_bytes",
                0,
            )
        ),

        # ==================================================
        # HTTP / URL
        # ==================================================
        "url": row["url"],
        "domain": row["domain"],
        "status_code": int(
            row["status_code"]
        ),
        "response_time_ms": float(
            row["response_time_ms"]
        ),
        "redirect_count": int(
            row["redirect_count"]
        ),

        # ==================================================
        # SEO FEATURES
        # ==================================================
        "features": features,
    }


def validate_required_columns(
    rows: list[dict],
) -> list[str]:
    """
    Validate that the V3 dataset contains
    all required columns.
    """

    if not rows:
        return []

    required_columns = {
        # Identity
        "crawl_id",
        "page_id",
        "crawl_timestamp",
        "content_hash",

        # Calibration metadata
        "calibration_group",

        # Crawl quality metadata
        "crawl_quality",
        "html_size_bytes",

        # HTTP
        "url",
        "domain",
        "status_code",
        "response_time_ms",
        "redirect_count",

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
    }

    available_columns = set(
        rows[0].keys()
    )

    return sorted(
        required_columns - available_columns
    )


def main():
    print(
        "\n=== TRAFIQ AI — V3.3 DATASET LABELING TEST ==="
    )

    storage = DatasetStorage()

    # ======================================================
    # LOAD DATASET
    # ======================================================

    try:
        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(
                file
            )

            rows = list(reader)

    except FileNotFoundError:
        print(
            f"Dataset not found: {INPUT_FILE}"
        )
        return

    if not rows:
        print(
            "Dataset is empty."
        )
        return

    # ======================================================
    # VALIDATE COLUMNS
    # ======================================================

    missing_columns = (
        validate_required_columns(
            rows
        )
    )

    if missing_columns:
        print(
            "\nV3 dataset is missing "
            "required columns:"
        )

        for column in missing_columns:
            print(
                f"- {column}"
            )

        return

    # ======================================================
    # COUNTERS
    # ======================================================

    processed = 0
    duplicates = 0
    errors = 0
    suspect_skipped = 0

    # ======================================================
    # PROCESS ROWS
    # ======================================================

    for row in rows:

        try:
            url = row.get(
                "url",
                "unknown URL",
            )

            calibration_group = row.get(
                "calibration_group",
                "unknown",
            )

            crawl_quality = row.get(
                "crawl_quality",
                "NORMAL",
            )

            # ----------------------------------------------
            # Build observation first so that crawl metadata
            # is preserved even when labeling is skipped.
            # ----------------------------------------------

            observation = build_observation(
                row
            )

            # ----------------------------------------------
            # QUALITY GATE
            # ----------------------------------------------

            if crawl_quality != "NORMAL":

                suspect_skipped += 1

                print(
                    f"\nURL: {url}"
                )

                print(
                    "Calibration group: "
                    f"{calibration_group}"
                )

                print(
                    "Crawl quality: "
                    f"{crawl_quality}"
                )

                print(
                    "SEO labeling skipped: "
                    "suspect crawl."
                )

                continue

            # ----------------------------------------------
            # Build validated SEO features
            # ----------------------------------------------

            features = build_features(
                row
            )

            # ----------------------------------------------
            # Run labeling functions
            # ----------------------------------------------

            labels = (
                run_all_labeling_functions(
                    features
                )
            )

            # ----------------------------------------------
            # Aggregate labels
            # ----------------------------------------------

            aggregation = (
                aggregate_labels(
                    labels
                )
            )

            # ----------------------------------------------
            # Store labeled observation
            # ----------------------------------------------

            output = storage.append_labeled(
                observation=observation,
                labels=labels,
                aggregation=aggregation,
                filename=OUTPUT_FILE,
            )

            if output is None:
                duplicates += 1

                print(
                    f"\nURL: {url}"
                )

                print(
                    "Calibration group: "
                    f"{calibration_group}"
                )

                print(
                    "↪ Duplicate labeled observation skipped."
                )

                continue

            processed += 1

            # ----------------------------------------------
            # Display result
            # ----------------------------------------------

            print(
                f"\nURL: {url}"
            )

            print(
                "Calibration group: "
                f"{calibration_group}"
            )

            print(
                "Crawl quality: "
                f"{crawl_quality}"
            )

            print(
                "HTML size: "
                f"{observation['html_size_bytes']} bytes"
            )

            for name, label in labels.items():
                print(
                    f"{name}: "
                    f"{label.value}"
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

        except Exception as error:
            errors += 1

            print(
                f"\n❌ Error processing "
                f"{row.get('url', 'unknown URL')}"
            )

            print(
                f"   {error}"
            )

    # ======================================================
    # SUMMARY
    # ======================================================

    print(
        "\n=== LABELING SUMMARY ==="
    )

    print(
        f"Rows processed: "
        f"{processed}"
    )

    print(
        f"Suspect crawls skipped: "
        f"{suspect_skipped}"
    )

    print(
        f"Duplicates skipped: "
        f"{duplicates}"
    )

    print(
        f"Rows with errors: "
        f"{errors}"
    )

    print(
        "\nV3.3 labeled dataset generated "
        "successfully!"
    )


if __name__ == "__main__":
    main()