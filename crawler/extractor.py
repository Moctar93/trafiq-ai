import re

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


class HTMLExtractor:
    """Extract SEO-related features from an HTML document."""

    def __init__(
        self,
        html: str,
        base_url: str,
    ):
        self.html = html
        self.base_url = base_url

        self.soup = BeautifulSoup(
            html,
            "html.parser",
        )

        self.base_domain = (
            urlparse(
                base_url
            )
            .netloc
            .lower()
        )

    # ==================================================
    # TITLE
    # ==================================================

    def extract_title(self) -> dict:
        title = self.soup.find(
            "title"
        )

        if not title:
            return {
                "title_exists": False,
                "title_length": 0,
                "title_word_count": 0,
            }

        text = title.get_text(
            " ",
            strip=True,
        )

        return {
            "title_exists": True,
            "title_length": len(text),
            "title_word_count": len(
                text.split()
            ),
        }

    # ==================================================
    # META DESCRIPTION
    # ==================================================

    def extract_meta_description(
        self,
    ) -> dict:

        meta = self.soup.find(
            "meta",
            attrs={
                "name": lambda value: (
                    value
                    and value.lower()
                    == "description"
                )
            },
        )

        if not meta:
            return {
                "meta_description_exists": False,
                "meta_description_length": 0,
                "meta_description_word_count": 0,
            }

        content = meta.get(
            "content",
            "",
        ).strip()

        return {
            "meta_description_exists": True,
            "meta_description_length": len(
                content
            ),
            "meta_description_word_count": len(
                content.split()
            ),
        }

    # ==================================================
    # HEADINGS
    # ==================================================

    def extract_headings(self) -> dict:

        h1_count = len(
            self.soup.find_all("h1")
        )

        h2_count = len(
            self.soup.find_all("h2")
        )

        h3_count = len(
            self.soup.find_all("h3")
        )

        h4_count = len(
            self.soup.find_all("h4")
        )

        h5_count = len(
            self.soup.find_all("h5")
        )

        h6_count = len(
            self.soup.find_all("h6")
        )

        return {
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "h4_count": h4_count,
            "h5_count": h5_count,
            "h6_count": h6_count,
            "heading_total_count": (
                h1_count
                + h2_count
                + h3_count
                + h4_count
                + h5_count
                + h6_count
            ),
        }

    # ==================================================
    # CONTENT
    # ==================================================

    def extract_content(self) -> dict:
        # Remove elements that should not count
        # as visible textual content.

        for element in self.soup.find_all(
            [
                "script",
                "style",
                "noscript",
                "svg",
            ]
        ):
            element.decompose()

        text = self.soup.get_text(
            separator=" ",
            strip=True,
        )

        words = text.split()

        unique_words = {
            word.lower()
            for word in words
        }

        return {
            "word_count": len(words),
            "character_count": len(text),
            "unique_word_count": len(
                unique_words
            ),
            "unique_word_ratio": (
                len(unique_words)
                / len(words)
                if words
                else None
            ),
        }

    # ==================================================
    # IMAGES
    # ==================================================

    def extract_images(self) -> dict:

        images = self.soup.find_all(
            "img"
        )

        images_with_alt = 0
        images_without_alt = 0
        empty_alt_count = 0

        for image in images:

            if not image.has_attr(
                "alt"
            ):
                images_without_alt += 1
                continue

            alt = image.get(
                "alt",
                "",
            ).strip()

            if alt:
                images_with_alt += 1
            else:
                empty_alt_count += 1

        image_count = len(images)

        alt_coverage_ratio = (
            images_with_alt / image_count
            if image_count
            else None
        )

        return {
            "image_count": image_count,
            "images_with_alt": images_with_alt,
            "images_without_alt": images_without_alt,
            "images_missing_alt_attribute": (
                images_without_alt
            ),
            "empty_alt_count": empty_alt_count,
            "alt_coverage_ratio": (
                alt_coverage_ratio
            ),
        }

    # ==================================================
    # LINKS
    # ==================================================

    def extract_links(self) -> dict:

        links = self.soup.find_all(
            "a",
            href=True,
        )

        internal_links = 0
        external_links = 0

        nofollow_links = 0
        sponsored_links = 0
        ugc_links = 0

        external_domains = set()

        for link in links:

            href = link.get(
                "href",
                "",
            ).strip()

            if not href:
                continue

            absolute_url = urljoin(
                self.base_url,
                href,
            )

            parsed_url = urlparse(
                absolute_url
            )

            domain = (
                parsed_url.netloc
                .lower()
            )

            if (
                domain
                == self.base_domain
            ):
                internal_links += 1

            elif domain:
                external_links += 1

                external_domains.add(
                    domain
                )

            rel = link.get(
                "rel",
                [],
            )

            if isinstance(
                rel,
                str,
            ):
                rel = rel.split()

            rel = [
                value.lower()
                for value in rel
            ]

            if "nofollow" in rel:
                nofollow_links += 1

            if "sponsored" in rel:
                sponsored_links += 1

            if "ugc" in rel:
                ugc_links += 1

        total_link_count = len(
            links
        )

        internal_link_ratio = (
            internal_links
            / total_link_count
            if total_link_count
            else None
        )

        return {
            "total_link_count": total_link_count,
            "internal_link_count": internal_links,
            "external_link_count": external_links,
            "nofollow_link_count": nofollow_links,
            "sponsored_link_count": sponsored_links,
            "ugc_link_count": ugc_links,
            "internal_link_ratio": (
                internal_link_ratio
            ),
            "external_unique_domain_count": len(
                external_domains
            ),
        }

    # ==================================================
    # V4 — TECHNICAL
    # ==================================================

    def extract_technical(self) -> dict:
        """Extract basic technical SEO signals."""

        canonical_exists = False

        for link in self.soup.find_all(
            "link"
        ):
            rel = link.get(
                "rel",
                [],
            )

            if isinstance(
                rel,
                str,
            ):
                rel = rel.split()

            rel = [
                value.lower()
                for value in rel
            ]

            if (
                "canonical"
                in rel
            ):
                canonical_exists = True
                break

        robots_meta = self.soup.find(
            "meta",
            attrs={
                "name": lambda value: (
                    value
                    and value.lower()
                    == "robots"
                )
            },
        )

        viewport_meta = self.soup.find(
            "meta",
            attrs={
                "name": lambda value: (
                    value
                    and value.lower()
                    == "viewport"
                )
            },
        )

        html_tag = self.soup.find(
            "html"
        )

        lang_exists = bool(
            html_tag
            and html_tag.get(
                "lang"
            )
        )

        return {
            "canonical_exists": (
                canonical_exists
            ),
            "robots_meta_exists": (
                robots_meta is not None
            ),
            "viewport_exists": (
                viewport_meta is not None
            ),
            "lang_exists": lang_exists,
        }

    # ==================================================
    # V4 — STRUCTURED DATA
    # ==================================================

    def extract_structured_data(
        self,
    ) -> dict:
        """Extract basic JSON-LD / Schema.org signals."""

        jsonld_blocks = (
            self.soup.find_all(
                "script",
                attrs={
                    "type": (
                        "application/ld+json"
                    )
                },
            )
        )

        schema_org_count = 0

        for script in jsonld_blocks:

            text = script.get_text(
                strip=True
            )

            if (
                "schema.org"
                in text.lower()
            ):
                schema_org_count += 1

        return {
            "jsonld_count": len(
                jsonld_blocks
            ),
            "schema_org_count": (
                schema_org_count
            ),
        }

    # ==================================================
    # V4 — BUSINESS SIGNALS
    # ==================================================

    def extract_business_signals(
        self,
    ) -> dict:
        """
        Extract simple HTML-level business/conversion signals.

        These are heuristics only. They do not prove
        trustworthiness, authority or conversion quality.
        """

        text = self.soup.get_text(
            " ",
            strip=True,
        )

        lowered_text = (
            text.lower()
        )

        cta_keywords = [
            "contact",
            "contacter",
            "demander un devis",
            "devis",
            "réserver",
            "reservation",
            "réservez",
            "acheter",
            "commander",
            "commandez",
            "prendre rendez-vous",
            "prendre rendez vous",
            "appointment",
            "book now",
            "get started",
            "learn more",
            "en savoir plus",
        ]

        cta_count = 0

        for keyword in cta_keywords:
            cta_count += (
                lowered_text.count(
                    keyword
                )
            )

        phone_pattern = re.compile(
            r"""
            (?:
                \+33[\s.\-]?
                [1-9]
                (?:
                    [\s.\-]?
                    \d{2}
                ){4}
            )
            |
            (?:
                0[1-9]
                (?:
                    [\s.\-]?
                    \d{2}
                ){4}
            )
            """,
            re.VERBOSE,
        )

        email_pattern = re.compile(
            r"""
            [A-Z0-9._%+-]+
            @
            [A-Z0-9.-]+
            \.
            [A-Z]{2,}
            """,
            re.IGNORECASE
            | re.VERBOSE,
        )

        phone_count = len(
            phone_pattern.findall(
                text
            )
        )

        email_count = len(
            email_pattern.findall(
                text
            )
        )

        return {
            "cta_count": cta_count,
            "phone_count": phone_count,
            "email_count": email_count,
        }

    # ==================================================
    # ALL FEATURES
    # ==================================================

    def extract_all(self) -> dict:
        """Run all extraction methods."""

        features = {}

        features.update(
            self.extract_title()
        )

        features.update(
            self.extract_meta_description()
        )

        features.update(
            self.extract_headings()
        )

        features.update(
            self.extract_content()
        )

        features.update(
            self.extract_images()
        )

        features.update(
            self.extract_links()
        )

        features.update(
            self.extract_technical()
        )

        features.update(
            self.extract_structured_data()
        )

        features.update(
            self.extract_business_signals()
        )

        return features