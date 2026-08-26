from crawler.labeling import SEOClass
from crawler.schemas import SEOFeatures


def label_title(
    features: SEOFeatures,
) -> SEOClass:
    """
    Evaluate title quality as a negative signal.

    TITLE never produces GOOD.
    """

    if not features.title_exists:
        return SEOClass.POOR

    if features.title_length < 20:
        return SEOClass.POOR

    return SEOClass.ABSTAIN


def label_meta_description(
    features: SEOFeatures,
) -> SEOClass:
    """
    Evaluate meta-description quality.

    META never produces GOOD.
    """

    if not features.meta_description_exists:
        return SEOClass.POOR

    length = features.meta_description_length

    if length < 70:
        return SEOClass.POOR

    if length > 200:
        return SEOClass.AVERAGE

    return SEOClass.ABSTAIN


def label_headings(
    features: SEOFeatures,
) -> SEOClass:
    """
    Evaluate heading structure conservatively.

    HEADINGS never produces GOOD.
    """

    if features.h1_count == 0:
        return SEOClass.POOR

    if features.h1_count > 1:
        return SEOClass.AVERAGE

    if features.heading_total_count <= 2:
        return SEOClass.POOR

    return SEOClass.ABSTAIN


def label_content(
    features: SEOFeatures,
) -> SEOClass:
    """
    Evaluate content depth.

    Content is one of the few dimensions allowed
    to provide a positive signal.
    """

    word_count = features.word_count
    heading_count = features.heading_total_count
    diversity = features.unique_word_ratio

    if word_count < 300:
        return SEOClass.POOR

    if (
        word_count >= 3000
        and heading_count >= 40
        and diversity is not None
        and diversity >= 0.35
    ):
        return SEOClass.GOOD

    if (
        300 <= word_count < 600
        and heading_count < 10
    ):
        return SEOClass.AVERAGE

    return SEOClass.ABSTAIN


def label_images(
    features: SEOFeatures,
) -> SEOClass:
    """
    Evaluate image ALT coverage only.

    A good image score is intentionally not emitted
    as GOOD because image optimization alone is not
    sufficient to establish overall SEO quality.
    """

    if features.image_count == 0:
        return SEOClass.ABSTAIN

    if features.alt_coverage_ratio is None:
        return SEOClass.ABSTAIN

    coverage = features.alt_coverage_ratio

    if coverage < 0.30:
        return SEOClass.POOR

    if coverage < 0.70:
        return SEOClass.AVERAGE

    return SEOClass.ABSTAIN


def label_links(
    features: SEOFeatures,
) -> SEOClass:
    """
    Evaluate internal-link structure conservatively.

    LINKS never produces GOOD.
    """

    if features.internal_link_count == 0:
        return SEOClass.POOR

    if (
        features.internal_link_ratio is not None
        and features.internal_link_ratio < 0.60
    ):
        return SEOClass.AVERAGE

    if features.internal_link_count < 5:
        return SEOClass.AVERAGE

    return SEOClass.ABSTAIN


def run_all_labeling_functions(
    features: SEOFeatures,
) -> dict[str, SEOClass]:
    """
    Run all SEO labeling functions.
    """

    return {
        "TITLE": label_title(features),
        "META": label_meta_description(features),
        "HEADINGS": label_headings(features),
        "CONTENT": label_content(features),
        "IMAGES": label_images(features),
        "LINKS": label_links(features),
    }