from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "seo_training_dataset_v3.csv"
)

MODELS_DIR = BASE_DIR / "data" / "models"

METRICS_PATH = MODELS_DIR / "baseline_metrics_v3.json"
PREDICTIONS_PATH = MODELS_DIR / "baseline_predictions_v3.csv"

LOGISTIC_MODEL_PATH = MODELS_DIR / "logistic_regression_v3.joblib"
RF_MODEL_PATH = MODELS_DIR / "random_forest_v3.joblib"

from feature_config import CANDIDATE_FEATURES, LABELS


RANDOM_STATE = 42
N_SPLITS = 3


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    """Load and validate the V3 training dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = set(CANDIDATE_FEATURES) | {"consensus_label"}

    missing_columns = sorted(required_columns - set(df.columns))

    if missing_columns:
        raise ValueError(
            "Colonnes manquantes dans le dataset V3 : "
            + ", ".join(missing_columns)
        )

    X = df[CANDIDATE_FEATURES].copy()
    y = (
        df["consensus_label"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    invalid_labels = sorted(set(y.unique()) - set(LABELS))

    if invalid_labels:
        raise ValueError(
            "Labels invalides : "
            + ", ".join(invalid_labels)
        )

    # Ensure numeric model inputs.
    for column in CANDIDATE_FEATURES:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce",
        )

    if X.isna().any().any():
        missing_counts = X.isna().sum()
        missing_counts = missing_counts[
            missing_counts > 0
        ].to_dict()

        raise ValueError(
            "Valeurs manquantes dans les features : "
            + str(missing_counts)
        )

    return df, X, y


def evaluate_model(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    cv: StratifiedKFold,
) -> tuple[dict, np.ndarray]:
    """Evaluate a model using stratified cross-validation."""
    predictions = cross_val_predict(
        model,
        X,
        y,
        cv=cv,
        method="predict",
    )

    accuracy = accuracy_score(y, predictions)
    macro_f1 = f1_score(
        y,
        predictions,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )
    balanced_accuracy = balanced_accuracy_score(
        y,
        predictions,
    )

    matrix = confusion_matrix(
        y,
        predictions,
        labels=LABELS,
    )

    report = classification_report(
        y,
        predictions,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "balanced_accuracy": float(balanced_accuracy),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }

    return metrics, predictions


def main() -> None:
    print("=" * 70)
    print("BASELINE ML V3")
    print("=" * 70)

    df, X, y = load_dataset()

    class_counts = y.value_counts()

    print(f"\nDataset : {DATASET_PATH}")
    print(f"Rows : {len(df)}")
    print(f"Features : {len(CANDIDATE_FEATURES)}")

    print("\nDistribution des classes :")
    print(class_counts.to_string())

    minimum_class_count = int(class_counts.min())

    if minimum_class_count < N_SPLITS:
        raise ValueError(
            f"Impossible d'utiliser {N_SPLITS}-fold stratifié : "
            f"la classe minoritaire ne contient que "
            f"{minimum_class_count} exemple(s)."
        )

    print(
        f"\nValidation : StratifiedKFold "
        f"({N_SPLITS} folds, shuffle=True, random_state={RANDOM_STATE})"
    )

    cv = StratifiedKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    # Logistic regression requires feature scaling.
    logistic_model = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=5000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    random_forest_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    models = {
        "Logistic Regression": logistic_model,
        "Random Forest": random_forest_model,
    }

    all_metrics: dict[str, object] = {
        "dataset": str(DATASET_PATH),
        "rows": int(len(df)),
        "feature_count": int(len(CANDIDATE_FEATURES)),
        "features": CANDIDATE_FEATURES,
        "labels": LABELS,
        "class_distribution": {
            label: int(class_counts.get(label, 0))
            for label in LABELS
        },
        "cv": {
            "method": "StratifiedKFold",
            "n_splits": N_SPLITS,
            "shuffle": True,
            "random_state": RANDOM_STATE,
        },
        "models": {},
    }

    prediction_df = df[
        [
            column
            for column in [
                "url",
                "domain",
                "consensus_label",
                "consensus_strength",
                "human_disagreement",
            ]
            if column in df.columns
        ]
    ].copy()

    for model_name, model in models.items():
        print("\n" + "-" * 70)
        print(model_name)
        print("-" * 70)

        metrics, predictions = evaluate_model(
            model,
            X,
            y,
            cv,
        )

        print(f"Accuracy          : {metrics['accuracy']:.4f}")
        print(f"Macro-F1          : {metrics['macro_f1']:.4f}")
        print(
            f"Balanced accuracy : "
            f"{metrics['balanced_accuracy']:.4f}"
        )

        print("\nConfusion matrix")
        print(
            pd.DataFrame(
                metrics["confusion_matrix"],
                index=LABELS,
                columns=LABELS,
            )
        )

        print("\nClassification report")
        report_df = pd.DataFrame(
            metrics["classification_report"]
        ).transpose()
        print(report_df.to_string())

        if model_name == "Logistic Regression":
            prefix = "logistic_regression"
        else:
            prefix = "random_forest"

        prediction_df[f"{prefix}_prediction"] = predictions

        all_metrics["models"][model_name] = metrics

        # Fit once on the complete V3 training dataset for later inference.
        model.fit(X, y)

        if model_name == "Logistic Regression":
            joblib.dump(
                model,
                LOGISTIC_MODEL_PATH,
            )
            print(
                f"\nModèle final sauvegardé : "
                f"{LOGISTIC_MODEL_PATH}"
            )
        else:
            joblib.dump(
                model,
                RF_MODEL_PATH,
            )
            print(
                f"\nModèle final sauvegardé : "
                f"{RF_MODEL_PATH}"
            )

    # Add simple correctness flags for error analysis.
    for model_name in models:
        prefix = (
            "logistic_regression"
            if model_name == "Logistic Regression"
            else "random_forest"
        )

        prediction_column = f"{prefix}_prediction"
        correct_column = f"{prefix}_correct"

        prediction_df[correct_column] = (
            prediction_df[prediction_column]
            == prediction_df["consensus_label"]
        )

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with METRICS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            all_metrics,
            file,
            indent=2,
            ensure_ascii=False,
        )

    prediction_df.to_csv(
        PREDICTIONS_PATH,
        index=False,
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)

    for model_name, metrics in all_metrics["models"].items():
        print(
            f"{model_name}: "
            f"Accuracy={metrics['accuracy']:.4f}, "
            f"Macro-F1={metrics['macro_f1']:.4f}, "
            f"Balanced Accuracy={metrics['balanced_accuracy']:.4f}"
        )

    print("\nFichiers générés :")
    print(f"- {METRICS_PATH}")
    print(f"- {PREDICTIONS_PATH}")
    print(f"- {LOGISTIC_MODEL_PATH}")
    print(f"- {RF_MODEL_PATH}")

    print("\n" + "=" * 70)
    print("BASELINE V3 TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()
