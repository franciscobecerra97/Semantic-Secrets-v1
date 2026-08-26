"""Schema validation for pre-execution records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "experiments" / "v3" / "schemas"


def validate(name: str, value: Any) -> None:
    schema = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
    jsonschema.validate(value, schema)
