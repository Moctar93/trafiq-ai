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

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)

    def save_raw(self, observation: dict, filename: str):
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

    def append_processed(
        self,
        observation: dict,
        filename: str = "seo_dataset.csv",
    ):
        """Append a validated observation to the processed dataset."""

        filepath = self.processed_dir / filename

        features = observation["features"]

        row = {
            "url": observation["url"],
            "domain": observation["domain"],
            "status_code": observation["status_code"],
            "response_time_ms": observation["response_time_ms"],
            "redirect_count": observation["redirect_count"],
            **features,
        }

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
        
        """Append a labeled SEO observation to the labeled dataset."""

        filepath = self.processed_dir / filename

        features = observation["features"]

        row = {
            "url": observation["url"],
            "domain": observation["domain"],
            "status_code": observation["status_code"],
            "response_time_ms": observation["response_time_ms"],
            "redirect_count": observation["redirect_count"],
            **features,

            "title_label": labels["TITLE"].value,
            "meta_label": labels["META"].value,
            "headings_label": labels["HEADINGS"].value,
            "content_label": labels["CONTENT"].value,
            "images_label": labels["IMAGES"].value,
            "links_label": labels["LINKS"].value,

            "final_label": aggregation["label"],
            "confidence": aggregation["confidence"],
            "vote_count": aggregation["vote_count"],
            "ambiguous": aggregation["ambiguous"],
            "training_eligible": aggregation["training_eligible"],
        }

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