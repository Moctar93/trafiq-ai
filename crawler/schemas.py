from typing import Optional

from pydantic import BaseModel, Field


class SEOFeatures(BaseModel):
    """Validated SEO features extracted from a webpage."""

    title_exists: bool
    title_length: int = Field(ge=0)
    title_word_count: int = Field(ge=0)

    meta_description_exists: bool
    meta_description_length: int = Field(ge=0)
    meta_description_word_count: int = Field(ge=0)

    h1_count: int = Field(ge=0)
    h2_count: int = Field(ge=0)
    h3_count: int = Field(ge=0)
    h4_count: int = Field(ge=0)
    h5_count: int = Field(ge=0)
    h6_count: int = Field(ge=0)

    word_count: int = Field(ge=0)
    character_count: int = Field(ge=0)
    unique_word_count: int = Field(ge=0)

    unique_word_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )

    image_count: int = Field(ge=0)
    images_with_alt: int = Field(ge=0)
    images_without_alt: int = Field(ge=0)
    empty_alt_count: int = Field(ge=0)

    total_link_count: int = Field(ge=0)
    internal_link_count: int = Field(ge=0)
    external_link_count: int = Field(ge=0)
    nofollow_link_count: int = Field(ge=0)
    sponsored_link_count: int = Field(ge=0)
    ugc_link_count: int = Field(ge=0)