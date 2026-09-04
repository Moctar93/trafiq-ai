"""Display the saved TRAFIQ AI baseline report."""

from pathlib import Path
import json
import sys


DEFAULT_REPORT = Path(
    "data/models/baseline_v1_report.json"
)


def main():
    report_path = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else DEFAULT_REPORT
    )

    if not report_path.exists():
        raise FileNotFoundError(
            f"Baseline report not found: "
            f"{report_path}"
        )

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        report = json.load(file)

    print(
        "\n=== TRAFIQ AI — BASELINE SUMMARY ==="
    )

    print(
        f"Rows: {report['rows']}"
    )

    print(
        f"Features: "
        f"{report['feature_count']}"
    )

    print(
        "\n=== CLASS DISTRIBUTION ==="
    )

    for label, count in report[
        "class_distribution"
    ].items():

        print(
            f"{label}: {count}"
        )

    print(
        "\n=== MODELS ==="
    )

    for name, result in report[
        "models"
    ].items():

        print(
            f"\n{name}"
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
        "\nBaseline report loaded successfully."
    )


if __name__ == "__main__":
    main()