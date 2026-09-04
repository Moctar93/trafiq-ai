"""Validate seo_training_dataset_v1.csv before ML."""

from pathlib import Path
import sys

import pandas as pd

from ml.feature_config import (
    LABELS,
    TARGET_COLUMN,
    get_feature_columns,
)


DEFAULT_DATASET = Path(
    "data/processed/seo_training_dataset_v1.csv"
)


def validate_dataset(path: Path):
    """Validate dataset and return dataframe plus diagnostics."""

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(path)

    errors = []
    warnings = []

    if df.empty:
        errors.append("Dataset is empty.")

    if TARGET_COLUMN not in df.columns:
        errors.append(
            f"Missing target column: {TARGET_COLUMN}"
        )

    features = get_feature_columns(
        df.columns
    )

    if not features:
        errors.append(
            "No configured ML features were found."
        )

    if TARGET_COLUMN in df.columns:

        missing_target = int(
            df[TARGET_COLUMN].isna().sum()
        )

        if missing_target:
            errors.append(
                f"{missing_target} rows have no human label."
            )

        labels = (
            df[TARGET_COLUMN]
            .dropna()
            .astype(str)
            .str.upper()
        )

        invalid_labels = sorted(
            set(labels) - set(LABELS)
        )

        if invalid_labels:
            errors.append(
                "Invalid labels: "
                + ", ".join(invalid_labels)
            )

        counts = labels.value_counts()

        for label in LABELS:
            count = int(
                counts.get(label, 0)
            )

            if count < 2:
                warnings.append(
                    f"Class {label} has only "
                    f"{count} labeled rows; "
                    "stratified CV may be unstable."
                )

    return (
        df,
        features,
        errors,
        warnings,
    )


def print_report(
    df,
    features,
    errors,
    warnings,
):
    """Print validation report."""

    print(
        "\n=== TRAFIQ AI — ML DATASET VALIDATION ==="
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Configured features: {len(features)}"
    )

    if TARGET_COLUMN in df.columns:

        print(
            "\n=== HUMAN LABEL DISTRIBUTION ==="
        )

        print(
            df[TARGET_COLUMN]
            .dropna()
            .astype(str)
            .str.upper()
            .value_counts()
            .to_string()
        )

    print(
        "\n=== FEATURE COLUMNS ==="
    )

    for feature in features:
        print(
            f"- {feature}"
        )

    print(
        "\n=== ERRORS ==="
    )

    if errors:
        for error in errors:
            print(
                f"❌ {error}"
            )
    else:
        print("None")

    print(
        "\n=== WARNINGS ==="
    )

    if warnings:
        for warning in warnings:
            print(
                f"⚠️ {warning}"
            )
    else:
        print("None")

    print(
        "\n=== VALIDATION STATUS ==="
    )

    print(
        "PASS"
        if not errors
        else "FAIL"
    )


def main():
    path = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else DEFAULT_DATASET
    )

    (
        df,
        features,
        errors,
        warnings,
    ) = validate_dataset(path)

    print_report(
        df,
        features,
        errors,
        warnings,
    )

    raise SystemExit(
        1 if errors else 0
    )


if __name__ == "__main__":
    main()