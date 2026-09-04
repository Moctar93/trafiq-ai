import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    "data/processed/seo_dataset_v3.csv"
)


ANALYSIS_COLUMNS = [
    "domain",
    "calibration_group",
    "word_count",
    "unique_word_ratio",
    "heading_total_count",
    "h1_count",
    "h2_count",
    "h3_count",
    "image_count",
    "images_without_alt",
    "images_missing_alt_attribute",
    "empty_alt_count",
    "alt_coverage_ratio",
    "total_link_count",
    "internal_link_count",
    "internal_link_ratio",
    "external_link_count",
    "response_time_ms",
    "meta_description_exists",
    "meta_description_length",
    "title_length",
]


def load_dataset() -> pd.DataFrame:
    """Load the V3 calibration dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return pd.read_csv(DATASET_PATH)


def print_group_distribution(
    df: pd.DataFrame,
):
    """Display the number of observations per calibration group."""

    print(
        "\n=== CALIBRATION GROUP DISTRIBUTION ==="
    )

    counts = (
        df["calibration_group"]
        .value_counts()
        .sort_index()
    )

    print(counts.to_string())


def print_observation_table(
    df: pd.DataFrame,
):
    """Display the most relevant features for each observation."""

    columns = [
        column
        for column in ANALYSIS_COLUMNS
        if column in df.columns
    ]

    print(
        "\n=== OBSERVATION-LEVEL CALIBRATION TABLE ==="
    )

    table = df[columns].copy()

    print(
        table.to_string(
            index=False,
            float_format=lambda value: (
                f"{value:.2f}"
            ),
        )
    )


def print_group_feature_summary(
    df: pd.DataFrame,
):
    """Display descriptive statistics by calibration group."""

    numeric_columns = [
        "word_count",
        "unique_word_ratio",
        "heading_total_count",
        "image_count",
        "images_without_alt",
        "alt_coverage_ratio",
        "total_link_count",
        "internal_link_ratio",
        "response_time_ms",
        "meta_description_length",
        "title_length",
        "image_count",
        "images_without_alt",
        "images_missing_alt_attribute",
        "empty_alt_count",
        "crawl_quality",
        "html_size_bytes",
        
    ]

    available = [
        column
        for column in numeric_columns
        if column in df.columns
    ]

    print(
        "\n=== GROUP FEATURE SUMMARY ==="
    )

    grouped = (
        df.groupby(
            "calibration_group",
            dropna=False,
        )[available]
        .agg(
            [
                "mean",
                "median",
                "min",
                "max",
            ]
        )
    )

    print(
        grouped.to_string(
            float_format=lambda value: (
                f"{value:.2f}"
            ),
        )
    )


def print_extreme_observations(
    df: pd.DataFrame,
):
    """Display observations at important feature extremes."""

    features = [
        "word_count",
        "heading_total_count",
        "alt_coverage_ratio",
        "internal_link_ratio",
        "response_time_ms",
    ]

    print(
        "\n=== FEATURE EXTREMES ==="
    )

    for feature in features:

        if feature not in df.columns:
            continue

        print(
            f"\n--- {feature} ---"
        )

        minimum = df.loc[
            df[feature].idxmin()
        ]

        maximum = df.loc[
            df[feature].idxmax()
        ]

        print(
            "MIN -> "
            f"{minimum['domain']} | "
            f"group={minimum['calibration_group']} | "
            f"value={minimum[feature]}"
        )

        print(
            "MAX -> "
            f"{maximum['domain']} | "
            f"group={maximum['calibration_group']} | "
            f"value={maximum[feature]}"
        )


def print_potential_contradictions(
    df: pd.DataFrame,
):
    """
    Highlight candidate groups whose observed features
    strongly overlap with other calibration groups.

    This is not a classification or ground-truth decision.
    It is only a diagnostic.
    """

    print(
        "\n=== POTENTIAL GROUP CONTRADICTIONS ==="
    )

    features = [
        "word_count",
        "heading_total_count",
        "alt_coverage_ratio",
        "internal_link_ratio",
        "response_time_ms",
    ]

    for feature in features:

        if feature not in df.columns:
            continue

        print(
            f"\n--- {feature} ---"
        )

        ordered = df.sort_values(
            feature
        )

        for _, row in ordered.iterrows():
            print(
                f"{row['domain']} | "
                f"group={row['calibration_group']} | "
                f"{feature}={row[feature]:.2f}"
            )

def print_crawl_quality_distribution(
    df: pd.DataFrame,
):
    """Display crawl quality distribution."""

    print(
        "\n=== CRAWL QUALITY DISTRIBUTION ==="
    )

    counts = (
        df["crawl_quality"]
        .value_counts(dropna=False)
    )

    print(
        counts.to_string()
    )   


def main():
    print(
        "\n=== TRAFIQ AI — CALIBRATION ANALYSIS ==="
    )

    df = load_dataset()

    print(
        f"\nRows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print_group_distribution(df)

    print_observation_table(df)

    print_group_feature_summary(df)

    print_extreme_observations(df)

    print_potential_contradictions(df)

    print_crawl_quality_distribution(df)

    print(
        "\n=== CALIBRATION ANALYSIS COMPLETE ==="
    )


if __name__ == "__main__":
    main()