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

        # Headings
    calculated_heading_total = (
        features.h1_count
        + features.h2_count
        + features.h3_count
        + features.h4_count
        + features.h5_count
        + features.h6_count
    )

    if (
        features.heading_total_count
        != calculated_heading_total
    ):
        errors.append(
            "heading_total_count must equal "
            "the sum of h1_count through h6_count."
        )

    # Images
    calculated_image_total = (
        features.images_with_alt
        + features.images_without_alt
    )

    if (
        calculated_image_total
        != features.image_count
    ):
        errors.append(
            "images_with_alt + "
            "images_without_alt must equal "
            "image_count."
        )

    if (
        features.images_missing_alt_attribute
        > features.images_without_alt
    ):
        errors.append(
            "images_missing_alt_attribute "
            "cannot be greater than "
            "images_without_alt."
        )

    if (
        features.empty_alt_count
        > features.images_without_alt
    ):
        errors.append(
            "empty_alt_count cannot be greater "
            "than images_without_alt."
        )
    return errors