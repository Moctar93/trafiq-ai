from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.inspection import permutation_importance

from feature_config import CANDIDATE_FEATURES, LABELS


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "seo_training_dataset_v3.csv"
)

MODELS_DIR = BASE_DIR / "data" / "models"

IMPORTANCE_PATH = (
    MODELS_DIR / "feature_importance_v3.csv"
)

ANALYSIS_PATH = (
    MODELS_DIR / "feature_analysis_v3.json"
)


RANDOM_STATE = 42


def main() -> None:
    print("=" * 70)
    print("FEATURE ANALYSIS V3")
    print("=" * 70)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required = set(CANDIDATE_FEATURES) | {"consensus_label"}

    missing = sorted(required - set(df.columns))

    if missing:
        raise ValueError(
            "Colonnes manquantes dans le dataset : "
            + ", ".join(missing)
        )

    X = df[CANDIDATE_FEATURES].copy()
    y = (
        df["consensus_label"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    for column in CANDIDATE_FEATURES:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce",
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

    print(f"\nRows : {len(df)}")
    print(f"Features : {len(CANDIDATE_FEATURES)}")

    # ------------------------------------------------------------------
    # 1. Constant features
    # ------------------------------------------------------------------
    nunique = X.nunique(dropna=False)

    constant_features = (
        nunique[nunique <= 1]
        .index
        .tolist()
    )

    print("\nFeatures constantes :")
    if constant_features:
        for feature in constant_features:
            print(f"  - {feature}")
    else:
        print("  Aucune")

    # ------------------------------------------------------------------
    # 2. Descriptive statistics
    # ------------------------------------------------------------------
    numeric_stats = {}

    for feature in CANDIDATE_FEATURES:
        series = X[feature]

        numeric_stats[feature] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "std": float(series.std(ddof=0)),
            "unique_values": int(series.nunique(dropna=False)),
        }

    # ------------------------------------------------------------------
    # 3. Random Forest feature importance
    # ------------------------------------------------------------------
    rf = RandomForestClassifier(
        n_estimators=500,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    rf.fit(X, y)

    rf_importance = pd.Series(
        rf.feature_importances_,
        index=CANDIDATE_FEATURES,
        name="random_forest_importance",
    )

    # ------------------------------------------------------------------
    # 4. Permutation importance
    #
    # This is an exploratory analysis on the complete tiny training set,
    # not an unbiased generalization estimate.
    # ------------------------------------------------------------------
    permutation = permutation_importance(
        rf,
        X,
        y,
        n_repeats=20,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        scoring="f1_macro",
    )

    permutation_mean = pd.Series(
        permutation.importances_mean,
        index=CANDIDATE_FEATURES,
        name="permutation_importance_mean",
    )

    permutation_std = pd.Series(
        permutation.importances_std,
        index=CANDIDATE_FEATURES,
        name="permutation_importance_std",
    )

    # ------------------------------------------------------------------
    # 5. Mutual information
    #
    # Discrete flag follows the existing boolean feature configuration.
    # ------------------------------------------------------------------
    discrete_features = [
        column
        for column in CANDIDATE_FEATURES
        if column in {
            "title_exists",
            "meta_description_exists",
            "canonical_exists",
            "robots_meta_exists",
            "viewport_exists",
            "lang_exists",
        }
    ]

    discrete_mask = [
        feature in discrete_features
        for feature in CANDIDATE_FEATURES
    ]

    mi_scores = mutual_info_classif(
        X,
        y,
        discrete_features=discrete_mask,
        random_state=RANDOM_STATE,
    )

    mutual_information = pd.Series(
        mi_scores,
        index=CANDIDATE_FEATURES,
        name="mutual_information",
    )

    # ------------------------------------------------------------------
    # 6. Consolidated table
    # ------------------------------------------------------------------
    importance_df = pd.concat(
        [
            rf_importance,
            permutation_mean,
            permutation_std,
            mutual_information,
            nunique.rename("unique_values"),
        ],
        axis=1,
    )

    importance_df["is_constant"] = (
        importance_df["unique_values"] <= 1
    )

    importance_df = importance_df.sort_values(
        by="random_forest_importance",
        ascending=False,
    )

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    importance_df.to_csv(
        IMPORTANCE_PATH,
        index_label="feature",
        encoding="utf-8",
    )

    analysis = {
        "dataset": str(DATASET_PATH),
        "rows": int(len(df)),
        "feature_count": int(len(CANDIDATE_FEATURES)),
        "labels": LABELS,
        "class_distribution": {
            label: int(
                (y == label).sum()
            )
            for label in LABELS
        },
        "constant_features": constant_features,
        "warning": (
            "Feature importance is exploratory because the dataset "
            "contains only 15 observations. It must not be interpreted "
            "as a stable estimate of real-world feature impact."
        ),
        "top_random_forest_features": [
            {
                "feature": str(feature),
                "importance": float(row["random_forest_importance"]),
            }
            for feature, row in importance_df.head(20).iterrows()
        ],
        "top_permutation_features": [
            {
                "feature": str(feature),
                "importance_mean": float(
                    row["permutation_importance_mean"]
                ),
                "importance_std": float(
                    row["permutation_importance_std"]
                ),
            }
            for feature, row in importance_df.sort_values(
                "permutation_importance_mean",
                ascending=False,
            ).head(20).iterrows()
        ],
        "feature_statistics": numeric_stats,
    }

    with ANALYSIS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            analysis,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\nTop 20 Random Forest features :")
    print(
        importance_df[
            [
                "random_forest_importance",
                "permutation_importance_mean",
                "mutual_information",
                "is_constant",
            ]
        ]
        .head(20)
        .to_string()
    )

    print("\nFichiers générés :")
    print(f"- {IMPORTANCE_PATH}")
    print(f"- {ANALYSIS_PATH}")

    print("\n" + "=" * 70)
    print("FEATURE ANALYSIS V3 TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()