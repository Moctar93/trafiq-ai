from typing import Optional

from pydantic import BaseModel, Field


class SEOFeatures(BaseModel):
    """Validated SEO features extracted from one HTML page."""

    # ==================================================
    # TITLE
    # ==================================================

    title_exists: bool
    title_length: int = Field(ge=0)
    title_word_count: int = Field(ge=0)

    # ==================================================
    # META DESCRIPTION
    # ==================================================

    meta_description_exists: bool
    meta_description_length: int = Field(ge=0)
    meta_description_word_count: int = Field(ge=0)

    # ==================================================
    # HEADINGS
    # ==================================================

    h1_count: int = Field(ge=0)
    h2_count: int = Field(ge=0)
    h3_count: int = Field(ge=0)
    h4_count: int = Field(ge=0)
    h5_count: int = Field(ge=0)
    h6_count: int = Field(ge=0)

    heading_total_count: int = Field(ge=0)

    # ==================================================
    # CONTENT
    # ==================================================

    word_count: int = Field(ge=0)
    character_count: int = Field(ge=0)
    unique_word_count: int = Field(ge=0)

    unique_word_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )

    # ==================================================
    # IMAGES
    # ==================================================

    image_count: int = Field(ge=0)
    images_with_alt: int = Field(ge=0)
    images_without_alt: int = Field(ge=0)
    images_missing_alt_attribute: int = Field(
        ge=0
    )
    empty_alt_count: int = Field(ge=0)

    alt_coverage_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )

    # ==================================================
    # LINKS
    # ==================================================

    total_link_count: int = Field(ge=0)
    internal_link_count: int = Field(ge=0)
    external_link_count: int = Field(ge=0)
    nofollow_link_count: int = Field(ge=0)
    sponsored_link_count: int = Field(ge=0)
    ugc_link_count: int = Field(ge=0)

    internal_link_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )

    # ==================================================
    # V4 — TECHNICAL
    # ==================================================

    canonical_exists: bool

    robots_meta_exists: bool

    viewport_exists: bool

    lang_exists: bool

    # ==================================================
    # V4 — STRUCTURED DATA
    # ==================================================

    jsonld_count: int = Field(ge=0)

    schema_org_count: int = Field(ge=0)

    # ==================================================
    # V4 — BUSINESS / CONVERSION SIGNALS
    # ==================================================

    cta_count: int = Field(ge=0)

    phone_count: int = Field(ge=0)

    email_count: int = Field(ge=0)

    # ==================================================
    # V4 — EXTERNAL LINK DIVERSITY
    # ==================================================

    external_unique_domain_count: int = Field(
        ge=0
    )