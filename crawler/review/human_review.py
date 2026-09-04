import csv
from pathlib import Path

from crawler.review.review_schema import (
    HumanReviewLabel,
)


INPUT_FILE = Path(
    "data/processed/seo_dataset_v3.csv"
)

OUTPUT_DIR = Path(
    "data/reviewed"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "seo_human_review_v1.csv"
)


REVIEW_URLS = [
    # ==================================================
    # KNOWN EDITED
    # ==================================================
    "https://essence-resilience.coach/",
    "https://jespomi.com/",
    "https://trafiq.fr/",
    "https://nkongsambapeguanto.ltd/",
    "https://depannage-rideaux-metalliques.fr/",
    "https://cabinet-3c.com/",
    "https://if-ca.fr/",

    # ==================================================
    # POOR CANDIDATES
    # ==================================================
    "https://ada13.org/",
    "https://toulemondencuisine.wordpress.com/",
    "https://jeanleptitplombier.com/",
    "https://a-un-clic-de-vous.fr/site-vitrine/trelaze/49800",
    "https://arret-net.fr/",

    # ==================================================
    # INTERMEDIATE
    # ==================================================
    "https://lageneraledetheatre.com/",
    "https://l-artisanat-a-la-francaise.fr/",

    # ==================================================
    # RICH
    # ==================================================
    "https://abondance.com/",
]


OUTPUT_COLUMNS = [
    "page_id",
    "url",
    "domain",
    "calibration_group",
    "crawl_quality",
    "human_review_label",
    "review_notes",
    "reviewed_at",
    "reviewer",
]


def load_dataset() -> list[dict]:
    """Load the V3 dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        return list(reader)


def normalize_url(
    url: str,
) -> str:
    """
    Normalize URL for comparison.

    Removes trailing slash but preserves
    path and query parameters.
    """

    return url.strip().rstrip("/")


def build_review_rows(
    rows: list[dict],
) -> list[dict]:
    """
    Select configured URLs and create
    human-review records.
    """

    by_url = {
        normalize_url(
            row["url"]
        ): row
        for row in rows
    }

    review_rows = []

    for target_url in REVIEW_URLS:

        normalized_target = normalize_url(
            target_url
        )

        row = by_url.get(
            normalized_target
        )

        # --------------------------------------------------
        # Try alternate www / non-www form
        # --------------------------------------------------

        if row is None:

            if normalized_target.startswith(
                "https://www."
            ):
                alternate = (
                    "https://"
                    + normalized_target[
                        len("https://www.") :
                    ]
                )

            elif normalized_target.startswith(
                "https://"
            ):
                alternate = (
                    "https://www."
                    + normalized_target[
                        len("https://") :
                    ]
                )

            else:
                alternate = normalized_target

            row = by_url.get(
                normalize_url(
                    alternate
                )
            )

        # --------------------------------------------------
        # URL missing
        # --------------------------------------------------

        if row is None:
            print(
                "⚠️ URL not found in dataset: "
                f"{target_url}"
            )
            continue

        # --------------------------------------------------
        # Crawl quality gate
        # --------------------------------------------------

        crawl_quality = row.get(
            "crawl_quality",
            "NORMAL",
        )

        if crawl_quality != "NORMAL":
            print(
                "⚠️ Skipping non-normal crawl: "
                f"{target_url} "
                f"({crawl_quality})"
            )
            continue

        review_rows.append(
            {
                "page_id": row["page_id"],
                "url": row["url"],
                "domain": row["domain"],
                "calibration_group": row.get(
                    "calibration_group",
                    "unknown",
                ),
                "crawl_quality": crawl_quality,
                "human_review_label": "",
                "review_notes": "",
                "reviewed_at": "",
                "reviewer": "",
            }
        )

    return review_rows


def save_review_file(
    review_rows: list[dict],
):
    """Save the human-review template."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()

        writer.writerows(
            review_rows
        )


def main():
    print(
        "\n=== TRAFIQ AI — HUMAN REVIEW V1 ==="
    )

    rows = load_dataset()

    review_rows = build_review_rows(
        rows
    )

    if not review_rows:
        print(
            "No reviewable observations found."
        )
        return

    save_review_file(
        review_rows
    )

    print(
        f"\nReview rows created: "
        f"{len(review_rows)}"
    )

    print(
        f"Review file: "
        f"{OUTPUT_FILE}"
    )

    print(
        "\nAllowed labels:"
    )

    for label in HumanReviewLabel:
        print(
            f"- {label.value}"
        )

    print(
        "\nExpected review rows: 15"
    )

    if len(review_rows) != 15:
        print(
            "⚠️ Warning: the generated review "
            "file does not contain 15 rows."
        )


if __name__ == "__main__":
    main()