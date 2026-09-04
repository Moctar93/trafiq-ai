from enum import Enum


class SEOClass(str, Enum):
    POOR = "POOR"
    AVERAGE = "AVERAGE"
    GOOD = "GOOD"
    ABSTAIN = "ABSTAIN"