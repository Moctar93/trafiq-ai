from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CrawlResult(BaseModel):
    url: str
    domain: str
    crawl_timestamp: datetime

    http_status_code: int
    response_time_ms: Optional[float] = None
    content_type: Optional[str] = None
    html_size_bytes: Optional[int] = None
    redirect_count: int = 0

    https_enabled: bool

    robots_txt_exists: Optional[bool] = None
    sitemap_exists: Optional[bool] = None

    title_exists: bool
    title_length: int

    meta_description_exists: bool
    meta_description_length: int

    h1_count: int
    h2_count: int
    h3_count: int

    word_count: int

    image_count: int
    images_with_alt: int
    images_without_alt: int

    total_link_count: int
    internal_link_count: int
    external_link_count: int