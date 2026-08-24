"""Protocol-neutral plaintext matchers used before private protocol selection."""

from .metrics import (
    ThresholdDecision,
    cardinality_score,
    cosine_score,
    jaccard_score,
    select_threshold,
    threshold_decision,
    weighted_overlap_score,
)

__all__ = [
    "ThresholdDecision",
    "cardinality_score",
    "cosine_score",
    "jaccard_score",
    "select_threshold",
    "threshold_decision",
    "weighted_overlap_score",
]
