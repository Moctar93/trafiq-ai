from crawler.schemas import SEOFeatures
from crawler.labeling import SEOClass


def label_title(features: SEOFeatures) -> SEOClass:
    """
    Evaluate the basic presence and characteristics of the page title.

    The current feature set cannot determine whether a title is truly
    descriptive, unique, relevant, or well-written.

    Rules:
    - missing title -> POOR
    - extremely short title -> POOR
    - very long title -> AVERAGE
    - otherwise -> AVERAGE

    Title length alone is not considered sufficient to produce GOOD.
    """

    if not features.title_exists:
        return SEOClass.POOR

    if features.title_length < 10:
        return SEOClass.POOR

    if features.title_length > 200:
        return SEOClass.AVERAGE

    return SEOClass.AVERAGE


def label_meta_description(features: SEOFeatures) -> SEOClass:
    """
    Evaluate the presence of a meta description.

    The current feature set does not allow us to determine whether
    a meta description is relevant, unique, descriptive, or useful.

    Rules:
    - missing meta description -> POOR
    - existing meta description -> AVERAGE

    Length alone is intentionally not sufficient to produce GOOD.
    """

    if not features.meta_description_exists:
        return SEOClass.POOR

    return SEOClass.AVERAGE


def label_headings(features: SEOFeatures) -> SEOClass:
    """
    Evaluate the basic heading structure of the page.

    The current features provide heading counts but do not tell us
    whether the headings are semantically meaningful or well organized.

    Rules:
    - no H1 -> POOR
    - one or more H1 -> AVERAGE

    The function does not produce GOOD from heading counts alone.
    """

    if features.h1_count == 0:
        return SEOClass.POOR

    return SEOClass.AVERAGE


def label_content(features: SEOFeatures) -> SEOClass:
    """
    Evaluate the amount of textual content available on the page.

    Word count alone cannot determine:
    - content quality
    - relevance
    - originality
    - usefulness
    - search intent satisfaction

    Therefore:
    - extremely low content -> POOR
    - otherwise -> AVERAGE

    No GOOD label is produced from word count alone.
    """

    if features.word_count < 20:
        return SEOClass.POOR

    return SEOClass.AVERAGE


def label_images(features: SEOFeatures) -> SEOClass:
    """
    Evaluate basic image and alt-attribute signals.

    The absence of images is not inherently an SEO problem.

    Rules:
    - no images -> ABSTAIN
    - all images without usable alt attributes -> POOR
    - some images without usable alt attributes -> AVERAGE
    - all images have usable alt attributes -> AVERAGE

    Empty alt attributes can be intentional for decorative images,
    so they are not automatically considered errors.
    """

    if features.image_count == 0:
        return SEOClass.ABSTAIN

    if features.images_without_alt >= features.image_count:
        return SEOClass.POOR

    if features.images_without_alt > 0:
        return SEOClass.AVERAGE

    return SEOClass.AVERAGE


def label_links(features: SEOFeatures) -> SEOClass:
    """
    Evaluate the basic internal-linking signal.

    Internal link count alone cannot determine whether the site's
    linking architecture is good.

    Rules:
    - no internal links -> POOR
    - internal links exist -> AVERAGE

    GOOD is intentionally not produced from link count alone.
    """

    if features.internal_link_count == 0:
        return SEOClass.POOR

    return SEOClass.AVERAGE


def run_all_labeling_functions(
    features: SEOFeatures,
) -> dict[str, SEOClass]:
    """
    Run all Trafiq AI labeling functions.

    Returns the individual votes without performing aggregation.
    """

    return {
        "TITLE": label_title(features),
        "META": label_meta_description(features),
        "HEADINGS": label_headings(features),
        "CONTENT": label_content(features),
        "IMAGES": label_images(features),
        "LINKS": label_links(features),
    }