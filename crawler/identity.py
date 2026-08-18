from datetime import datetime, timezone
import hashlib
from urllib.parse import urlsplit, urlunsplit
import uuid


def normalize_url(url: str) -> str:
    """
    Normalize a URL before generating a stable page identifier.

    The normalization:
    - removes fragments
    - lowercases scheme and hostname
    - removes a trailing slash from non-root paths
    """

    parsed = urlsplit(url.strip())

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower() if parsed.hostname else ""

    netloc = hostname

    if parsed.port:
        default_port = (
            (scheme == "http" and parsed.port == 80)
            or (scheme == "https" and parsed.port == 443)
        )

        if not default_port:
            netloc = f"{hostname}:{parsed.port}"

    path = parsed.path or "/"

    if path != "/":
        path = path.rstrip("/")

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            "",
        )
    )


def generate_page_id(url: str) -> str:
    """
    Generate a stable identifier for the logical webpage.
    """

    normalized_url = normalize_url(url)

    return hashlib.sha256(
        normalized_url.encode("utf-8")
    ).hexdigest()[:16]


def generate_content_hash(content: str) -> str:
    """
    Generate a hash representing the exact crawled HTML content.
    """

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def generate_crawl_id() -> str:
    """
    Generate a unique identifier for a crawl execution.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S")

    unique_id = uuid.uuid4().hex[:8]

    return f"crawl_{timestamp}_{unique_id}"


def generate_crawl_timestamp() -> str:
    """
    Return the current UTC timestamp in ISO 8601 format.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()