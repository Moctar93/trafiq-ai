from crawler.identity import (
    generate_page_id,
    generate_content_hash,
    generate_crawl_id,
    generate_crawl_timestamp,
    normalize_url,
)


def main():
    url_1 = "https://example.com/about/"
    url_2 = "https://example.com/about/#section"

    normalized_1 = normalize_url(url_1)
    normalized_2 = normalize_url(url_2)

    page_id_1 = generate_page_id(url_1)
    page_id_2 = generate_page_id(url_2)

    content_a = "<html><body>Version A</body></html>"
    content_b = "<html><body>Version B</body></html>"

    hash_a = generate_content_hash(content_a)
    hash_a_again = generate_content_hash(content_a)
    hash_b = generate_content_hash(content_b)

    crawl_id = generate_crawl_id()
    crawl_timestamp = generate_crawl_timestamp()

    print("\n=== TRAFIQ AI — IDENTITY TEST ===")

    print(f"URL 1: {url_1}")
    print(f"Normalized URL 1: {normalized_1}")

    print(f"\nURL 2: {url_2}")
    print(f"Normalized URL 2: {normalized_2}")

    print(
        f"\nPage IDs identical: "
        f"{page_id_1 == page_id_2}"
    )

    print(f"Page ID: {page_id_1}")

    print(
        f"\nSame content hashes identical: "
        f"{hash_a == hash_a_again}"
    )

    print(
        f"Different content hashes different: "
        f"{hash_a != hash_b}"
    )

    print(f"Content hash A: {hash_a}")
    print(f"Content hash B: {hash_b}")

    print(f"\nCrawl ID: {crawl_id}")
    print(f"Crawl timestamp: {crawl_timestamp}")


if __name__ == "__main__":
    main()