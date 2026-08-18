import csv
import json
from pathlib import Path


class DatasetStorage:
    """Store validated SEO observations on disk."""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)

        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.rejected_dir = self.base_dir / "rejected"

        self._create_directories()

    def _create_directories(self):
        """Create dataset directories if they do not exist."""

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

    def save_raw(
        self,
        observation: dict,
        filename: str,
    ):
        """Save a raw observation as JSON."""

        filepath = self.raw_dir / filename

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

    def save_rejected(
        self,
        observation: dict,
        filename: str,
    ):
        """Save a rejected observation as JSON."""

        filepath = self.rejected_dir / filename

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

    def _build_base_row(
        self,
        observation: dict,
    ) -> dict:
        """
        Build the common row structure used by the datasets.
        """

        return {
            "crawl_id": observation["crawl_id"],
            "page_id": observation["page_id"],
            "crawl_timestamp": observation[
                "crawl_timestamp"
            ],
            "content_hash": observation[
                "content_hash"
            ],
            "url": observation["url"],
            "domain": observation["domain"],
            "status_code": observation[
                "status_code"
            ],
            "response_time_ms": observation[
                "response_time_ms"
            ],
            "redirect_count": observation[
                "redirect_count"
            ],
            **observation["features"],
        }

    def is_duplicate(
        self,
        page_id: str,
        content_hash: str,
        filename: str = "seo_dataset.csv",
    ) -> bool:
        """
        Check whether the same page and the same content
        have already been stored.
        """

        filepath = self.processed_dir / filename

        if not filepath.exists():
            return False

        with filepath.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                if (
                    row.get("page_id") == page_id
                    and row.get("content_hash") == content_hash
                ):
                    return True

        return False

    def append_processed(
        self,
        observation: dict,
        filename: str = "seo_dataset.csv",
    ):
        """
        Append a validated observation to the processed dataset.

        Duplicate observations are skipped when the same page_id
        and content_hash already exist.
        """

        if self.is_duplicate(
            page_id=observation["page_id"],
            content_hash=observation["content_hash"],
            filename=filename,
        ):
            return None

        filepath = self.processed_dir / filename

        row = self._build_base_row(
            observation
        )

        file_exists = filepath.exists()

        with filepath.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=row.keys(),
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        return filepath

    def append_labeled(
        self,
        observation: dict,
        labels: dict,
        aggregation: dict,
        filename: str = "seo_labeled_dataset.csv",
    ):
        """
        Append a labeled SEO observation to the
        labeled dataset.
        """

        filepath = self.processed_dir / filename

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

        file_exists = filepath.exists()

        with filepath.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=row.keys(),
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        return filepath