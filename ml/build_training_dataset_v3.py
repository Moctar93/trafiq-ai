from __future__ import annotations

from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_DATASET = BASE_DIR / "data" / "processed" / "seo_dataset_v4.csv"
HUMAN_REVIEWS = BASE_DIR / "data" / "reviewed" / "seo_human_review_merged_v3.csv"
OUTPUT_DATASET = BASE_DIR / "data" / "processed" / "seo_training_dataset_v3.csv"


TARGET_COLUMN = "consensus_label"


# Exact SEO feature set used by the V4 crawler.
# Crawl/provenance metadata are intentionally excluded from model features.
FEATURE_COLUMNS = [
    # Meta / structure
    "title_exists",
    "title_length",
    "title_word_count",
    "meta_description_exists",
    "meta_description_length",
    "meta_description_word_count",

    # Headings
    "h1_count",
    "h2_count",
    "h3_count",
    "h4_count",
    "h5_count",
    "h6_count",
    "heading_total_count",

    # Content
    "word_count",
    "character_count",
    "unique_word_count",
    "unique_word_ratio",

    # Images
    "image_count",
    "images_with_alt",
    "images_without_alt",
    "images_missing_alt_attribute",
    "empty_alt_count",
    "alt_coverage_ratio",

    # Links
    "total_link_count",
    "internal_link_count",
    "external_link_count",
    "nofollow_link_count",
    "sponsored_link_count",
    "ugc_link_count",
    "internal_link_ratio",

    # Technical SEO
    "canonical_exists",
    "robots_meta_exists",
    "viewport_exists",
    "lang_exists",
    "jsonld_count",
    "schema_org_count",

    # Business / UX
    "cta_count",
    "phone_count",
    "email_count",

    # External ecosystem
    "external_unique_domain_count",
]


VALID_LABELS = {"POOR", "AVERAGE", "GOOD"}


def normalize_url(value: object) -> str:
    """Normalize URLs enough for reliable matching."""
    if pd.isna(value):
        return ""

    url = str(value).strip().lower()

    if not url:
        return ""

    # Remove trailing slash, while preserving the scheme and path.
    return url.rstrip("/")


def validate_required_columns(
    df: pd.DataFrame,
    required: set[str],
    dataset_name: str,
) -> None:
    """Raise a clear error when required columns are missing."""
    missing = sorted(required - set(df.columns))

    if missing:
        raise ValueError(
            f"Colonnes manquantes dans {dataset_name} : "
            + ", ".join(missing)
        )


