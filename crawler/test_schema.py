from crawler.schemas import SEOFeatures


def main():
    features = SEOFeatures(
        title_exists=True,
        title_length=14,
        title_word_count=2,
        meta_description_exists=False,
        meta_description_length=0,
        meta_description_word_count=0,
        h1_count=1,
        h2_count=0,
        h3_count=0,
        h4_count=0,
        h5_count=0,
        h6_count=0,
        word_count=21,
        character_count=142,
        unique_word_count=16,
        unique_word_ratio=0.76,
        image_count=0,
        images_with_alt=0,
        images_without_alt=0,
        empty_alt_count=0,
        total_link_count=1,
        internal_link_count=0,
        external_link_count=1,
        nofollow_link_count=0,
        sponsored_link_count=0,
        ugc_link_count=0,
    )

    print("\n=== TRAFIQ AI — SCHEMA TEST ===")
    print(features)
    print("\nValidation successful!")


if __name__ == "__main__":
    main()