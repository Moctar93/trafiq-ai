from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

PREDICTIONS_PATH = (
    BASE_DIR / "data" / "models" / "baseline_predictions_v3.csv"
)

OUTPUT_PATH = (
    BASE_DIR / "data" / "models" / "error_analysis_v3.csv"
)


def main() -> None:
    print("=" * 70)
    print("ERROR ANALYSIS V3")
    print("=" * 70)

    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(
            f"Fichier de prédictions introuvable : {PREDICTIONS_PATH}\n"
            "Lance d'abord : python ml/baseline_train_v3.py"
        )

    df = pd.read_csv(PREDICTIONS_PATH)

    required = {
        "url",
        "consensus_label",
        "consensus_strength",
        "human_disagreement",
        "logistic_regression_prediction",
        "random_forest_prediction",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise ValueError(
            "Colonnes manquantes dans les prédictions : "
            + ", ".join(missing)
        )

    df["rf_correct"] = (
        df["random_forest_prediction"] == df["consensus_label"]
    )
    df["logistic_correct"] = (
        df["logistic_regression_prediction"] == df["consensus_label"]
    )

    df["rf_error_type"] = "CORRECT"
    rf_error_mask = ~df["rf_correct"]
    df.loc[rf_error_mask, "rf_error_type"] = (
        df.loc[rf_error_mask, "consensus_label"]
        + " -> "
        + df.loc[rf_error_mask, "random_forest_prediction"]
    )

    df["logistic_error_type"] = "CORRECT"
    logistic_error_mask = ~df["logistic_correct"]
    df.loc[logistic_error_mask, "logistic_error_type"] = (
        df.loc[logistic_error_mask, "consensus_label"]
        + " -> "
        + df.loc[logistic_error_mask, "logistic_regression_prediction"]
    )

    print(f"\nPages analysées : {len(df)}")

    rf_correct = int(df["rf_correct"].sum())
    rf_errors = len(df) - rf_correct

    log_correct = int(df["logistic_correct"].sum())
    log_errors = len(df) - log_correct

    print("\nRandom Forest")
    print(f"  Correctes : {rf_correct}/{len(df)}")
    print(f"  Erreurs   : {rf_errors}/{len(df)}")

    print("\nTypes d'erreurs Random Forest :")
    rf_errors_df = df.loc[~df["rf_correct"]]

    if rf_errors_df.empty:
        print("  Aucune erreur.")
    else:
        print(
            rf_errors_df["rf_error_type"]
            .value_counts()
            .to_string()
        )

    print("\nLogistic Regression")
    print(f"  Correctes : {log_correct}/{len(df)}")
    print(f"  Erreurs   : {log_errors}/{len(df)}")

    print("\nTypes d'erreurs Logistic Regression :")
    log_errors_df = df.loc[~df["logistic_correct"]]

    if log_errors_df.empty:
        print("  Aucune erreur.")
    else:
        print(
            log_errors_df["logistic_error_type"]
            .value_counts()
            .to_string()
        )

    print("\n" + "-" * 70)
    print("DÉTAIL RANDOM FOREST")
    print("-" * 70)

    detail_columns = [
        "url",
        "consensus_label",
        "consensus_strength",
        "human_disagreement",
        "random_forest_prediction",
        "rf_correct",
        "rf_error_type",
        "logistic_regression_prediction",
    ]

    print(
        df[detail_columns]
        .sort_values(
            by=["rf_correct", "consensus_label", "url"],
            ascending=[True, True, True],
        )
        .to_string(index=False)
    )

    print("\n" + "-" * 70)
    print("ERREURS RANDOM FOREST PAR FORCE DE CONSENSUS")
    print("-" * 70)

    if not rf_errors_df.empty:
        print(
            pd.crosstab(
                rf_errors_df["consensus_strength"],
                rf_errors_df["rf_error_type"],
            ).to_string()
        )
    else:
        print("Aucune erreur.")

    # Save enriched row-level analysis.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    print(f"\nAnalyse sauvegardée : {OUTPUT_PATH}")

    print("\n" + "=" * 70)
    print("ERROR ANALYSIS V3 TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()
