from enum import Enum

from pydantic import BaseModel, Field


class HumanReviewLabel(str, Enum):
    """Human-reviewed SEO quality label."""

    GOOD = "GOOD"
    AVERAGE = "AVERAGE"
    POOR = "POOR"


class HumanReview(BaseModel):
    """Human review record for one SEO observation."""

    page_id: str
    url: str
    domain: str

    calibration_group: str = "unknown"
    crawl_quality: str = "NORMAL"

    human_review_label: HumanReviewLabel

    review_notes: str = ""

    reviewed_at: str = ""

    reviewer: str = Field(
        default="human",
    )