def main() -> None:
    print("=" * 70)
    print("BUILD TRAINING DATASET V3")
    print("=" * 70)

    if not SOURCE_DATASET.exists():
        raise FileNotFoundError(
            f"Dataset crawler introuvable : {SOURCE_DATASET}"
        )

    if not HUMAN_REVIEWS.exists():
        raise FileNotFoundError(
            f"Dataset humain introuvable : {HUMAN_REVIEWS}"
        )

    seo_df = pd.read_csv(SOURCE_DATASET)
    reviews_df = pd.read_csv(HUMAN_REVIEWS)

    print(f"\nDataset crawler : {len(seo_df)} lignes")
    print(f"Reviews humaines : {len(reviews_df)} lignes")

    # Validate source structure.
    validate_required_columns(
        seo_df,
        {"url", "crawl_quality"},
        "seo_dataset_v4.csv",
    )

    validate_required_columns(
        reviews_df,
        {
            "url",
            "consensus_label",
            "consensus_strength",
            "human_disagreement",
            "annotator_count",
            "good_votes",
            "average_votes",
            "poor_votes",
        },
        "seo_human_review_merged_v3.csv",
    )

    # Verify that the crawler contains exactly the expected SEO features.
    missing_features = [
        feature for feature in FEATURE_COLUMNS
        if feature not in seo_df.columns
    ]

    if missing_features:
        raise ValueError(
            "Features SEO manquantes dans le dataset crawler : "
            + ", ".join(missing_features)
        )

    print(f"Features SEO V4 disponibles : {len(FEATURE_COLUMNS)}")

    # Normalize URLs for matching.
    seo_df["_match_url"] = seo_df["url"].map(normalize_url)
    reviews_df["_match_url"] = reviews_df["url"].map(normalize_url)

    # Detect empty URLs.
    if (seo_df["_match_url"] == "").any():
        bad_count = int((seo_df["_match_url"] == "").sum())
        raise ValueError(
            f"{bad_count} URL(s) vide(s) dans le dataset crawler."
        )

    if (reviews_df["_match_url"] == "").any():
        bad_count = int((reviews_df["_match_url"] == "").sum())
        raise ValueError(
            f"{bad_count} URL(s) vide(s) dans les reviews humaines."
        )

    # Duplicate checks.
    duplicated_reviews = reviews_df[
        reviews_df["_match_url"].duplicated(keep=False)
    ]

    if not duplicated_reviews.empty:
        duplicate_urls = sorted(
            duplicated_reviews["_match_url"].unique().tolist()
        )

        raise ValueError(
            "Des URLs dupliquées ont été trouvées dans les reviews humaines : "
            + ", ".join(duplicate_urls)
        )

    duplicated_crawler = seo_df[
        seo_df["_match_url"].duplicated(keep=False)
    ]

    if not duplicated_crawler.empty:
        duplicate_urls = sorted(
            duplicated_crawler["_match_url"].unique().tolist()
        )

        raise ValueError(
            "Des URLs dupliquées ont été trouvées dans le dataset crawler : "
            + ", ".join(duplicate_urls)
        )

    # Validate consensus labels.
    invalid_labels = set(
        reviews_df["consensus_label"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
    ) - VALID_LABELS

    if invalid_labels:
        raise ValueError(
            "Labels humains invalides détectés : "
            + ", ".join(sorted(invalid_labels))
        )

    reviews_df["consensus_label"] = (
        reviews_df["consensus_label"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    reviews_df = reviews_df[
        reviews_df["consensus_label"].isin(VALID_LABELS)
    ].copy()

    # Keep only the review columns needed for the training dataset.
    review_columns = [
        "_match_url",
        "consensus_label",
        "consensus_strength",
        "human_disagreement",
        "annotator_count",
        "good_votes",
        "average_votes",
        "poor_votes",
    ]

    merged = seo_df.merge(
        reviews_df[review_columns],
        on="_match_url",
        how="left",
        validate="one_to_one",
    )

    matched_reviews = int(merged["consensus_label"].notna().sum())
    unmatched_reviews = int(
        (~reviews_df["_match_url"].isin(seo_df["_match_url"])).sum()
    )

    print(f"Reviews humaines matchées : {matched_reviews}")
    print(f"Reviews humaines non matchées : {unmatched_reviews}")

    if unmatched_reviews:
        missing_review_urls = sorted(
            reviews_df.loc[
                ~reviews_df["_match_url"].isin(seo_df["_match_url"]),
                "url",
            ].tolist()
        )

        print("\nURLs de reviews non retrouvées dans le crawler :")
        for url in missing_review_urls:
            print(f"  - {url}")

    # Keep only human-reviewed pages.
    training_df = merged[
        merged["consensus_label"].notna()
    ].copy()

    print(
        f"\nPages avec consensus humain avant filtre qualité : "
        f"{len(training_df)}"
    )

    # Do not train on bad/incomplete crawl observations.
    before_quality_filter = len(training_df)

    training_df = training_df[
        training_df["crawl_quality"]
        .fillna("")
        .astype(str)
        .str.upper()
        .eq("NORMAL")
    ].copy()

    print(
        f"Filtre crawl_quality=NORMAL : "
        f"{before_quality_filter} -> {len(training_df)}"
    )

    if training_df.empty:
        raise ValueError(
            "Aucune donnée d'entraînement après le filtre crawl_quality=NORMAL."
        )

    # Final feature validation on the actual training rows.
    missing_training_features = [
        feature for feature in FEATURE_COLUMNS
        if feature not in training_df.columns
    ]

    if missing_training_features:
        raise ValueError(
            "Features SEO manquantes dans le dataset final : "
            + ", ".join(missing_training_features)
        )

    # Preserve metadata useful for auditability, but not as ML features.
    metadata_columns = [
        col
        for col in [
            "url",
            "domain",
            "crawl_quality",
            "crawl_id",
            "crawl_timestamp",
            "content_hash",
            "consensus_label",
            "consensus_strength",
            "human_disagreement",
            "annotator_count",
            "good_votes",
            "average_votes",
            "poor_votes",
        ]
        if col in training_df.columns
    ]

    final_columns = metadata_columns + FEATURE_COLUMNS

    training_df = training_df[final_columns].copy()

    # Sanity checks.
    if TARGET_COLUMN not in training_df.columns:
        raise ValueError(
            f"La cible '{TARGET_COLUMN}' est absente du dataset final."
        )

    actual_feature_count = len(FEATURE_COLUMNS)

    if actual_feature_count != 40:
        raise RuntimeError(
            f"Configuration inattendue : {actual_feature_count} features "
            "déclarées au lieu de 40."
        )

    print(f"\nNombre de lignes training : {len(training_df)}")
    print(f"Nombre de features SEO : {actual_feature_count}")

    print("\nDistribution des labels :")
    print(training_df[TARGET_COLUMN].value_counts())

    print("\nForce du consensus :")
    print(
        training_df["consensus_strength"]
        .value_counts()
        .sort_index()
    )

    print("\nDésaccord humain :")
    print(
        training_df["human_disagreement"]
        .value_counts()
    )

    # Check expected majority/consensus strength values for 3 annotators.
    invalid_strengths = sorted(
        set(
            pd.to_numeric(
                training_df["consensus_strength"],
                errors="coerce",
            )
            .dropna()
            .round(6)
            .tolist()
        )
        - {0.666667, 1.0}
    )

    if invalid_strengths:
        print(
            "\nAVERTISSEMENT : valeurs de consensus_strength "
            f"inhabituelles : {invalid_strengths}"
        )

    # Save.
    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    training_df.to_csv(
        OUTPUT_DATASET,
        index=False,
        encoding="utf-8",
    )

    print("\nDataset créé :")
    print(OUTPUT_DATASET)

    print("\nColonnes ML :")
    for index, feature in enumerate(FEATURE_COLUMNS, start=1):
        print(f"  {index:02d}. {feature}")

    print("\nPremières lignes :")
    print(training_df.head().to_string(index=False))

    print("\n" + "=" * 70)
    print("BUILD TERMINÉ")
    print("=" * 70)


if __name__ == "__main__":
    main()