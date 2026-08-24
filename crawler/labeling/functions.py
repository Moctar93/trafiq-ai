from crawler.labeling import SEOClass
from crawler.schemas import SEOFeatures


def label_title(
    features: SEOFeatures,
) -> SEOClass:
    """
    Label the title using basic presence and length signals.

    Experimental rules:
    - Missing title -> POOR
    - Very short title -> POOR
    - Otherwise -> ABSTAIN

    We do not emit GOOD because the current feature set
    cannot measure relevance, uniqueness, or search intent.
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
    Label the meta description.

    Experimental rules:
    - Missing -> POOR
    - Very short -> AVERAGE
    - Very long -> AVERAGE
    - Otherwise -> ABSTAIN
    """

    if not features.meta_description_exists:
        return SEOClass.POOR

    length = features.meta_description_length

    if length < 70:
        return SEOClass.AVERAGE

    if length > 200:
        return SEOClass.AVERAGE

    return SEOClass.ABSTAIN


def label_headings(
    features: SEOFeatures,
) -> SEOClass:

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
    Label textual content using combined signals.

    Experimental rules:
    - Very low volume -> POOR
    - Very rich content with sufficient structure
      and acceptable diversity -> GOOD
    - Limited/intermediate content with weak structure -> AVERAGE
    - Otherwise -> ABSTAIN

    Word count is never used alone as proof of GOOD.
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
    Label image ALT coverage.

    Experimental rules:
    - No images -> ABSTAIN
    - Low ALT coverage -> POOR
    - High ALT coverage -> GOOD
    - Intermediate coverage -> AVERAGE
    """

    if features.image_count == 0:
        return SEOClass.ABSTAIN

    if features.alt_coverage_ratio is None:
        return SEOClass.ABSTAIN

    coverage = features.alt_coverage_ratio

    if coverage < 0.30:
        return SEOClass.POOR

    if coverage >= 0.90:
        return SEOClass.GOOD

    return SEOClass.AVERAGE


def label_links(
    features: SEOFeatures,
) -> SEOClass:
    """
    Label internal-link structure conservatively.

    V3.1 deliberately does not emit GOOD.

    - No internal links -> POOR
    - Weak internal-link structure -> AVERAGE
    - Otherwise -> ABSTAIN

    A strong internal-link ratio alone is not evidence
    of overall SEO quality.
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
