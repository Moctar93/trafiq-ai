from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ml.feature_config import CANDIDATE_FEATURES
from ml.recommendation_engine import generate_recommendations

from crawler.pipeline import SEOPipeline


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR
    / "data"
    / "models"
    / "random_forest_v3.joblib"
)

DEFAULT_OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "models"
)


LABELS = ["POOR", "AVERAGE", "GOOD"]


def json_safe(value: Any) -> Any:
    """Convert common pandas/numpy values to JSON-safe values."""
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
    """Load the fitted Random Forest V3 model."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH}\n"
            "Lance d'abord : python ml/baseline_train_v3.py"
        )

    return joblib.load(MODEL_PATH)


def prepare_feature_frame(features: dict[str, Any]) -> pd.DataFrame:
    """Build a one-row DataFrame using exactly the 40 ML features."""
    missing = [
        feature
        for feature in CANDIDATE_FEATURES
        if feature not in features
    ]

    if missing:
        raise ValueError(
            "Features manquantes après le crawl : "
            + ", ".join(missing)
        )

    X = pd.DataFrame(
        [
            {
                feature: pd.to_numeric(
                    features[feature],
                    errors="coerce",
                )
                for feature in CANDIDATE_FEATURES
            }
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


def run_analysis(
    url: str,
    timeout: int = 15,
) -> dict[str, Any]:
    """Run crawler -> ML prediction -> recommendation engine."""
    pipeline = SEOPipeline(timeout=timeout)

    observation = pipeline.analyze(url)

    if not observation.get("success", False):
        return {
            "success": False,
            "url": observation.get("url", url),
            "domain": observation.get("domain", ""),
            "crawl_quality": observation.get(
                "crawl_quality",
                "FAILED",
            ),
            "status_code": observation.get("status_code"),
            "crawl_id": observation.get("crawl_id"),
            "crawl_timestamp": observation.get(
                "crawl_timestamp"
            ),
            "errors": observation.get(
                "errors",
                ["Crawler failed."],
            ),
        }

    crawl_quality = observation.get(
        "crawl_quality",
        "FAILED",
    )

    # A suspect capture is returned for transparency, but not sent to ML.
    if crawl_quality != "NORMAL":
        return {
            "success": False,
            "url": observation.get("url", url),
            "domain": observation.get("domain", ""),
            "crawl_quality": crawl_quality,
            "status_code": observation.get("status_code"),
            "crawl_id": observation.get("crawl_id"),
            "crawl_timestamp": observation.get(
                "crawl_timestamp"
            ),
            "message": (
                "Le crawl a abouti mais la qualité de capture est "
                f"{crawl_quality}. L'inférence ML est interrompue "
                "pour éviter de prédire à partir de données potentiellement "
                "incomplètes."
            ),
            "errors": observation.get("errors", []),
        }

    model = load_model()
    features = observation["features"]

    X = prepare_feature_frame(features)

    expected_feature_count = len(CANDIDATE_FEATURES)

    if hasattr(model, "n_features_in_"):
        if int(model.n_features_in_) != expected_feature_count:
            raise ValueError(
                f"Le modèle attend {model.n_features_in_} features, "
                f"mais Trafiq AI en fournit {expected_feature_count}."
            )

    prediction = str(model.predict(X)[0])

    if prediction not in LABELS:
        raise ValueError(
            f"Label prédit inattendu : {prediction}"
        )

    class_probabilities: dict[str, float] = {}

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[0]

        for class_name, probability in zip(
            model.classes_,
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

    # Recommendations use only the crawled features.
    recommendations = generate_recommendations(
        {
            **observation["features"],
            "url": observation.get("url", url),
            "domain": observation.get("domain", ""),
        }
    )

    recommendation_dicts = []

    for recommendation in recommendations:
        item = dict(vars(recommendation))

        item = {
            key: json_safe(value)
            for key, value in item.items()
        }

        recommendation_dicts.append(item)

    result: dict[str, Any] = {
        "success": True,
        "url": observation.get("url", url),
        "domain": observation.get("domain", ""),
        "crawl_quality": crawl_quality,
        "crawl_id": observation.get("crawl_id"),
        "crawl_timestamp": observation.get(
            "crawl_timestamp"
        ),
        "status_code": observation.get("status_code"),
        "response_time_ms": observation.get(
            "response_time_ms"
        ),
        "redirect_count": observation.get(
            "redirect_count"
        ),
        "html_size_bytes": observation.get(
            "html_size_bytes"
        ),
        "feature_count": len(CANDIDATE_FEATURES),
        "prediction": prediction,
        "confidence": confidence,
        "confidence_interpretation": (
            "Maximum class probability returned by the Random Forest. "
            "It is kept as-is for the current demo and is not a calibrated "
            "probability of correctness."
        ),
        "class_probabilities": class_probabilities,
        "recommendation_count": len(
            recommendation_dicts
        ),
        "recommendations": recommendation_dicts,
    }

    return result


def print_result(result: dict[str, Any]) -> None:
    """Print a human-readable analysis."""
    print("\n" + "=" * 70)
    print("TRAFIQ AI - SEO ANALYSIS")
    print("=" * 70)

    print(f"\nURL : {result.get('url')}")
    print(f"Domain : {result.get('domain')}")
    print(
        f"Crawl quality : "
        f"{result.get('crawl_quality')}"
    )

    if not result.get("success", False):
        print("\nSTATUT : ANALYSE NON DISPONIBLE")

        if result.get("message"):
            print(
                f"\nMessage : {result['message']}"
            )

        errors = result.get("errors", [])

        if errors:
            print("\nErreurs :")
            for error in errors:
                print(f"  - {error}")

        print("\n" + "=" * 70)
        return

    print(
        f"Features extraites : "
        f"{result.get('feature_count')}"
    )

    print("\nML prediction")
    print(
        f"  Classe : "
        f"{result.get('prediction')}"
    )

    confidence = result.get("confidence")

    if confidence is not None:
        print(
            f"  Confidence : "
            f"{confidence:.2%}"
        )

    print("\nProbabilités par classe :")

    probabilities = result.get(
        "class_probabilities",
        {},
    )

    for label in LABELS:
        print(
            f"  {label:<8}: "
            f"{probabilities.get(label, 0.0):.2%}"
        )

    recommendations = result.get(
        "recommendations",
        [],
    )

    print(
        "\nRecommandations : "
        f"{len(recommendations)}"
    )

    if not recommendations:
        print("  Aucune recommandation déclenchée.")
    else:
        severity_order = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }

        sorted_recommendations = sorted(
            recommendations,
            key=lambda item: (
                severity_order.get(
                    item.get("severity", "LOW"),
                    99,
                ),
                item.get("category", ""),
            ),
        )

        for index, item in enumerate(
            sorted_recommendations,
            start=1,
        ):
            print(
                f"\n  {index}. "
                f"[{item.get('severity')}] "
                f"{item.get('title')}"
            )

            print(
                f"     Catégorie : "
                f"{item.get('category')}"
            )

            print(
                f"     Feature : "
                f"{item.get('feature')}"
            )

            print(
                f"     Valeur : "
                f"{item.get('observed_value')}"
            )

            print(
                f"     Action : "
                f"{item.get('recommendation')}"
            )

            print(
                f"     Pourquoi : "
                f"{item.get('explanation')}"
            )

    print("\n" + "=" * 70)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Run a complete Trafiq AI analysis: "
            "URL -> crawler -> 40 features -> ML -> recommendations."
        )
    )

    parser.add_argument(
        "url",
        help="URL du site à analyser.",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout du crawler en secondes (défaut: 15).",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Chemin du JSON de sortie. "
            "Par défaut: data/models/analysis_<domain>.json"
        ),
    )

    return parser.parse_args()


def build_output_path(
    result: dict[str, Any],
    requested_output: Path | None,
) -> Path:
    """Build a safe output path for the JSON result."""
    if requested_output is not None:
        return requested_output

    domain = str(
        result.get("domain")
        or "unknown"
    )

    safe_domain = "".join(
        character
        if character.isalnum() or character in "._-"
        else "_"
        for character in domain
    )

    return (
        DEFAULT_OUTPUT_DIR
        / f"analysis_{safe_domain}.json"
    )


def main() -> None:
    args = parse_args()

    url = args.url.strip()

    if not url:
        raise ValueError(
            "L'URL ne peut pas être vide."
        )

    result = run_analysis(
        url=url,
        timeout=args.timeout,
    )

    print_result(result)

    output_path = build_output_path(
        result,
        args.output,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nRésultat JSON : "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()
