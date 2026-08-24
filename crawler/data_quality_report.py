import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    "data/processed/seo_dataset_v3.csv"
)


NUMERIC_FEATURES = [
    "title_length",
    "title_word_count",
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
    "total_link_count",
    "internal_link_count",
    "external_link_count",
    "nofollow_link_count",
    "sponsored_link_count",
    "ugc_link_count",
    "response_time_ms",
    "redirect_count",
    "alt_coverage_ratio",
    "internal_link_ratio",
    "html_size_bytes",
]


BOOLEAN_FEATURES = [
    "title_exists",
    "meta_description_exists",
]


def load_dataset() -> pd.DataFrame:
    """Load the processed SEO dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return pd.read_csv(DATASET_PATH)


def print_dataset_overview(
    df: pd.DataFrame,
):
    """Print basic dataset information."""

    print("\n=== DATASET OVERVIEW ===")

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print(
        f"Unique domains: "
        f"{df['domain'].nunique()}"
    )

    print(
        f"Unique pages: "
        f"{df['page_id'].nunique()}"
    )


def print_missing_values(
    df: pd.DataFrame,
):
    """Display missing values by feature."""

    print("\n=== MISSING VALUES ===")

    missing = df.isnull().sum()

    missing = missing[
        missing > 0
    ].sort_values(
        ascending=False
    )

    if missing.empty:
        print("No missing values detected.")
        return

    print(missing.to_string())


def print_numeric_statistics(
    df: pd.DataFrame,
):
    """Display descriptive statistics for numeric features."""

    print("\n=== NUMERIC STATISTICS ===")

    available_features = [
        feature
        for feature in NUMERIC_FEATURES
        if feature in df.columns
    ]

    statistics = df[
        available_features
    ].describe().T

    statistics = statistics[
        [
            "count",
            "mean",
            "std",
            "min",
            "50%",
            "max",
        ]
    ]

    statistics = statistics.rename(
        columns={
            "50%": "median",
        }
    )

    print(
        statistics.to_string(
            float_format=lambda value: (
                f"{value:.2f}"
            )
        )
    )


def print_boolean_distribution(
    df: pd.DataFrame,
):
    """Display boolean feature distributions."""

    print(
        "\n=== BOOLEAN FEATURE DISTRIBUTION ==="
    )

    for feature in BOOLEAN_FEATURES:

        if feature not in df.columns:
            continue

        print(
            f"\n{feature}:"
        )

        print(
            df[feature]
            .value_counts(dropna=False)
            .to_string()
        )


def print_domains(
    df: pd.DataFrame,
):
    """Display collected domains."""

    print("\n=== DOMAINS ===")

    print(
        df["domain"]
        .value_counts()
        .to_string()
    )

def print_group_statistics(df):
    print("\n=== CALIBRATION GROUP STATISTICS ===")

    feature_columns = [
        "word_count",
        "unique_word_ratio",
        "heading_total_count",
        "image_count",
        "alt_coverage_ratio",
        "total_link_count",
        "internal_link_ratio",
        "response_time_ms",
        "meta_description_length",
    ]

    available = [
        column
        for column in feature_columns
        if column in df.columns
    ]

    grouped = (
        df.groupby("calibration_group")[available]
        .agg(["mean", "median", "min", "max"])
    )

    print(
        grouped.to_string(
            float_format=lambda value: f"{value:.2f}"
        )
    )

def print_calibration_groups(df):
    print("\n=== CALIBRATION GROUP DISTRIBUTION ===")

    counts = (
        df["calibration_group"]
        .value_counts(dropna=False)
    )

    print(counts.to_string())


def main():
    print(
        "\n=== TRAFIQ AI — DATA QUALITY REPORT ==="
    )

    df = load_dataset()

    print_dataset_overview(df)

    print_domains(df)

    print_group_statistics(df)

    print_calibration_groups(df)

    print_missing_values(df)

    print_numeric_statistics(df)

    print_boolean_distribution(df)

    print(
        df["crawl_quality"]
        .value_counts(dropna=False)
        .to_string()
    )

    print(
        "\n=== REPORT COMPLETE ==="
    )


if __name__ == "__main__":
    main()