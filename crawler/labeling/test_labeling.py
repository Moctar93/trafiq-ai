from crawler.pipeline import SEOPipeline
from crawler.labeling.functions import (
    label_title,
    label_meta_description,
    label_headings,
    label_content,
    label_images,
    label_links,
)


def main():
    pipeline = SEOPipeline()

    result = pipeline.analyze(
        "https://example.com"
    )

    print("\n=== TRAFIQ AI — LABELING TEST ===")

    if not result["success"]:
        print("Pipeline failed:")

        for error in result["errors"]:
            print(f"- {error}")

        return

    from crawler.schemas import SEOFeatures

    features = SEOFeatures(
        **result["features"]
    )

    labels = {
        "TITLE": label_title(features),
        "META": label_meta_description(features),
        "HEADINGS": label_headings(features),
        "CONTENT": label_content(features),
        "IMAGES": label_images(features),
        "LINKS": label_links(features),
    }

    for name, label in labels.items():
        print(f"{name}: {label.value}")


if __name__ == "__main__":
    main()