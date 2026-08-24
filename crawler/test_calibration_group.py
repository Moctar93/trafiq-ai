from crawler.collector import SEOCollector


def main():
    collector = SEOCollector()

    urls = [
        "https://abondance.com/",
    ]

    print(
        "\n=== TRAFIQ AI — CALIBRATION GROUP TEST ==="
    )

    summary = collector.collect(
        urls,
        calibration_group="rich_candidate",
    )

    print("\n--- SUMMARY ---")

    for key, value in summary.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()