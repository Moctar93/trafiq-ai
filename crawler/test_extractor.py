from crawler.crawler import WebsiteCrawler
from crawler.extractor import HTMLExtractor


def main():
    crawler = WebsiteCrawler()

    crawl_result = crawler.fetch(
        "https://example.com"
    )

    extractor = HTMLExtractor(
        html=crawl_result["html"],
        base_url=crawl_result["url"],
    )

    features = extractor.extract_all()

    print("\n=== TRAFIQ AI — EXTRACTION TEST ===")

    for key, value in features.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()