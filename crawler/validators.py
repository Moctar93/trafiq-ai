from crawler.schemas import SEOFeatures


def validate_seo_features(features: SEOFeatures) -> list[str]:
    """
    Validate logical relationships between SEO features.

    Returns:
        A list of validation errors.
        An empty list means the observation is valid.
    """

    errors = []

    # Images
    if (
        features.images_with_alt
        + features.images_without_alt
        > features.image_count
    ):
        errors.append(
            "images_with_alt + images_without_alt "
            "cannot be greater than image_count."
        )

    if features.images_with_alt > features.image_count:
        errors.append(
            "images_with_alt cannot be greater than image_count."
        )

    if features.images_without_alt > features.image_count:
        errors.append(
            "images_without_alt cannot be greater than image_count."
        )

    # Links
    if (
        features.internal_link_count
        + features.external_link_count
        > features.total_link_count
    ):
        errors.append(
            "internal_link_count + external_link_count "
            "cannot be greater than total_link_count."
        )

    # Content
    if features.unique_word_count > features.word_count:
        errors.append(
            "unique_word_count cannot be greater than word_count."
        )

    # Ratio
    if (
        features.unique_word_ratio is not None
        and features.word_count == 0
    ):
        errors.append(
            "unique_word_ratio must be None when word_count is 0."
        )

    return errors