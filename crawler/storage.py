import csv
import json
from pathlib import Path


class DatasetStorage:
    """Store validated SEO observations on disk."""

    # ==================================================
    # V4 FEATURES
    # ==================================================

    V4_FEATURES = {
        "canonical_exists",
        "robots_meta_exists",
        "viewport_exists",
        "lang_exists",
        "jsonld_count",
        "schema_org_count",
        "cta_count",
        "phone_count",
        "email_count",
        "external_unique_domain_count",
    }

    def __init__(
        self,
        base_dir: str = "data",
    ):
        self.base_dir = Path(
            base_dir
        )

        self.raw_dir = (
            self.base_dir / "raw"
        )

        self.processed_dir = (
            self.base_dir / "processed"
        )

        self.rejected_dir = (
            self.base_dir / "rejected"
        )

        self._create_directories()

    # ==================================================
    # DIRECTORIES
    # ==================================================

    def _create_directories(self):
        """Create dataset directories."""

        self.raw_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.processed_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.rejected_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==================================================
    # RAW
    # ==================================================

    def save_raw(
        self,
        observation: dict,
        filename: str,
    ):
        """Save a raw observation as JSON."""

        filepath = (
            self.raw_dir / filename
        )

        with filepath.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                observation,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return filepath

    # ==================================================
    # REJECTED
    # ==================================================

    def save_rejected(
        self,
        observation: dict,
        filename: str,
    ):
        """Save a rejected observation as JSON."""

        filepath = (
            self.rejected_dir
            / filename
        )

        with filepath.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                observation,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return filepath

    # ==================================================
    # VALIDATION
    # ==================================================

    def _validate_v4_features(
        self,
        observation: dict,
    ):
        """
        Validate that all V4 features are present.

        This deliberately raises an error instead of
        silently writing an incomplete V4 dataset.
        """

        features = observation.get(
            "features",
            {},
        )

        missing = (
            self.V4_FEATURES
            - set(features.keys())
        )

        if missing:
            raise ValueError(
                "Missing V4 features: "
                + ", ".join(
                    sorted(missing)
                )
            )

    # ==================================================
    # BASE ROW
    # ==================================================

    def _build_base_row(
        self,
        observation: dict,
    ) -> dict:
        """
        Build the dataset row.

        The feature dictionary is intentionally expanded
        dynamically so V3/V4 features are preserved.
        """

        self._validate_v4_features(
            observation
        )

        features = observation.get(
            "features",
            {},
        )

        return {
            # --------------------------------------------------
            # Identity
            # --------------------------------------------------

            "crawl_id": observation[
                "crawl_id"
            ],

            "page_id": observation[
                "page_id"
            ],

            "crawl_timestamp": observation[
                "crawl_timestamp"
            ],

            "content_hash": observation[
                "content_hash"
            ],

            # --------------------------------------------------
            # Calibration
            # --------------------------------------------------

            "calibration_group": observation.get(
                "calibration_group",
                "unknown",
            ),

            # --------------------------------------------------
            # Crawl quality
            # --------------------------------------------------

            "crawl_quality": observation.get(
                "crawl_quality",
                "NORMAL",
            ),

            "html_size_bytes": observation.get(
                "html_size_bytes",
                0,
            ),

            # --------------------------------------------------
            # URL / HTTP
            # --------------------------------------------------

            "url": observation[
                "url"
            ],

            "domain": observation[
                "domain"
            ],

            "status_code": observation[
                "status_code"
            ],

            "response_time_ms": observation[
                "response_time_ms"
            ],

            "redirect_count": observation[
                "redirect_count"
            ],

            # --------------------------------------------------
            # SEO FEATURES
            # --------------------------------------------------

            **features,
        }

    # ==================================================
    # DUPLICATES
    # ==================================================

    def is_duplicate(
        self,
        page_id: str,
        content_hash: str,
        filename: str = (
            "seo_dataset_v4.csv"
        ),
    ) -> bool:
        """
        Check whether the same page state already exists.

        Duplicate means:
        - same page_id
        - same content_hash
        """

        filepath = (
            self.processed_dir
            / filename
        )

        if not filepath.exists():
            return False

        with filepath.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                if (
                    row.get("page_id")
                    == page_id
                    and row.get(
                        "content_hash"
                    )
                    == content_hash
                ):
                    return True

        return False

    # ==================================================
    # CSV HEADER
    # ==================================================

    def _get_existing_fieldnames(
        self,
        filepath: Path,
    ):
        """Read the existing CSV header."""

        if not filepath.exists():
            return None

        with filepath.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.reader(
                file
            )

            return next(
                reader,
                None,
            )

    # ==================================================
    # APPEND PROCESSED
    # ==================================================

    def append_processed(
        self,
        observation: dict,
        filename: str = (
            "seo_dataset_v4.csv"
        ),
    ):
        """
        Append a validated observation.

        Duplicate observations are skipped.

        V4 observations are validated so missing
        features cannot silently enter the dataset.
        """

        if self.is_duplicate(
            page_id=observation[
                "page_id"
            ],
            content_hash=observation[
                "content_hash"
            ],
            filename=filename,
        ):
            return None

        filepath = (
            self.processed_dir
            / filename
        )

        row = self._build_base_row(
            observation
        )

        file_exists = (
            filepath.exists()
        )

        existing_fieldnames = (
            self._get_existing_fieldnames(
                filepath
            )
        )

        if file_exists and existing_fieldnames:
            fieldnames = (
                existing_fieldnames
            )

            missing_columns = [
                key
                for key in row.keys()
                if key
                not in fieldnames
            ]

            if missing_columns:
                raise ValueError(
                    "Existing CSV header is missing "
                    "columns: "
                    + ", ".join(
                        missing_columns
                    )
                )

        else:
            fieldnames = list(
                row.keys()
            )

        with filepath.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        return filepath

    # ==================================================
    # APPEND LABELED
    # ==================================================

    def append_labeled(
        self,
        observation: dict,
        labels: dict,
        aggregation: dict,
        filename: str = (
            "seo_labeled_dataset_v4.csv"
        ),
    ):
        """
        Append a labeled observation.

        Duplicate observations are skipped.
        """

        if self.is_duplicate(
            page_id=observation[
                "page_id"
            ],
            content_hash=observation[
                "content_hash"
            ],
            filename=filename,
        ):
            return None

        filepath = (
            self.processed_dir
            / filename
        )

        row = self._build_base_row(
            observation
        )

        row.update(
            {
                "title_label": labels[
                    "TITLE"
                ].value,

                "meta_label": labels[
                    "META"
                ].value,

                "headings_label": labels[
                    "HEADINGS"
                ].value,

                "content_label": labels[
                    "CONTENT"
                ].value,

                "images_label": labels[
                    "IMAGES"
                ].value,

                "links_label": labels[
                    "LINKS"
                ].value,

                "final_label": aggregation[
                    "label"
                ],

                "confidence": aggregation[
                    "confidence"
                ],

                "vote_count": aggregation[
                    "vote_count"
                ],

                "ambiguous": aggregation[
                    "ambiguous"
                ],

                "training_eligible": aggregation[
                    "training_eligible"
                ],
            }
        )

        file_exists = (
            filepath.exists()
        )

        existing_fieldnames = (
            self._get_existing_fieldnames(
                filepath
            )
        )

        if file_exists and existing_fieldnames:

            fieldnames = (
                existing_fieldnames
            )

            missing_columns = [
                key
                for key in row.keys()
                if key
                not in fieldnames
            ]

            if missing_columns:
                raise ValueError(
                    "Existing labeled CSV header "
                    "is missing columns: "
                    + ", ".join(
                        missing_columns
                    )
                )

        else:
            fieldnames = list(
                row.keys()
            )

        with filepath.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        return filepath