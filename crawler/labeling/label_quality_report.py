import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    "data/processed/seo_labeled_dataset_v3.csv"
)


LABEL_COLUMNS = [
    "title_label",
    "meta_label",
    "headings_label",
    "content_label",
    "images_label",
    "links_label",
]


def load_dataset() -> pd.DataFrame:
    """Load the V3 labeled dataset."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return pd.read_csv(
        DATASET_PATH
    )


def print_overview(
    df: pd.DataFrame,
):
    """Display basic dataset information."""

    print(
        "\n=== LABEL DATASET OVERVIEW ==="
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"Unique domains: "
        f"{df['domain'].nunique()}"
    )

    print(
        f"Unique pages: "
        f"{df['page_id'].nunique()}"
    )


def print_calibration_groups(
    df: pd.DataFrame,
):
    """Display calibration group distribution."""

    print(
        "\n=== CALIBRATION GROUP DISTRIBUTION ==="
    )

    if "calibration_group" not in df.columns:
        print(
            "calibration_group column not found."
        )
        return

    counts = (
        df["calibration_group"]
        .value_counts(dropna=False)
    )

    percentages = (
        df["calibration_group"]
        .value_counts(
            normalize=True,
            dropna=False,
        )
        * 100
    )

    for group in counts.index:
        print(
            f"{group}: "
            f"{counts[group]} "
            f"({percentages[group]:.1f}%)"
        )


def print_final_label_distribution(
    df: pd.DataFrame,
):
    """Display final label distribution."""

    print(
        "\n=== FINAL LABEL DISTRIBUTION ==="
    )

    counts = (
        df["final_label"]
        .value_counts(dropna=False)
    )

    percentages = (
        df["final_label"]
        .value_counts(
            normalize=True,
            dropna=False,
        )
        * 100
    )

    for label in counts.index:
        print(
            f"{label}: "
            f"{counts[label]} "
            f"({percentages[label]:.1f}%)"
        )


def print_labeling_function_distribution(
    df: pd.DataFrame,
):
    """Display the output distribution of each labeling function."""

    print(
        "\n=== LABELING FUNCTION DISTRIBUTION ==="
    )

    for column in LABEL_COLUMNS:

        if column not in df.columns:
            print(
                f"\n--- {column} ---"
            )
            print(
                "Column not found."
            )
            continue

        print(
            f"\n--- {column} ---"
        )

        counts = (
            df[column]
            .value_counts(dropna=False)
        )

        percentages = (
            df[column]
            .value_counts(
                normalize=True,
                dropna=False,
            )
            * 100
        )

        for label in counts.index:
            print(
                f"{label}: "
                f"{counts[label]} "
                f"({percentages[label]:.1f}%)"
            )


def print_confidence_distribution(
    df: pd.DataFrame,
):
    """Display confidence statistics."""

    print(
        "\n=== CONFIDENCE DISTRIBUTION ==="
    )

    statistics = (
        df["confidence"]
        .describe()
    )

    print(
        statistics.to_string(
            float_format=lambda value: (
                f"{value:.4f}"
            )
        )
    )


def print_training_eligibility(
    df: pd.DataFrame,
):
    """Display training eligibility distribution."""

    print(
        "\n=== TRAINING ELIGIBILITY ==="
    )

    counts = (
        df["training_eligible"]
        .value_counts(dropna=False)
    )

    percentages = (
        df["training_eligible"]
        .value_counts(
            normalize=True,
            dropna=False,
        )
        * 100
    )

    for value in counts.index:
        print(
            f"{value}: "
            f"{counts[value]} "
            f"({percentages[value]:.1f}%)"
        )


def print_label_by_calibration_group(
    df: pd.DataFrame,
):
    """
    Compare final labels with calibration groups.

    Calibration groups are experimental metadata.
    They are not treated as ground truth.
    """

    print(
        "\n=== FINAL LABEL BY CALIBRATION GROUP ==="
    )

    if "calibration_group" not in df.columns:
        print(
            "calibration_group column not found."
        )
        return

    table = pd.crosstab(
        df["calibration_group"],
        df["final_label"],
        margins=True,
    )

    print(
        table.to_string()
    )


def print_training_by_calibration_group(
    df: pd.DataFrame,
):
    """Display training eligibility by calibration group."""

    print(
        "\n=== TRAINING ELIGIBILITY BY CALIBRATION GROUP ==="
    )

    if "calibration_group" not in df.columns:
        print(
            "calibration_group column not found."
        )
        return

    table = pd.crosstab(
        df["calibration_group"],
        df["training_eligible"],
        margins=True,
    )

    print(
        table.to_string()
    )


def print_vote_patterns(
    df: pd.DataFrame,
):
    """Display individual labeling votes by domain."""

    columns = [
        "domain",
        "calibration_group",
        "title_label",
        "meta_label",
        "headings_label",
        "content_label",
        "images_label",
        "links_label",
        "final_label",
        "confidence",
        "training_eligible",
    ]

    available_columns = [
        column
        for column in columns
        if column in df.columns
    ]

    print(
        "\n=== LABELING VOTES BY DOMAIN ==="
    )

    print(
        df[available_columns].to_string(
            index=False
        )
    )


def print_abstain_distribution(
    df: pd.DataFrame,
):
    """Display abstention rates for all labeling functions."""

    print(
        "\n=== ABSTAIN DISTRIBUTION ==="
    )

    for column in LABEL_COLUMNS:

        if column not in df.columns:
            continue

        total = len(df)

        abstain_count = (
            df[column]
            .eq("ABSTAIN")
            .sum()
        )

        abstain_ratio = (
            abstain_count / total
            if total > 0
            else 0.0
        )

        print(
            f"{column}: "
            f"{abstain_count}/{total} "
            f"({abstain_ratio * 100:.1f}%)"
        )


def print_labeling_function_diversity(
    df: pd.DataFrame,
):
    """
    Show how many distinct labels each labeling function produces.
    """

    print(
        "\n=== LABELING FUNCTION DIVERSITY ==="
    )

    for column in LABEL_COLUMNS:

        if column not in df.columns:
            continue

        values = (
            df[column]
            .dropna()
            .unique()
        )

        print(
            f"{column}: "
            f"{len(values)} distinct labels "
            f"-> {sorted(values.tolist())}"
        )


def print_confidence_by_final_label(
    df: pd.DataFrame,
):
    """Display confidence statistics by final label."""

    print(
        "\n=== CONFIDENCE BY FINAL LABEL ==="
    )

    grouped = (
        df.groupby(
            "final_label"
        )["confidence"]
        .agg(
            [
                "count",
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
                f"{value:.4f}"
            )
        )
    )


def main():
    print(
        "\n=== TRAFIQ AI — V3 LABEL QUALITY REPORT ==="
    )

    try:
        df = load_dataset()

    except FileNotFoundError as error:
        print(error)
        return

    if df.empty:
        print(
            "Labeled dataset is empty."
        )
        return

    print_overview(df)

    print_calibration_groups(df)

    print_final_label_distribution(df)

    print_labeling_function_distribution(
        df
    )

    print_abstain_distribution(df)

    print_labeling_function_diversity(
        df
    )

    print_confidence_distribution(df)

    print_confidence_by_final_label(
        df
    )

    print_training_eligibility(df)

    print_label_by_calibration_group(
        df
    )

    print_training_by_calibration_group(
        df
    )

    print_vote_patterns(df)

    print(
        "\n=== LABEL QUALITY REPORT COMPLETE ==="
    )


if __name__ == "__main__":
    main()