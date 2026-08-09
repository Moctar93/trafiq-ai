from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class HTMLExtractor:

    def __init__(self, html: str, base_url: str):
        self.soup = BeautifulSoup(html, "html.parser")
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc

    def extract_title(self):
        title = self.soup.find("title")

        if not title:
            return {
                "title_exists": False,
                "title_length": 0,
            }

        text = title.get_text(strip=True)

        return {
            "title_exists": True,
            "title_length": len(text),
        }

    def extract_meta_description(self):
        meta = self.soup.find(
            "meta",
            attrs={"name": lambda value: value and value.lower() == "description"}
        )

        if not meta:
            return {
                "meta_description_exists": False,
                "meta_description_length": 0,
            }

        content = meta.get("content", "").strip()

        return {
            "meta_description_exists": True,
            "meta_description_length": len(content),
        }

    def extract_headings(self):
        return {
            "h1_count": len(self.soup.find_all("h1")),
            "h2_count": len(self.soup.find_all("h2")),
            "h3_count": len(self.soup.find_all("h3")),
        }