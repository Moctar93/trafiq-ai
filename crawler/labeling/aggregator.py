from collections import Counter

from crawler.labeling import SEOClass


DEFAULT_CONFIDENCE_THRESHOLD = 0.80


def aggregate_labels(
    labels: dict[str, SEOClass],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict:
    """
    Aggregate labeling-function outputs into a global label.

    ABSTAIN votes are ignored.

    The function returns:
    - the majority label
    - the consensus confidence
    - the number of active votes
    - the individual votes
    - whether the result is ambiguous
    - whether the result is eligible for dataset generation

    A result is dataset-eligible only when:
    - there is at least one active vote
    - the result is not ambiguous
    - confidence >= confidence_threshold
    """

    if not 0 <= confidence_threshold <= 1:
        raise ValueError(
            "confidence_threshold must be between 0 and 1"
        )

    active_labels = [
        label
        for label in labels.values()
        if label != SEOClass.ABSTAIN
    ]

    votes = {
        name: label.value
        for name, label in labels.items()
    }

    if not active_labels:
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": 0.0,
            "vote_count": 0,
            "votes": votes,
            "ambiguous": False,
            "training_eligible": False,
        }

    counts = Counter(active_labels)

    highest_count = max(counts.values())

    winners = [
        label
        for label, count in counts.items()
        if count == highest_count
    ]

    confidence = highest_count / len(active_labels)

    # Several labels have the same number of votes.
    if len(winners) > 1:
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": round(confidence, 4),
            "vote_count": len(active_labels),
            "votes": votes,
            "ambiguous": True,
            "training_eligible": False,
        }

    winner = winners[0]

    training_eligible = (
        confidence >= confidence_threshold
    )

    return {
        "label": winner.value,
        "confidence": round(confidence, 4),
        "vote_count": len(active_labels),
        "votes": votes,
        "ambiguous": False,
        "training_eligible": training_eligible,
    }