"""Feature configuration for TRAFIQ AI ML baselines."""

TARGET_COLUMN = "human_review_label"

EXCLUDED_COLUMNS = {
    TARGET_COLUMN,
    "weak_label",
    "weak_confidence",
    "weak_vote_count",
    "weak_ambiguous",
    "weak_training_eligible",
    "crawl_id",
    "page_id",
    "crawl_timestamp",
    "content_hash",
    "url",
    "domain",
    "calibration_group",
    "crawl_quality",
    "status_code",
    "html_size_bytes",
    "response_time_ms",
    "redirect_count",
    "review_notes",
    "reviewed_at",
    "reviewer",
    "score_100",
}

CANDIDATE_FEATURES = [
    "title_exists",
    "title_length",
    "title_word_count",
    "meta_description_exists",
    "meta_description_length",
    "meta_description_word_count",
    "h1_count",
    "h2_count",
    "h3_count",
    "h4_count",
    "h5_count",
    "h6_count",
    "heading_total_count",
    "word_count",
    "character_count",
    "unique_word_count",
    "unique_word_ratio",
    "image_count",
    "images_with_alt",
    "images_without_alt",
    "images_missing_alt_attribute",
    "empty_alt_count",
    "alt_coverage_ratio",
    "total_link_count",
    "internal_link_count",
    "external_link_count",
    "nofollow_link_count",
    "sponsored_link_count",
    "ugc_link_count",
    "internal_link_ratio",
]

BOOLEAN_FEATURES = {
    "title_exists",
    "meta_description_exists",
}

LABELS = [
    "POOR",
    "AVERAGE",
    "GOOD",
]


def get_feature_columns(columns):
    """Return configured feature columns present in the dataset."""

    return [
        column
        for column in CANDIDATE_FEATURES
        if column in columns
    ]