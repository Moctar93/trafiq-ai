"""
TRAFIQ AI — Feature Analysis V2

Diagnostic descriptif des features utilisées par le benchmark ML.

IMPORTANT:
Avec seulement 14 observations annotées, les importances calculées ici
ne constituent PAS une preuve statistique robuste. Elles servent à :
- repérer les features constantes ou quasi constantes ;
- identifier les signaux dominants ;
- détecter les features potentiellement bruitées ;
- préparer une V2.1 du jeu de features.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.dataset_validator import validate_dataset
from ml.feature_config import (
    BOOLEAN_FEATURES,
    LABELS,
)


DATASET_FILE = Path(
    "data/processed/seo_training_dataset_v2.csv"
)

JSON_OUTPUT = Path(
    "data/models/feature_analysis_v2.json"
)

CSV_OUTPUT = Path(
    "data/models/feature_importance_v2.csv"
)

RANDOM_STATE = 42


def prepare_features(
    df: pd.DataFrame,
    feature_columns: list[str],
):
    """
    Convert configured features to numeric values.
    """

    X = df[
        feature_columns
    ].copy()

    for column in feature_columns:

        if column in BOOLEAN_FEATURES:

            X[column] = (
                X[column]
                .astype(str)
                .str.strip()
                .str.lower()
                .map(
                    {
                        "true": 1.0,
                        "false": 0.0,
                    }
                )
            )

        else:

            X[column] = pd.to_numeric(
                X[column],
                errors="coerce",
            )

    y = (
        df["human_review_label"]
        .astype(str)
        .str.upper()
    )

    return X, y


def calculate_variance_report(
    X: pd.DataFrame,
):
    """
    Calculate descriptive statistics per feature.
    """

    rows = []

    for column in X.columns:

        series = X[column]

        non_null = series.dropna()

        unique_count = (
            non_null.nunique()
        )

        variance = (
            float(non_null.var())
            if len(non_null) > 1
            else 0.0
        )

        rows.append(
            {
                "feature": column,
                "count": int(
                    len(non_null)
                ),
                "missing": int(
                    series.isna().sum()
                ),
                "unique_values": int(
                    unique_count
                ),
                "variance": variance,
                "mean": (
                    float(non_null.mean())
                    if len(non_null)
                    else None
                ),
                "min": (
                    float(non_null.min())
                    if len(non_null)
                    else None
                ),
                "max": (
                    float(non_null.max())
                    if len(non_null)
                    else None
                ),
                "constant": (
                    unique_count <= 1
                ),
            }
        )

    report = pd.DataFrame(
        rows
    )

    return report.sort_values(
        by=[
            "constant",
            "variance",
        ],
        ascending=[
            False,
            True,
        ],
    )


def fit_random_forest(
    X: pd.DataFrame,
    y: pd.Series,
):
    """
    Fit Random Forest on the full tiny dataset.

    This is descriptive only; not a validation score.
    """

    pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=500,
                    max_depth=5,
                    min_samples_leaf=1,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    pipeline.fit(
        X,
        y,
    )

    classifier = pipeline[
        "classifier"
    ]

    importance = (
        classifier.feature_importances_
    )

    result = pd.DataFrame(
        {
            "feature": X.columns,
            "random_forest_importance": importance,
        }
    )

    return (
        pipeline,
        result.sort_values(
            "random_forest_importance",
            ascending=False,
        ),
    )


def fit_logistic_regression(
    X: pd.DataFrame,
    y: pd.Series,
):
    """
    Fit Logistic Regression on the full tiny dataset.

    Absolute coefficients are aggregated across classes.
    This is descriptive only.
    """

    pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    pipeline.fit(
        X,
        y,
    )

    classifier = pipeline[
        "classifier"
    ]

    coefficients = (
        np.asarray(
            classifier.coef_
        )
    )

    absolute_mean = np.mean(
        np.abs(coefficients),
        axis=0,
    )

    result = pd.DataFrame(
        {
            "feature": X.columns,
            "logistic_abs_mean_coefficient": (
                absolute_mean
            ),
        }
    )

    # --------------------------------------------------
    # Add per-class coefficients when available
    # --------------------------------------------------

    for index, class_name in enumerate(
        classifier.classes_
    ):

        result[
            f"logistic_coefficient_{class_name}"
        ] = coefficients[
            index
        ]

    return (
        pipeline,
        result.sort_values(
            "logistic_abs_mean_coefficient",
            ascending=False,
        ),
    )


def build_combined_importance(
    variance_df: pd.DataFrame,
    rf_df: pd.DataFrame,
    lr_df: pd.DataFrame,
):
    """
    Merge descriptive diagnostics.
    """

    result = variance_df.merge(
        rf_df,
        on="feature",
        how="left",
    ).merge(
        lr_df,
        on="feature",
        how="left",
    )

    return result.sort_values(
        by=[
            "random_forest_importance",
            "logistic_abs_mean_coefficient",
        ],
        ascending=False,
    )


def main():
    print(
        "\n=== TRAFIQ AI — FEATURE ANALYSIS V2 ==="
    )

    (
        df,
        feature_columns,
        errors,
        warnings,
    ) = validate_dataset(
        DATASET_FILE
    )

    if errors:

        print(
            "\nDataset validation failed:"
        )

        for error in errors:
            print(
                f"❌ {error}"
            )

        return 1

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Features: {len(feature_columns)}"
    )

    X, y = prepare_features(
        df,
        feature_columns,
    )

    # ==================================================
    # VARIANCE
    # ==================================================

    variance_df = (
        calculate_variance_report(
            X
        )
    )

    constant_features = (
        variance_df[
            variance_df[
                "constant"
            ]
        ]["feature"]
        .tolist()
    )

    print(
        "\n=== CONSTANT FEATURES ==="
    )

    if constant_features:

        for feature in constant_features:
            print(
                f"- {feature}"
            )

    else:

        print(
            "None"
        )

    # ==================================================
    # RANDOM FOREST
    # ==================================================

    (
        rf_pipeline,
        rf_df,
    ) = fit_random_forest(
        X,
        y,
    )

    print(
        "\n=== RANDOM FOREST IMPORTANCE ==="
    )

    print(
        rf_df.head(20).to_string(
            index=False
        )
    )

    # ==================================================
    # LOGISTIC REGRESSION
    # ==================================================

    (
        lr_pipeline,
        lr_df,
    ) = fit_logistic_regression(
        X,
        y,
    )

    print(
        "\n=== LOGISTIC REGRESSION COEFFICIENTS ==="
    )

    print(
        lr_df.head(20).to_string(
            index=False
        )
    )

    # ==================================================
    # COMBINED
    # ==================================================

    combined_df = (
        build_combined_importance(
            variance_df,
            rf_df,
            lr_df,
        )
    )

    # ==================================================
    # SAVE CSV
    # ==================================================

    CSV_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_df.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8",
    )

    # ==================================================
    # SAVE JSON
    # ==================================================

    top_rf = (
        rf_df.head(15)
        .to_dict(
            orient="records"
        )
    )

    top_lr = (
        lr_df.head(15)
        .to_dict(
            orient="records"
        )
    )

    json_report = {
        "dataset": str(
            DATASET_FILE
        ),
        "rows": int(
            len(df)
        ),
        "feature_count": int(
            len(feature_columns)
        ),
        "class_distribution": {
            label: int(
                (
                    y == label
                ).sum()
            )
            for label in LABELS
        },
        "constant_features": (
            constant_features
        ),
        "top_random_forest_features": (
            top_rf
        ),
        "top_logistic_features": (
            top_lr
        ),
        "warnings": warnings,
        "methodological_note": (
            "Full-dataset feature importance is "
            "descriptive only because the current "
            "human-reviewed dataset contains only "
            "14 observations."
        ),
    }

    JSON_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with JSON_OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            json_report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ==================================================
    # FINAL SUMMARY
    # ==================================================

    print(
        "\n=== OUTPUTS ==="
    )

    print(
        f"CSV: {CSV_OUTPUT}"
    )

    print(
        f"JSON: {JSON_OUTPUT}"
    )

    print(
        "\n=== FEATURE ANALYSIS COMPLETE ==="
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )