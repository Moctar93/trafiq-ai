import json
from pathlib import Path

import pandas as pd


DATASET_FILE = Path(
    "data/processed/seo_training_dataset_v1.csv"
)

REPORT_FILE = Path(
    "data/models/baseline_v1_report.json"
)


def load_data():
    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Report not found: {REPORT_FILE}"
        )

    df = pd.read_csv(
        DATASET_FILE
    )

    with REPORT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    return df, report


def main():
    print(
        "\n=== TRAFIQ AI — ML ERROR ANALYSIS V1 ==="
    )

    df, report = load_data()

    models = report.get(
        "models",
        {}
    )

    for model_name, result in models.items():

        predictions = result.get(
            "oof_predictions",
            []
        )

        if len(predictions) != len(df):
            print(
                f"\n⚠️ {model_name}: "
                "prediction count does not match dataset."
            )
            continue

        df[
            f"{model_name}_prediction"
        ] = predictions

    output_columns = [
        "domain",
        "url",
        "human_review_label",
        "weak_label",
        "weak_confidence",
        "weak_vote_count",
    ]

    model_columns = [
        column
        for column in df.columns
        if column.endswith(
            "_prediction"
        )
    ]

    output_columns.extend(
        model_columns
    )

    result_df = df[
        output_columns
    ].copy()

    for column in model_columns:

        prediction_column = column.replace(
            "_prediction",
            "",
        )

        result_df[
            f"{prediction_column}_match"
        ] = (
            result_df[
                column
            ]
            == result_df[
                "human_review_label"
            ]
        )

    print(
        "\n=== PAGE-LEVEL RESULTS ==="
    )

    print(
        result_df.to_string(
            index=False
        )
    )

    print(
        "\n=== MODEL ERROR SUMMARY ==="
    )

    for model_name in models:

        prediction_column = (
            f"{model_name}_prediction"
        )

        match_column = (
            f"{model_name}_match"
        )

        if (
            prediction_column
            not in result_df.columns
        ):
            continue

        matches = int(
            result_df[
                match_column
            ].sum()
        )

        total = len(
            result_df
        )

        print(
            f"{model_name}: "
            f"{matches}/{total} "
            f"({matches / total:.2%})"
        )

        print(
            "\nConfusion matrix:"
        )

        print(
            pd.crosstab(
                result_df[
                    "human_review_label"
                ],
                result_df[
                    prediction_column
                ],
                dropna=False,
            ).to_string()
        )

    print(
        "\n=== ERROR ANALYSIS COMPLETE ==="
    )


if __name__ == "__main__":
    main()