"""Feature configuration for TRAFIQ AI ML baselines."""

TARGET_COLUMN = "human_review_label"


EXCLUDED_COLUMNS = {
    # ==============================================
    # HUMAN TARGET
    # ==============================================

    TARGET_COLUMN,

    # ==============================================
    # WEAK LABELS
    # ==============================================

    "weak_label",
    "weak_confidence",
    "weak_vote_count",
    "weak_ambiguous",
    "weak_training_eligible",

    # ==============================================
    # IDENTIFIERS / PROVENANCE
    # ==============================================

    "crawl_id",
    "page_id",
    "crawl_timestamp",
    "content_hash",
    "url",
    "domain",
    "calibration_group",

    # ==============================================
    # CRAWL METADATA
    # ==============================================

    "crawl_quality",
    "status_code",
    "html_size_bytes",
    "response_time_ms",
    "redirect_count",

    # ==============================================
    # HUMAN REVIEW METADATA
    # ==============================================

    "review_notes",
    "reviewed_at",
    "reviewer",
    "score_100",
}


# ==================================================
# SEO FEATURES V1 + V4
# ==================================================

CANDIDATE_FEATURES = [
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

    # Business / UX signals
    "cta_count",
    "phone_count",
    "email_count",

    # Authority / external ecosystem
    "external_unique_domain_count",
]


BOOLEAN_FEATURES = {
    "title_exists",
    "meta_description_exists",
    "canonical_exists",
    "robots_meta_exists",
    "viewport_exists",
    "lang_exists",
}


OPTIONAL_NUMERIC_FEATURES = {
    "unique_word_ratio",
    "alt_coverage_ratio",
    "internal_link_ratio",
}


LABELS = [
    "POOR",
    "AVERAGE",
    "GOOD",
]


def get_feature_columns(columns):
    """
    Return the configured feature columns
    that are actually present in the dataset.
    """

    return [
        column
        for column in CANDIDATE_FEATURES
        if column in columns
    ]