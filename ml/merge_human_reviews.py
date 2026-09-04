"""
TRAFIQ AI — Merge multi-annotator human reviews.

Supported input formats:
- CSV
- XLSX / XLSM

Usage:
    python -m ml.merge_human_reviews

Or directly:
    python ml/merge_human_reviews.py \
        data/reviewed/seo_human_review_v1.csv \
        data/reviewed/audit_seo_15_sites.xlsx

The script:
1. Loads two human-review files.
2. Normalizes URLs/domains for matching.
3. Keeps each annotator's original label/score/notes.
4. Computes vote counts and consensus.
5. Flags disagreement / ambiguity.
6. Writes one merged CSV.

Important:
- No existing human label is overwritten.
- Consensus is a derived field, not an absolute truth.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd


DEFAULT_FIRST_REVIEW = Path(
    "data/reviewed/seo_human_review_v1.csv"
)

DEFAULT_SECOND_REVIEW = Path(
    "data/reviewed/seo_human_review_v2.csv"
)

DEFAULT_OUTPUT = Path(
    "data/reviewed/seo_human_review_merged_v1.csv"
)

VALID_LABELS = {"GOOD", "AVERAGE", "POOR"}

LABEL_ORDER = ["GOOD", "AVERAGE", "POOR"]


def normalize_text(value: object) -> str:
    """Normalize text for stable matching."""
    if value is None:
        return ""

    text = str(value).strip().lower()

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    return text


def normalize_url(value: object) -> str:
    """
    Normalize URLs for matching.

    This intentionally does not alter the original URLs
    stored in the merged output.
    """

    text = normalize_text(value)

    if not text:
        return ""

    text = re.sub(
        r"^https?://",
        "",
        text,
    )

    text = re.sub(
        r"^www\.",
        "",
        text,
    )

    text = text.split("?", 1)[0]
    text = text.split("#", 1)[0]

    text = text.rstrip("/")

    return text


def normalize_domain(value: object) -> str:
    """Normalize a domain similarly to URLs."""
    text = normalize_text(value)

    if not text:
        return ""

    text = re.sub(
        r"^https?://",
        "",
        text,
    )

    text = re.sub(
        r"^www\.",
        "",
        text,
    )

    text = text.split("/", 1)[0]

    return text.rstrip(".")


def matching_keys(url: object) -> set[str]:
    """
    Produce several matching keys.

    The goal is to tolerate harmless differences such as:
    - www vs non-www
    - accents in domains
    - trailing slash
    """

    normalized = normalize_url(url)

    if not normalized:
        return set()

    keys = {normalized}

    domain = normalized.split("/", 1)[0]

    # Domain-only key is useful for homepage comparisons.
    if "/" not in normalized:
        keys.add(
            f"domain:{normalize_domain(domain)}"
        )

    return keys


def read_review_file(path: Path) -> pd.DataFrame:
    """Read CSV or Excel review file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Review file not found: {path}"
        )

    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xlsm", ".xls"}:
        # The workbook supplied for annotator #2 uses
        # the "Audit SEO" sheet.
        workbook = pd.ExcelFile(path)

        if "Audit SEO" in workbook.sheet_names:
            return pd.read_excel(
                path,
                sheet_name="Audit SEO",
            )

        return pd.read_excel(
            path,
            sheet_name=0,
        )

    return pd.read_csv(
        path,
        encoding="utf-8-sig",
    )


