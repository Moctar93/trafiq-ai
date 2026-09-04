from pathlib import Path
import pandas as pd


RAW_V4_FILE = Path(
    "data/processed/seo_dataset_v4.csv"
)

HUMAN_REVIEW_FILE = Path(
    "data/reviewed/seo_human_review_v1.csv"
)

OUTPUT_FILE = Path(
    "data/processed/seo_training_dataset_v2.csv"
)


FEATURE_COLUMNS = [
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
    "heading_total_count",

    "word_count",
    "character_count",
    "unique_word_count",
    "unique_word_ratio",

    "image_count",
    "images_with_alt",
    "images_without_alt",
    "images_missing_alt_attribute",
    "empty_alt_count",
    "alt_coverage_ratio",

    "total_link_count",
    "internal_link_count",
    "external_link_count",
    "nofollow_link_count",
    "sponsored_link_count",
    "ugc_link_count",
    "internal_link_ratio",

    # V4
    "canonical_exists",
    "robots_meta_exists",
    "viewport_exists",
    "lang_exists",
    "jsonld_count",
    "schema_org_count",
    "cta_count",
    "phone_count",
    "email_count",
    "external_unique_domain_count",
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


REVIEW_COLUMNS = [
    "human_review_label",
    "review_notes",
    "reviewed_at",
    "reviewer",
]


WEAK_COLUMNS = [
    "weak_label",
    "weak_confidence",
    "weak_vote_count",
    "weak_ambiguous",
    "weak_training_eligible",
]


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    return pd.read_csv(path)


def normalize_url(value: str) -> str:
    """
    Normalize URL only for joining the datasets.

    We preserve the original URL in the output.
    """
    return str(value).strip().rstrip("/")


def main():
    print(
        "\n=== TRAFIQ AI — BUILD TRAINING DATASET V2 ==="
    )

    raw_df = load_csv(
        RAW_V4_FILE
    )

    review_df = load_csv(
        HUMAN_REVIEW_FILE
    )

    if "url" not in raw_df.columns:
        raise ValueError(
            "V4 dataset has no url column."
        )

    if "url" not in review_df.columns:
        raise ValueError(
            "Human review file has no url column."
        )

    raw_df["_join_url"] = (
        raw_df["url"]
        .map(normalize_url)
    )

    review_df["_join_url"] = (
        review_df["url"]
        .map(normalize_url)
    )

    # --------------------------------------------------
    # Only human-reviewed rows become training rows.
    # --------------------------------------------------

    merged = raw_df.merge(
        review_df[
            [
                "_join_url",
                *REVIEW_COLUMNS,
            ]
        ],
        on="_join_url",
        how="inner",
        suffixes=("", "_review"),
    )

    # --------------------------------------------------
    # Keep only actual human labels.
    # --------------------------------------------------

    merged[
        "human_review_label"
    ] = (
        merged[
            "human_review_label"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    before_filter = len(
        merged
    )

    merged = merged[
        merged[
            "human_review_label"
        ].isin(
            {
                "GOOD",
                "AVERAGE",
                "POOR",
            }
        )
    ].copy()

    skipped_unreviewed = (
        before_filter
        - len(merged)
    )

    # --------------------------------------------------
    # Weak labels come from V4 labeled dataset if
    # available. We locate the corresponding row by URL.
    # --------------------------------------------------

    weak_file = Path(
        "data/processed/seo_labeled_dataset_v4.csv"
    )

    weak_df = None

    if weak_file.exists():

        weak_df = load_csv(
            weak_file
        )

        if "url" in weak_df.columns:

            weak_df["_join_url"] = (
                weak_df["url"]
                .map(normalize_url)
            )

            weak_keep = [
                "_join_url",
                "final_label",
                "confidence",
                "vote_count",
                "ambiguous",
                "training_eligible",
            ]

            weak_keep = [
                column
                for column in weak_keep
                if column in weak_df.columns
            ]

            merged = merged.merge(
                weak_df[weak_keep],
                on="_join_url",
                how="left",
            )

    # --------------------------------------------------
    # Build output
    # --------------------------------------------------

    output_columns = []

    for column in IDENTITY_COLUMNS:
        if column in merged.columns:
            output_columns.append(
                column
            )

    for column in METADATA_COLUMNS:
        if column in merged.columns:
            output_columns.append(
                column
            )

    missing_features = [
        column
        for column in FEATURE_COLUMNS
        if column not in merged.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing V4 features: "
            + ", ".join(
                missing_features
            )
        )

    output_columns.extend(
        FEATURE_COLUMNS
    )

    output_columns.extend(
        [
            "human_review_label",
            "review_notes",
            "reviewed_at",
            "reviewer",
        ]
    )

    if weak_df is not None:

        weak_mapping = {
            "final_label": "weak_label",
            "confidence": "weak_confidence",
            "vote_count": "weak_vote_count",
            "ambiguous": "weak_ambiguous",
            "training_eligible": (
                "weak_training_eligible"
            ),
        }

        for source, target in weak_mapping.items():

            if source in merged.columns:

                merged[target] = (
                    merged[source]
                )

                output_columns.append(
                    target
                )

    # --------------------------------------------------
    # Deduplicate output columns while preserving order.
    # --------------------------------------------------

    output_columns = list(
        dict.fromkeys(
            output_columns
        )
    )

    output_df = merged[
        output_columns
    ].copy()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print(
        f"\nV4 source rows: {len(raw_df)}"
    )

    print(
        f"Human review rows matched: "
        f"{before_filter}"
    )

    print(
        f"Training rows created: "
        f"{len(output_df)}"
    )

    print(
        f"Unreviewed skipped: "
        f"{skipped_unreviewed}"
    )

    print(
        f"Feature count: "
        f"{len(FEATURE_COLUMNS)}"
    )

    print(
        f"Output columns: "
        f"{len(output_df.columns)}"
    )

    print(
        "\n=== HUMAN LABEL DISTRIBUTION ==="
    )

    print(
        output_df[
            "human_review_label"
        ]
        .value_counts()
        .to_string()
    )

    print(
        f"\nDataset written to: "
        f"{OUTPUT_FILE}"
    )

    print(
        "\nTraining dataset V2 generated successfully."
    )


if __name__ == "__main__":
    main()