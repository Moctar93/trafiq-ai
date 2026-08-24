from crawler.schemas import SEOFeatures
from crawler.validators import validate_seo_features


def main():
    valid_features = SEOFeatures(
        # Title
        title_exists=True,
        title_length=50,
        title_word_count=8,

        # Meta description
        meta_description_exists=True,
        meta_description_length=150,
        meta_description_word_count=22,

        # Headings
        h1_count=1,
        h2_count=3,
        h3_count=2,
        h4_count=0,
        h5_count=0,
        h6_count=0,
        heading_total_count=6,

        # Content
        word_count=500,
        character_count=3000,
        unique_word_count=300,
        unique_word_ratio=0.6,

        # Images
        image_count=5,
        images_with_alt=5,
        images_without_alt=0,
        images_missing_alt_attribute=0,
        empty_alt_count=0,
        alt_coverage_ratio=1.0,

        # Links
        total_link_count=10,
        internal_link_count=5,
        external_link_count=5,
        nofollow_link_count=0,
        sponsored_link_count=0,
        ugc_link_count=0,
        internal_link_ratio=0.5,
    )

    print("\n=== TRAFIQ AI — VALIDATION TEST ===")

    valid_errors = validate_seo_features(
        valid_features
    )

    if valid_errors:
        print("Validation failed:")

        for error in valid_errors:
            print(f"- {error}")

        return

    print("Validation successful!")


if __name__ == "__main__":
    main()