def standardize_review_columns(
    df: pd.DataFrame,
    annotator_name: str,
) -> pd.DataFrame:
    """
    Map common review column names to a standard schema.
    """

    column_map: dict[str, str] = {}

    for column in df.columns:

        normalized = normalize_text(
            column
        )

        if normalized in {
            "site",
            "url",
        }:
            column_map[column] = "url"

        elif normalized in {
            "human review label",
            "human_review_label",
            "label",
        }:
            column_map[column] = (
                "human_review_label"
            )

        elif normalized in {
            "score",
            "score 100",
            "score_100",
            "note",
        }:
            column_map[column] = "score_100"

        elif normalized in {
            "review notes",
            "review_notes",
            "notes",
            "comment",
            "commentaire",
        }:
            column_map[column] = (
                "review_notes"
            )

        elif normalized in {
            "review at",
            "reviewed at",
            "reviewed_at",
            "date",
        }:
            column_map[column] = (
                "reviewed_at"
            )

        elif normalized in {
            "reviewer",
        }:
            column_map[column] = "reviewer"

    df = df.rename(
        columns=column_map
    ).copy()

    if "url" not in df.columns:
        raise ValueError(
            f"{annotator_name}: "
            "missing URL/Site column."
        )

    # Fill optional columns.
    for column in [
        "human_review_label",
        "score_100",
        "review_notes",
        "reviewed_at",
        "reviewer",
    ]:
        if column not in df.columns:
            df[column] = ""

    df["human_review_label"] = (
        df["human_review_label"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["url"] = (
        df["url"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["_match_key"] = df["url"].map(
        normalize_url
    )

    df["_match_domain"] = df["url"].map(
        lambda value: normalize_domain(
            normalize_url(value).split("/", 1)[0]
        )
        if normalize_url(value)
        else ""
    )

    # Keep the source rows unique enough for matching.
    duplicated = df[
        df["_match_key"].duplicated(
            keep=False
        )
        & df["_match_key"].ne("")
    ]

    if not duplicated.empty:
        raise ValueError(
            f"{annotator_name}: duplicate review URLs found:\n"
            + duplicated[
                ["url", "_match_key"]
            ].to_string(index=False)
        )

    # Store annotator-specific columns.
    prefix = annotator_name.lower()

    df = df.rename(
        columns={
            "url": f"{prefix}_url",
            "human_review_label": (
                f"{prefix}_label"
            ),
            "score_100": (
                f"{prefix}_score_100"
            ),
            "review_notes": (
                f"{prefix}_notes"
            ),
            "reviewed_at": (
                f"{prefix}_reviewed_at"
            ),
            "reviewer": (
                f"{prefix}_reviewer"
            ),
        }
    )

    return df


def make_base_site_table(
    first: pd.DataFrame,
    second: pd.DataFrame,
) -> pd.DataFrame:
    """Outer-join both annotator files."""

    left = first[
        [
            "_match_key",
            "_match_domain",
            "annotator1_url",
            "annotator1_label",
            "annotator1_score_100",
            "annotator1_notes",
            "annotator1_reviewed_at",
            "annotator1_reviewer",
        ]
    ].copy()

    right = second[
        [
            "_match_key",
            "_match_domain",
            "annotator2_url",
            "annotator2_label",
            "annotator2_score_100",
            "annotator2_notes",
            "annotator2_reviewed_at",
            "annotator2_reviewer",
        ]
    ].copy()

    # Exact normalized URL match first.
    merged = left.merge(
        right,
        on="_match_key",
        how="outer",
        suffixes=("", "_right"),
    )

    # Fill missing domains.
    merged["_match_domain"] = (
        merged["_match_domain"]
        .fillna(
            merged.get(
                "_match_domain_right",
                "",
            )
        )
    )

    # Guard against harmless homepage/domain spelling differences:
    # cabinet-3c.com vs cabinet3c.com,
    # accented domains, etc.
    unmatched_left = merged[
        merged["annotator1_url"].notna()
        & merged["annotator2_url"].isna()
    ].copy()

    unmatched_right = merged[
        merged["annotator1_url"].isna()
        & merged["annotator2_url"].notna()
    ].copy()

    if (
        not unmatched_left.empty
        and not unmatched_right.empty
    ):

        def compact_domain(domain: object) -> str:
            return re.sub(
                r"[^a-z0-9]",
                "",
                normalize_domain(domain),
            )

        left_lookup: dict[str, int] = {}

        for idx, row in unmatched_left.iterrows():
            key = compact_domain(
                row["_match_domain"]
            )
            if key:
                left_lookup[key] = idx

        consumed_right = set()

        for idx, row in unmatched_right.iterrows():

            key = compact_domain(
                row["_match_domain"]
            )

            if (
                key
                and key in left_lookup
                and left_lookup[key] in merged.index
            ):

                left_idx = left_lookup[key]

                for column in [
                    "annotator2_url",
                    "annotator2_label",
                    "annotator2_score_100",
                    "annotator2_notes",
                    "annotator2_reviewed_at",
                    "annotator2_reviewer",
                ]:
                    merged.loc[
                        left_idx,
                        column,
                    ] = row[column]

                consumed_right.add(
                    idx
                )

        # Rows matched manually by compact domain can now be removed
        # from their original standalone positions.
        if consumed_right:
            merged = merged.drop(
                index=list(
                    consumed_right
                ),
                errors="ignore",
            )

    return merged


def normalize_score(value: object):
    """Convert score to numeric when possible."""
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def derive_consensus(
    labels: list[str],
) -> tuple[
    str,
    float,
    bool,
]:
    """
    Derive a simple consensus from available human labels.

    For 2 annotators:
    - same label -> consensus_strength 1.0
    - different labels -> tie -> ABSTAIN, 0.5, ambiguous=True

    For >2 labels, majority is selected.
    Ties become ABSTAIN.
    """

    valid = [
        label
        for label in labels
        if label in VALID_LABELS
    ]

    if not valid:
        return (
            "ABSTAIN",
            0.0,
            True,
        )

    counts = {
        label: valid.count(label)
        for label in LABEL_ORDER
    }

    max_count = max(
        counts.values()
    )

    winners = [
        label
        for label, count
        in counts.items()
        if count == max_count
    ]

    strength = round(
        max_count
        / len(valid),
        4,
    )

    if len(winners) != 1:
        return (
            "ABSTAIN",
            strength,
            True,
        )

    return (
        winners[0],
        strength,
        False,
    )


def add_derived_fields(
    merged: pd.DataFrame,
) -> pd.DataFrame:
    """Add consensus and disagreement fields."""

    good_votes = []
    average_votes = []
    poor_votes = []
    annotator_count = []
    consensus_labels = []
    consensus_strengths = []
    ambiguous_flags = []
    score_means = []
    score_stds = []

    for _, row in merged.iterrows():

        labels = []

        for column in [
            "annotator1_label",
            "annotator2_label",
        ]:
            label = str(
                row.get(
                    column,
                    "",
                )
            ).strip().upper()

            if label in VALID_LABELS:
                labels.append(label)

        annotator_count.append(
            len(labels)
        )

        good_votes.append(
            labels.count("GOOD")
        )

        average_votes.append(
            labels.count("AVERAGE")
        )

        poor_votes.append(
            labels.count("POOR")
        )

        consensus, strength, ambiguous = (
            derive_consensus(labels)
        )

        consensus_labels.append(
            consensus
        )

        consensus_strengths.append(
            strength
        )

        ambiguous_flags.append(
            ambiguous
        )

        scores = []

        for column in [
            "annotator1_score_100",
            "annotator2_score_100",
        ]:
            score = normalize_score(
                row.get(column)
            )

            if score is not None:
                scores.append(score)

        if scores:
            score_means.append(
                round(
                    sum(scores)
                    / len(scores),
                    4,
                )
            )

            if len(scores) >= 2:
                mean = (
                    sum(scores)
                    / len(scores)
                )

                variance = (
                    sum(
                        (x - mean) ** 2
                        for x in scores
                    )
                    / len(scores)
                )

                score_stds.append(
                    round(
                        variance ** 0.5,
                        4,
                    )
                )

            else:
                score_stds.append(
                    0.0
                )

        else:
            score_means.append(
                None
            )

            score_stds.append(
                None
            )

    merged = merged.copy()

    merged[
        "annotator_count"
    ] = annotator_count

    merged[
        "good_votes"
    ] = good_votes

    merged[
        "average_votes"
    ] = average_votes

    merged[
        "poor_votes"
    ] = poor_votes

    merged[
        "consensus_label"
    ] = consensus_labels

    merged[
        "consensus_strength"
    ] = consensus_strengths

    merged[
        "human_disagreement"
    ] = ambiguous_flags

    merged[
        "score_mean"
    ] = score_means

    merged[
        "score_std"
    ] = score_stds

    # Site-level canonical URL.
    merged["url"] = (
        merged["annotator1_url"]
        .fillna("")
        .where(
            merged["annotator1_url"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne(""),
            merged["annotator2_url"],
        )
    )

    merged["domain"] = (
        merged["url"]
        .map(
            lambda value: (
                normalize_domain(
                    normalize_url(value).split(
                        "/",
                        1,
                    )[0]
                )
                if normalize_url(value)
                else ""
            )
        )
    )

    return merged


def main():
    first_path = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else DEFAULT_FIRST_REVIEW
    )

    second_path = Path(
        sys.argv[2]
        if len(sys.argv) > 2
        else DEFAULT_SECOND_REVIEW
    )

    output_path = Path(
        sys.argv[3]
        if len(sys.argv) > 3
        else DEFAULT_OUTPUT
    )

    print(
        "\n=== TRAFIQ AI — MERGE HUMAN REVIEWS V1 ==="
    )

    print(
        f"Annotator 1: {first_path}"
    )

    print(
        f"Annotator 2: {second_path}"
    )

    first_raw = read_review_file(
        first_path
    )

    second_raw = read_review_file(
        second_path
    )

    first = standardize_review_columns(
        first_raw,
        "Annotator1",
    )

    second = standardize_review_columns(
        second_raw,
        "Annotator2",
    )

    merged = make_base_site_table(
        first,
        second,
    )

    merged = add_derived_fields(
        merged
    )

    # Ensure deterministic order.
    merged = merged.sort_values(
        by="url",
        kind="stable",
    ).reset_index(
        drop=True
    )

    output_columns = [
        "url",
        "domain",

        "annotator_count",

        "annotator1_label",
        "annotator1_score_100",
        "annotator1_notes",
        "annotator1_reviewed_at",
        "annotator1_reviewer",

        "annotator2_label",
        "annotator2_score_100",
        "annotator2_notes",
        "annotator2_reviewed_at",
        "annotator2_reviewer",

        "good_votes",
        "average_votes",
        "poor_votes",

        "consensus_label",
        "consensus_strength",
        "human_disagreement",

        "score_mean",
        "score_std",
    ]

    merged[
        output_columns
    ].to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"\nRows merged: {len(merged)}"
    )

    print(
        "\n=== CONSENSUS DISTRIBUTION ==="
    )

    print(
        merged[
            "consensus_label"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print(
        "\n=== DISAGREEMENT ==="
    )

    print(
        merged[
            "human_disagreement"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\n=== OUTPUT ==="
    )

    print(
        output_path
    )

    print(
        "\nMerge completed successfully."
    )


if __name__ == "__main__":
    main()
