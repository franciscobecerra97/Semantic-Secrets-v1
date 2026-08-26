"""Frozen v3 observation/compiler implementation.

This package contains deterministic preparation code only. Model adapters emit
bounded observations; only :mod:`compiler` constructs canonical graph results.
"""

from .compiler import SemanticCompilerV3, canonical_json_bytes
from .contract import ActiveV31Contract, load_active_contract

__all__ = [
    "ActiveV31Contract",
    "SemanticCompilerV3",
    "canonical_json_bytes",
    "load_active_contract",
]
