"""Protocol-neutral structured representation containers and training-only weights."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .canonicalize import CANONICAL_SCHEME_VERSION, CanonicalResult, CanonicalizationError


@dataclass(frozen=True)
class StructuredSet:
    scheme_version: str
    atoms: frozenset[str]

    @classmethod
    def from_result(cls, result: CanonicalResult) -> "StructuredSet":
        if result.scheme_version != CANONICAL_SCHEME_VERSION:
            raise CanonicalizationError(f"unsupported canonical scheme: {result.scheme_version}")
        return cls(result.scheme_version, frozenset(result.atoms))

    def jaccard(self, other: "StructuredSet") -> float:
        self._compatible(other.scheme_version)
        union = self.atoms | other.atoms
        return 1.0 if not union else len(self.atoms & other.atoms) / len(union)

    def _compatible(self, other_version: str) -> None:
        if self.scheme_version != other_version:
            raise CanonicalizationError(
                f"representation version mismatch: {self.scheme_version!r} != {other_version!r}"
            )


@dataclass(frozen=True)
class WeightedStructuredSet:
    scheme_version: str
    atoms: frozenset[str]
    weights: Mapping[str, float]
    weights_version: str

    def overlap(self, other: "WeightedStructuredSet") -> float:
        if self.scheme_version != other.scheme_version or self.weights_version != other.weights_version:
            raise CanonicalizationError("weighted representation version mismatch")
        denominator = sum(self.weights.get(atom, 1.0) for atom in self.atoms)
        if denominator == 0:
            return 1.0 if not other.atoms else 0.0
        numerator = sum(self.weights.get(atom, 1.0) for atom in self.atoms & other.atoms)
        return numerator / denominator


def fit_idf_weights(
    training_documents: Sequence[Iterable[str]],
    *,
    weights_version: str,
) -> dict[str, float]:
    if not weights_version:
        raise ValueError("weights_version is required")
    documents = [set(document) for document in training_documents]
    if not documents:
        raise ValueError("at least one training document is required")
    atoms = sorted(set().union(*documents))
    count = len(documents)
    return {
        atom: math.log((count + 1) / (sum(atom in document for document in documents) + 1)) + 1.0
        for atom in atoms
    }
