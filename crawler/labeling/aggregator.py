from collections import Counter

from crawler.labeling import SEOClass


MIN_TRAINING_VOTES = 3
MIN_TRAINING_CONFIDENCE = 0.80


# These dimensions are considered too specialized
# to establish a global POOR label on their own.
METADATA_ONLY_NEGATIVE_LFS = {
    "TITLE",
    "META",
}

SPECIALIZED_NEGATIVE_LFS = {
    "HEADINGS",
    "IMAGES",
    "LINKS",
}


def _active_votes(
    labels: dict[str, SEOClass],
) -> list[tuple[str, SEOClass]]:
    """
    Return non-ABSTAIN votes together with their LF names.
    """

    return [
        (name, label)
        for name, label in labels.items()
        if label != SEOClass.ABSTAIN
    ]


def _confidence(
    active: list[tuple[str, SEOClass]],
) -> float:
    """
    Compute majority confidence.
    """

    if not active:
        return 0.0

    counts = Counter(
        label
        for _, label in active
    )

    highest = max(
        counts.values()
    )

    return round(
        highest / len(active),
        4,
    )


def _good_is_supported(
    active: list[tuple[str, SEOClass]],
) -> bool:
    """
    GOOD requires stronger positive evidence.

    Conditions:
    - at least two GOOD votes
    - CONTENT must be one of the GOOD votes
    """

    good_lfs = {
        name
        for name, label in active
        if label == SEOClass.GOOD
    }

    return (
        len(good_lfs) >= 2
        and "CONTENT" in good_lfs
    )


def _poor_is_supported(
    active: list[tuple[str, SEOClass]],
) -> bool:
    """
    Determine whether negative evidence is sufficiently
    diverse to support a global POOR label.

    Rules:
    - two POOR signals from at least two distinct dimensions
    - TITLE + META alone are insufficient
    - one isolated specialized negative signal is insufficient
    """

    poor_lfs = {
        name
        for name, label in active
        if label == SEOClass.POOR
    }

    if len(poor_lfs) < 2:
        return False

    # TITLE + META alone is not enough.
    if poor_lfs.issubset(
        METADATA_ONLY_NEGATIVE_LFS
    ):
        return False

    # There must be at least one negative
    # dimension beyond TITLE/META.
    non_metadata_negatives = (
        poor_lfs
        - METADATA_ONLY_NEGATIVE_LFS
    )

    return bool(
        non_metadata_negatives
    )


def _has_strong_conflict(
    active: list[tuple[str, SEOClass]],
) -> bool:
    """
    Detect strong GOOD/POOR conflict.
    """

    has_good = any(
        label == SEOClass.GOOD
        for _, label in active
    )

    has_poor = any(
        label == SEOClass.POOR
        for _, label in active
    )

    return (
        has_good
        and has_poor
    )


def aggregate_labels(
    labels: dict[str, SEOClass],
) -> dict:
    """
    V4.1 aggregation logic.

    Principles:
    - Specialized LFs do not decide the global label alone.
    - TITLE + META alone cannot force POOR.
    - HEADINGS alone cannot force POOR.
    - Two diverse POOR signals can support POOR.
    - GOOD requires CONTENT + another GOOD signal.
    - Strong GOOD/POOR conflict -> ABSTAIN.
    - One active vote -> ABSTAIN.
    - Training eligibility remains strict.
    """

    votes = {
        name: label.value
        for name, label in labels.items()
    }

    active = _active_votes(
        labels
    )

    vote_count = len(active)

    # --------------------------------------------------
    # No active votes
    # --------------------------------------------------

    if vote_count == 0:
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": 0.0,
            "vote_count": 0,
            "votes": votes,
            "ambiguous": False,
            "training_eligible": False,
        }

    confidence = _confidence(
        active
    )

    # --------------------------------------------------
    # One active vote
    # --------------------------------------------------

    if vote_count == 1:
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": confidence,
            "vote_count": 1,
            "votes": votes,
            "ambiguous": True,
            "training_eligible": False,
        }

    # --------------------------------------------------
    # Strong GOOD / POOR conflict
    # --------------------------------------------------

    if _has_strong_conflict(
        active
    ):
        return {
            "label": SEOClass.ABSTAIN.value,
            "confidence": confidence,
            "vote_count": vote_count,
            "votes": votes,
            "ambiguous": True,
            "training_eligible": False,
        }

    # --------------------------------------------------
    # Strong GOOD consensus
    # --------------------------------------------------

    if _good_is_supported(
        active
    ):

        good_count = sum(
            label == SEOClass.GOOD
            for _, label in active
        )

        good_confidence = round(
            good_count / vote_count,
            4,
        )

        return {
            "label": SEOClass.GOOD.value,
            "confidence": good_confidence,
            "vote_count": vote_count,
            "votes": votes,
            "ambiguous": False,
            "training_eligible": (
                good_confidence
                >= MIN_TRAINING_CONFIDENCE
                and vote_count
                >= MIN_TRAINING_VOTES
            ),
        }

    # --------------------------------------------------
    # Strong POOR consensus
    # --------------------------------------------------

    if _poor_is_supported(
        active
    ):

        poor_count = sum(
            label == SEOClass.POOR
            for _, label in active
        )

        poor_confidence = round(
            poor_count / vote_count,
            4,
        )

        return {
            "label": SEOClass.POOR.value,
            "confidence": poor_confidence,
            "vote_count": vote_count,
            "votes": votes,
            "ambiguous": False,
            "training_eligible": (
                poor_confidence
                >= MIN_TRAINING_CONFIDENCE
                and vote_count
                >= MIN_TRAINING_VOTES
            ),
        }

    # --------------------------------------------------
    # Standard majority
    # --------------------------------------------------

    counts = Counter(
        label
        for _, label in active
    )

    highest = max(
        counts.values()
    )

    winners = [
        label
        for label, count in counts.items()
        if count == highest
    ]

    # --------------------------------------------------
    # Ambiguous majority
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

    winner = winners[0]

    # --------------------------------------------------
    # Do not allow isolated specialized labels
    # to become a global decision.
    # --------------------------------------------------

    if winner in {
        SEOClass.AVERAGE,
        SEOClass.POOR,
        SEOClass.GOOD,
    }:

        winner_lfs = [
            name
            for name, label in active
            if label == winner
        ]

        if len(winner_lfs) < 2:
            return {
                "label": SEOClass.ABSTAIN.value,
                "confidence": confidence,
                "vote_count": vote_count,
                "votes": votes,
                "ambiguous": True,
                "training_eligible": False,
            }

    # --------------------------------------------------
    # Final majority result
    # --------------------------------------------------

    training_eligible = (
        confidence
        >= MIN_TRAINING_CONFIDENCE
        and vote_count
        >= MIN_TRAINING_VOTES
    )

    return {
        "label": winner.value,
        "confidence": confidence,
        "vote_count": vote_count,
        "votes": votes,
        "ambiguous": False,
        "training_eligible": training_eligible,
    }