import csv
from pathlib import Path


TRAINING_FILE = Path(
    "data/processed/seo_training_dataset_v1.csv"
)

LABELED_FILE = Path(
    "data/processed/seo_labeled_dataset_v3.csv"
)


LABEL_COLUMNS = [
    "title_label",
    "meta_label",
    "headings_label",
    "content_label",
    "images_label",
    "links_label",
]


def load_csv(
    path: Path,
) -> list[dict]:
    """Load a CSV file."""

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        return list(
            csv.DictReader(file)
        )


def build_index(
    rows: list[dict],
    key: str,
) -> dict[str, dict]:
    """Build an index by page ID."""

    return {
        row[key]: row
        for row in rows
        if row.get(key)
    }


def print_row(
    row: dict,
    weak_row: dict | None,
):
    """Print one human/weak comparison."""

    human = row.get(
        "human_review_label",
        "",
    )

    weak = row.get(
        "weak_label",
        "",
    )

    confidence = row.get(
        "weak_confidence",
        "",
    )

    vote_count = row.get(
        "weak_vote_count",
        "",
    )

    ambiguous = row.get(
        "weak_ambiguous",
        "",
    )

    print(
        f"\nDOMAIN: {row['domain']}"
    )

    print(
        f"Human: {human}"
    )

    print(
        f"Weak: {weak}"
    )

    print(
        f"Confidence: {confidence}"
    )

    print(
        f"Vote count: {vote_count}"
    )

    print(
        f"Ambiguous: {ambiguous}"
    )

    print(
        "\n--- LABELING FUNCTIONS ---"
    )

    if weak_row is None:

        print(
            "⚠️ Weak-label row not found."
        )

    else:

        for column in LABEL_COLUMNS:

            value = weak_row.get(
                column,
                "",
            )

            print(
                f"{column}: {value}"
            )

    if human == weak:

        print(
            "\n✅ MATCH"
        )

    elif weak == "ABSTAIN":

        print(
            "\n⚠️ ABSTAIN"
        )

    else:

        print(
            "\n❌ MISMATCH"
        )


def main():
    print(
        "\n=== TRAFIQ AI — HUMAN VS WEAK ANALYSIS V2 ==="
    )

    training_rows = load_csv(
        TRAINING_FILE
    )

    labeled_rows = load_csv(
        LABELED_FILE
    )

    labeled_by_page = build_index(
        labeled_rows,
        "page_id",
    )

    matches = 0
    mismatches = 0
    abstains = 0

    for row in training_rows:

        human = row.get(
            "human_review_label",
            "",
        )

        if not human:
            continue

        weak = row.get(
            "weak_label",
            "",
        )

        weak_row = labeled_by_page.get(
            row.get("page_id", "")
        )

        if human == weak:

            matches += 1

        elif weak == "ABSTAIN":

            abstains += 1

        else:

            mismatches += 1

        print_row(
            row,
            weak_row,
        )

    total = (
        matches
        + mismatches
        + abstains
    )

    print(
        "\n=== SUMMARY ==="
    )

    print(
        f"Total reviewed: {total}"
    )

    print(
        f"Matches: {matches}"
    )

    print(
        f"Mismatches: {mismatches}"
    )

    print(
        f"Abstains: {abstains}"
    )

    decisive = (
        matches
        + mismatches
    )

    if decisive > 0:

        print(
            "Decisive agreement: "
            f"{matches / decisive:.2%}"
        )

    print(
        "\n=== ANALYSIS COMPLETE ==="
    )


if __name__ == "__main__":
    main()