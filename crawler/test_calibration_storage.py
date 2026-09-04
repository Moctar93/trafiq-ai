import csv
from pathlib import Path


DATASET_PATH = Path(
    "data/processed/seo_dataset_v3.csv"
)


def main():
    print(
        "\n=== TRAFIQ AI — CALIBRATION STORAGE TEST ==="
    )

    if not DATASET_PATH.exists():
        print(
            f"Dataset not found: {DATASET_PATH}"
        )
        return

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    if not rows:
        print("Dataset is empty.")
        return

    print(
        f"Rows: {len(rows)}"
    )

    print(
        "\n--- CALIBRATION GROUPS ---"
    )

    groups = {}

    for row in rows:
        group = row.get(
            "calibration_group",
            "unknown",
        )

        groups[group] = (
            groups.get(group, 0) + 1
        )

    for group, count in groups.items():
        print(
            f"{group}: {count}"
        )

    print(
        "\n--- FIRST ROW ---"
    )

    first = rows[0]

    print(
        f"Domain: {first['domain']}"
    )

    print(
        "Calibration group: "
        f"{first.get('calibration_group')}"
    )

    print(
        "\nCalibration storage test successful!"
    )


if __name__ == "__main__":
    main()