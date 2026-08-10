from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


class HTMLExtractor:
    """Extract SEO-related features from an HTML document."""

    def __init__(self, html: str, base_url: str):
        self.html = html
        self.base_url = base_url

        self.soup = BeautifulSoup(
            html,
            "html.parser",
        )

        self.base_domain = urlparse(base_url).netloc.lower()

    def extract_title(self) -> dict:
        title = self.soup.find("title")

        if not title:
            return {
                "title_exists": False,
                "title_length": 0,
                "title_word_count": 0,
            }

        text = title.get_text(" ", strip=True)

        return {
            "title_exists": True,
            "title_length": len(text),
            "title_word_count": len(text.split()),
        }

    def extract_meta_description(self) -> dict:
        meta = self.soup.find(
            "meta",
            attrs={
                "name": lambda value: (
                    value and value.lower() == "description"
                )
            },
        )

        if not meta:
            return {
                "meta_description_exists": False,
                "meta_description_length": 0,
                "meta_description_word_count": 0,
            }

        content = meta.get("content", "").strip()

        return {
            "meta_description_exists": True,
            "meta_description_length": len(content),
            "meta_description_word_count": len(content.split()),
        }

    def extract_headings(self) -> dict:
        return {
            "h1_count": len(self.soup.find_all("h1")),
            "h2_count": len(self.soup.find_all("h2")),
            "h3_count": len(self.soup.find_all("h3")),
            "h4_count": len(self.soup.find_all("h4")),
            "h5_count": len(self.soup.find_all("h5")),
            "h6_count": len(self.soup.find_all("h6")),
        }

    def extract_content(self) -> dict:
        # Remove elements that should not be considered
        # visible textual content.
        for element in self.soup.find_all(
            ["script", "style", "noscript", "svg"]
        ):
            element.decompose()

        text = self.soup.get_text(
            separator=" ",
            strip=True,
        )

        words = text.split()

        unique_words = set(
            word.lower()
            for word in words
        )

        return {
            "word_count": len(words),
            "character_count": len(text),
            "unique_word_count": len(unique_words),
            "unique_word_ratio": (
                len(unique_words) / len(words)
                if words
                else None
            ),
        }

    def extract_images(self) -> dict:
        images = self.soup.find_all("img")

        images_with_alt = 0
        images_without_alt = 0
        empty_alt_count = 0

        for image in images:
            if not image.has_attr("alt"):
                images_without_alt += 1
                continue

            alt = image.get("alt", "").strip()

            if alt:
                images_with_alt += 1
            else:
                empty_alt_count += 1

        return {
            "image_count": len(images),
            "images_with_alt": images_with_alt,
            "images_without_alt": images_without_alt,
            "empty_alt_count": empty_alt_count,
        }

    def extract_links(self) -> dict:
        links = self.soup.find_all("a", href=True)

        internal_links = 0
        external_links = 0
        nofollow_links = 0
        sponsored_links = 0
        ugc_links = 0

        for link in links:
            href = link.get("href", "").strip()

            if not href:
                continue

            absolute_url = urljoin(
                self.base_url,
                href,
            )

            parsed_url = urlparse(absolute_url)

            domain = parsed_url.netloc.lower()

            if domain == self.base_domain:
                internal_links += 1
            elif domain:
                external_links += 1

            rel = link.get("rel", [])

            if isinstance(rel, str):
                rel = rel.split()

            rel = [value.lower() for value in rel]

            if "nofollow" in rel:
                nofollow_links += 1

            if "sponsored" in rel:
                sponsored_links += 1

            if "ugc" in rel:
                ugc_links += 1

        return {
            "total_link_count": len(links),
            "internal_link_count": internal_links,
            "external_link_count": external_links,
            "nofollow_link_count": nofollow_links,
            "sponsored_link_count": sponsored_links,
            "ugc_link_count": ugc_links,
        }

    def extract_all(self) -> dict:
        """Run all extraction methods."""

        features = {}

        features.update(self.extract_title())
        features.update(self.extract_meta_description())
        features.update(self.extract_headings())
        features.update(self.extract_content())
        features.update(self.extract_images())
        features.update(self.extract_links())

        return features