from collections import Counter

from crawler.labeling import SEOClass


MIN_TRAINING_VOTES = 3
MIN_TRAINING_CONFIDENCE = 0.80


def aggregate_labels(
    labels: dict[str, SEOClass],
) -> dict:
    """
    Aggregate labeling function outputs into a global label.

    ABSTAIN votes are ignored.

    If several classes have the same number of votes,
    the result is considered ambiguous.

    Training eligibility is deliberately stricter than
    final-label selection:
    - minimum 3 active votes
    - confidence >= 0.80
    - not ambiguous
    """

    active_labels = [
        label
        for label in labels.values()
        if label != SEOClass.ABSTAIN
    ]

    votes = {
        name: label.value
        for name, label in labels.items()
    }

    # --------------------------------------------------
    # No active vote
    # --------------------------------------------------
    if not active_labels:
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": 0.0,
            "vote_count": 0,
            "votes": votes,
            "ambiguous": False,
            "training_eligible": False,
        }

    # --------------------------------------------------
    # Count votes
    # --------------------------------------------------
    counts = Counter(
        active_labels
    )

    highest_count = max(
        counts.values()
    )

    winners = [
        label
        for label, count in counts.items()
        if count == highest_count
    ]

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------
    confidence = (
        highest_count
        / len(active_labels)
    )

    confidence = round(
        confidence,
        4,
    )

    vote_count = len(
        active_labels
    )

    # --------------------------------------------------
    # Ambiguous result
    # --------------------------------------------------
    if len(winners) > 1:
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": confidence,
            "vote_count": vote_count,
            "votes": votes,
            "ambiguous": True,
            "training_eligible": False,
        }

    # --------------------------------------------------
    # Clear winner
    # --------------------------------------------------
    winner = winners[0]

    # --------------------------------------------------
    # Strict training eligibility
    # --------------------------------------------------
    training_eligible = (
        confidence >= MIN_TRAINING_CONFIDENCE
        and vote_count >= MIN_TRAINING_VOTES
        and len(winners) == 1
    )

    return {
        "label": winner.value,
        "confidence": confidence,
        "vote_count": vote_count,
        "votes": votes,
        "ambiguous": False,
        "training_eligible": training_eligible,
    }