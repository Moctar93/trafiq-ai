"""Train and evaluate ML baselines for TRAFIQ AI."""

from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


from ml.dataset_validator import (
    validate_dataset,
)

from ml.feature_config import (
    BOOLEAN_FEATURES,
    LABELS,
    TARGET_COLUMN,
)


DEFAULT_DATASET = Path(
    "data/processed/seo_training_dataset_v1.csv"
)

DEFAULT_REPORT = Path(
    "data/models/baseline_v1_report.json"
)

RANDOM_STATE = 42


def prepare_dataframe(
    df: pd.DataFrame,
    feature_columns: list[str],
):
    """Prepare X and y."""

    work = df.copy()

    for column in feature_columns:

        if column in BOOLEAN_FEATURES:

            work[column] = (
                work[column]
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

            work[column] = pd.to_numeric(
                work[column],
                errors="coerce",
            )

    y = (
        work[TARGET_COLUMN]
        .astype(str)
        .str.upper()
    )

    X = work[
        feature_columns
    ]

    return X, y


def build_preprocessor(
    feature_columns,
):
    """Build preprocessing pipeline."""

    numeric_features = [
        column
        for column in feature_columns
        if column not in BOOLEAN_FEATURES
    ]

    boolean_features = [
        column
        for column in feature_columns
        if column in BOOLEAN_FEATURES
    ]

    numeric_pipeline = Pipeline(
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
        ]
    )

    boolean_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                numeric_features,
            ),
            (
                "boolean",
                boolean_pipeline,
                boolean_features,
            ),
        ],
        remainder="drop",
    )


def build_models(
    feature_columns,
):
    """Build baseline models."""

    preprocessor = build_preprocessor(
        feature_columns
    )

    return {
        "logistic_regression": Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=5,
                        min_samples_leaf=1,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def evaluate_model(
    model,
    X,
    y,
    folds,
):
    """Evaluate with out-of-fold predictions."""

    predictions = np.empty(
        len(y),
        dtype=object,
    )

    fold_records = []

    for fold_index, (
        train_idx,
        test_idx,
    ) in enumerate(
        folds.split(X, y),
        start=1,
    ):

        X_train = X.iloc[
            train_idx
        ]

        X_test = X.iloc[
            test_idx
        ]

        y_train = y.iloc[
            train_idx
        ]

        y_test = y.iloc[
            test_idx
        ]

        model.fit(
            X_train,
            y_train,
        )

        y_pred = model.predict(
            X_test
        )

        predictions[test_idx] = (
            y_pred
        )

        fold_records.append(
            {
                "fold": fold_index,
                "accuracy": float(
                    accuracy_score(
                        y_test,
                        y_pred,
                    )
                ),
                "macro_f1": float(
                    f1_score(
                        y_test,
                        y_pred,
                        labels=LABELS,
                        average="macro",
                        zero_division=0,
                    )
                ),
            }
        )

    labels = [
        label
        for label in LABELS
        if label in set(y)
    ]

    matrix = confusion_matrix(
        y,
        predictions,
        labels=labels,
    )

    report = classification_report(
        y,
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    return {
        "oof_predictions": predictions.tolist(),
        "folds": fold_records,
        "accuracy": float(
            accuracy_score(
                y,
                predictions,
            )
        ),
        "macro_f1": float(
            f1_score(
                y,
                predictions,
                labels=LABELS,
                average="macro",
                zero_division=0,
            )
        ),
        "labels": labels,
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }


def main():
    dataset_path = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else DEFAULT_DATASET
    )

    report_path = Path(
        sys.argv[2]
        if len(sys.argv) > 2
        else DEFAULT_REPORT
    )

    (
        df,
        features,
        errors,
        warnings,
    ) = validate_dataset(
        dataset_path
    )

    if errors:

        print(
            "\nDataset validation failed."
        )

        for error in errors:
            print(
                f"❌ {error}"
            )

        return 1

    X, y = prepare_dataframe(
        df,
        features,
    )

    class_counts = (
        y.value_counts()
    )

    min_class_count = int(
        class_counts.min()
    )

    if min_class_count < 2:

        print(
            "\nNeed at least 2 examples per class "
            "for stratified cross-validation."
        )

        print(
            class_counts.to_string()
        )

        return 1

    n_splits = min(
        2,
        min_class_count,
    )

    folds = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    models = build_models(
        features
    )

    results = {
        "dataset_path": str(
            dataset_path
        ),
        "rows": int(
            len(df)
        ),
        "feature_count": int(
            len(features)
        ),
        "features": features,
        "class_distribution": {
            key: int(value)
            for key, value
            in class_counts.items()
        },
        "cv": {
            "type": "StratifiedKFold",
            "n_splits": n_splits,
            "random_state": RANDOM_STATE,
        },
        "models": {},
        "warnings": warnings,
    }

    print(
        "\n=== TRAFIQ AI — ML BASELINE V1 ==="
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Features: {len(features)}"
    )

    print(
        f"CV folds: {n_splits}"
    )

    for model_name, model in models.items():

        result = evaluate_model(
            model,
            X,
            y,
            folds,
        )

        results[
            "models"
        ][model_name] = result

        print(
            f"\n--- {model_name} ---"
        )

        print(
            f"Accuracy: "
            f"{result['accuracy']:.4f}"
        )

        print(
            f"Macro-F1: "
            f"{result['macro_f1']:.4f}"
        )

        print(
            "Confusion matrix:"
        )

        matrix_df = pd.DataFrame(
            result[
                "confusion_matrix"
            ],
            index=result["labels"],
            columns=result["labels"],
        )

        print(
            matrix_df.to_string()
        )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nReport saved to: "
        f"{report_path}"
    )

    print(
        "\nNOTE: With the current tiny dataset, "
        "this is a diagnostic baseline only."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )