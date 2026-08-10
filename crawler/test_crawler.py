from crawler import WebsiteCrawler


def main():
    crawler = WebsiteCrawler()

    result = crawler.fetch("https://example.com")

    print("\n=== TRAFIQ AI — CRAWLER TEST ===")

    for key, value in result.items():
        if key == "html":
            print(f"{key}: {len(value)} characters")
        elif key == "headers":
            print(f"{key}: {len(value)} headers")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()