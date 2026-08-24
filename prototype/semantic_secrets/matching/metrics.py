"""Deterministic plaintext similarity scores and threshold selection."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


def cardinality_score(left: Iterable[str], right: Iterable[str]) -> int:
    """Return the exact set-intersection cardinality."""

    return len(set(left) & set(right))


def jaccard_score(left: Iterable[str], right: Iterable[str]) -> float:
    """Return Jaccard similarity, defining two empty sets as identical."""

    left_set, right_set = set(left), set(right)
    union = left_set | right_set
    return 1.0 if not union else len(left_set & right_set) / len(union)


def weighted_overlap_score(
    enrolled: Iterable[str],
    candidate: Iterable[str],
    weights: Mapping[str, float],
) -> float:
    """Return matched enrolled weight divided by total enrolled weight.

    The score is intentionally directional: the first argument is the enrolled
    credential. Atoms absent from the frozen weight table receive weight 1.0.
    """

    enrolled_set, candidate_set = set(enrolled), set(candidate)
    denominator = sum(float(weights.get(atom, 1.0)) for atom in enrolled_set)
    if denominator == 0:
        return 1.0 if not candidate_set else 0.0
    return sum(float(weights.get(atom, 1.0)) for atom in enrolled_set & candidate_set) / denominator


def cosine_score(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity and fail closed for invalid or zero vectors."""

    if len(left) != len(right) or not left:
        raise ValueError("cosine vectors must be non-empty and have equal length")
    dot = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) ** 2 for value in left))
    right_norm = math.sqrt(sum(float(value) ** 2 for value in right))
    if not math.isfinite(dot) or not math.isfinite(left_norm) or not math.isfinite(right_norm):
        raise ValueError("cosine vectors must contain finite values")
    if left_norm == 0 or right_norm == 0:
        raise ValueError("cosine is undefined for a zero vector")
    return max(-1.0, min(1.0, dot / (left_norm * right_norm)))


@dataclass(frozen=True)
class ThresholdDecision:
    threshold: float
    false_reject_rate: float
    near_false_accept_rate: float
    random_false_accept_rate: float
    objective: tuple[float, float, float, float]


def threshold_decision(
    threshold: float,
    positive_scores: Sequence[float],
    near_scores: Sequence[float],
    random_scores: Sequence[float],
) -> ThresholdDecision:
    """Evaluate an inclusive score threshold."""

    if not positive_scores or not near_scores or not random_scores:
        raise ValueError("threshold evaluation requires positive, near, and random scores")
    frr = sum(score < threshold for score in positive_scores) / len(positive_scores)
    near_far = sum(score >= threshold for score in near_scores) / len(near_scores)
    random_far = sum(score >= threshold for score in random_scores) / len(random_scores)
    # Predeclared minimax rule: protect the worst error class, then total error,
    # then accepted-negative mass, and finally prefer the stricter threshold.
    objective = (
        max(frr, near_far, random_far),
        frr + near_far + random_far,
        near_far + random_far,
        -float(threshold),
    )
    return ThresholdDecision(float(threshold), frr, near_far, random_far, objective)


def select_threshold(
    positive_scores: Sequence[float],
    near_scores: Sequence[float],
    random_scores: Sequence[float],
) -> ThresholdDecision:
    """Select a threshold using the frozen deterministic minimax rule."""

    values = [float(value) for value in [*positive_scores, *near_scores, *random_scores]]
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("threshold scores must be finite and non-empty")
    candidates = sorted(set(values) | {math.nextafter(max(values), math.inf)})
    return min(
        (threshold_decision(value, positive_scores, near_scores, random_scores) for value in candidates),
        key=lambda decision: decision.objective,
    )
