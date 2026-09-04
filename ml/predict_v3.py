from __future__ import annotations

from pathlib import Path
from typing import Any

import json
import math

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "seo_training_dataset_v3.csv"
)

RECOMMENDATION_ENGINE_IMPORT = "recommendation_engine"

MODEL_PATH = (
    BASE_DIR
    / "data"
    / "models"
    / "random_forest_v3.joblib"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "models"
    / "prediction_v3_demo.json"
)


LABELS = ["POOR", "AVERAGE", "GOOD"]


def _import_recommendation_engine():
    """
    Import recommendation_engine whether this file is launched as:

        python ml/predict_v3.py

    or from the project root as a module.
    """
    try:
        from recommendation_engine import generate_recommendations

        return generate_recommendations
    except ModuleNotFoundError:
        from ml.recommendation_engine import generate_recommendations

        return generate_recommendations


from feature_config import CANDIDATE_FEATURES


def _json_safe(value: Any) -> Any:
    """Convert common pandas/numpy values into JSON-safe values."""
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return value

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def load_model():
    """Load the fitted Random Forest model."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH}\n"
            "Lance d'abord : python ml/baseline_train_v3.py"
        )

    return joblib.load(MODEL_PATH)


def validate_model_features(model) -> None:
    """Check that the model exposes the expected feature count."""
    if not hasattr(model, "n_features_in_"):
        return

    expected = len(CANDIDATE_FEATURES)

    if int(model.n_features_in_) != expected:
        raise ValueError(
            f"Le modèle attend {model.n_features_in_} features, "
            f"mais la configuration actuelle en contient {expected}."
        )


def prepare_features_from_row(row: pd.Series) -> pd.DataFrame:
    """Build the exact feature matrix expected by the model."""
    missing = [
        feature
        for feature in CANDIDATE_FEATURES
        if feature not in row.index
    ]

    if missing:
        raise ValueError(
            "Features manquantes dans la ligne : "
            + ", ".join(missing)
        )

    X = pd.DataFrame(
        [
            pd.to_numeric(
                row[CANDIDATE_FEATURES],
                errors="coerce",
            )
        ],
        columns=CANDIDATE_FEATURES,
    )

    if X.isna().any().any():
        missing_values = X.isna().sum()
        missing_values = missing_values[
            missing_values > 0
        ].to_dict()

        raise ValueError(
            "Valeurs manquantes dans les features : "
            + str(missing_values)
        )

    return X


def predict_row(
    row: pd.Series,
    model,
) -> dict[str, Any]:
    """
    Predict one SEO page and generate its recommendations.

    Confidence is represented by the maximum class probability returned
    by the Random Forest. It is a model score, not a calibrated probability
    of real-world correctness.
    """
    validate_model_features(model)

    X = prepare_features_from_row(row)

    prediction = str(model.predict(X)[0])

    if prediction not in LABELS:
        raise ValueError(
            f"Label prédit inattendu : {prediction}"
        )

    class_probabilities: dict[str, float] = {}

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[0]
        classes = model.classes_

        for class_name, probability in zip(
            classes,
            probabilities,
        ):
            class_probabilities[str(class_name)] = float(
                probability
            )

        confidence = max(
            class_probabilities.values()
        )
    else:
        confidence = None

    generate_recommendations = _import_recommendation_engine()

    recommendations = generate_recommendations(
        row.to_dict()
    )

    recommendation_dicts = []

    for item in recommendations:
        if hasattr(item, "__dataclass_fields__"):
            item_dict = {
                key: _json_safe(value)
                for key, value in vars(item).items()
            }
        else:
            item_dict = {
                key: _json_safe(value)
                for key, value in dict(item).items()
            }

        recommendation_dicts.append(item_dict)

    result = {
        "url": _json_safe(row.get("url")),
        "domain": _json_safe(row.get("domain")),
        "prediction": prediction,
        "confidence": confidence,
        "confidence_interpretation": (
            "Maximum class probability returned by the Random Forest; "
            "not a calibrated probability of correctness."
        ),
        "class_probabilities": class_probabilities,
        "recommendation_count": len(
            recommendation_dicts
        ),
        "recommendations": recommendation_dicts,
    }

    # Keep human consensus only when testing against an annotated example.
    # This is not used for prediction.
    if "consensus_label" in row.index:
        result["reference_consensus_label"] = _json_safe(
            row.get("consensus_label")
        )

    if "consensus_strength" in row.index:
        result["reference_consensus_strength"] = _json_safe(
            row.get("consensus_strength")
        )

    return result


def load_demo_row(
    row_index: int = 0,
) -> pd.Series:
    """Load one row from the V3 training dataset for demo inference."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    if df.empty:
        raise ValueError("Le dataset est vide.")

    if row_index < 0 or row_index >= len(df):
        raise IndexError(
            f"row_index={row_index} invalide pour {len(df)} ligne(s)."
        )

    return df.iloc[row_index]


def save_prediction(
    result: dict[str, Any],
) -> None:
    """Save an inference result to JSON."""
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    print("=" * 70)
    print("PREDICTION SERVICE V3")
    print("=" * 70)

    # Demo on the first annotated page.
    row = load_demo_row(row_index=0)
    model = load_model()

    print(f"\nURL : {row.get('url')}")
    print(f"Domain : {row.get('domain')}")
    print(f"Features utilisées : {len(CANDIDATE_FEATURES)}")

    result = predict_row(
        row=row,
        model=model,
    )

    print("\nPrediction :")
    print(f"  Classe : {result['prediction']}")

    if result["confidence"] is not None:
        print(
            f"  Confidence modèle : "
            f"{result['confidence']:.4f}"
        )

    print("\nProbabilités par classe :")
    for label in LABELS:
        probability = result["class_probabilities"].get(
            label,
            0.0,
        )
        print(
            f"  {label:<8}: {probability:.4f}"
        )

    if "reference_consensus_label" in result:
        print(
            "\nRéférence humaine (non utilisée par le modèle) : "
            f"{result['reference_consensus_label']}"
        )

    print(
        "\nNombre de recommandations : "
        f"{result['recommendation_count']}"
    )

    if result["recommendations"]:
        print("\nRecommandations :")

        for index, item in enumerate(
            result["recommendations"],
            start=1,
        ):
            print(
                f"\n  {index}. "
                f"[{item['severity']}] "
                f"{item['title']}"
            )

            print(
                f"     Feature : {item['feature']}"
            )

            print(
                f"     Valeur observée : "
                f"{item['observed_value']}"
            )

            print(
                f"     Recommandation : "
                f"{item['recommendation']}"
            )

    save_prediction(result)

    print(f"\nRésultat JSON : {OUTPUT_PATH}")

    print("\n" + "=" * 70)
    print("PREDICTION V3 TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()
