"""Read-only composition of the frozen v3.0 through v3.3 contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT / "experiments" / "v3" / "config"
BASE_PREREG_PATH = CONFIG_DIR / "preregistration_v3.json"
AMEND_PREREG_PATH = CONFIG_DIR / "preregistration_v3_1.json"
GROUND_TRUTH_PREREG_PATH = CONFIG_DIR / "preregistration_v3_2.json"
CALIBRATION_PREREG_PATH = CONFIG_DIR / "preregistration_v3_3.json"
SMOKE_SETTINGS_PATH = CONFIG_DIR / "engineering_smoke_settings_v3_3.json"
BASE_OBSERVATION_PATH = CONFIG_DIR / "visual_observation_v3.json"
AMEND_OBSERVATION_PATH = CONFIG_DIR / "visual_observation_v3_1.json"


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ActiveV3Contract:
    base_prereg: Mapping[str, Any]
    amend_prereg: Mapping[str, Any]
    ground_truth_prereg: Mapping[str, Any]
    calibration_prereg: Mapping[str, Any]
    base_observation: Mapping[str, Any]
    amend_observation: Mapping[str, Any]
    config_hashes: Mapping[str, str]

    @property
    def observation_version(self) -> str:
        return str(self.amend_observation["$schema_version"])

    @property
    def compiler_id(self) -> str:
        return str(self.base_observation["compiler"]["compiler_id"])

    @property
    def result_schema(self) -> str:
        return str(self.base_observation["compiler"]["result_schema"])

    @property
    def pipeline_ids(self) -> tuple[str, ...]:
        return tuple(str(item["pipeline_id"]) for item in self.amend_observation["pipelines"])

    def pipeline(self, pipeline_id: str) -> Mapping[str, Any]:
        for pipeline in self.amend_observation["pipelines"]:
            if pipeline["pipeline_id"] == pipeline_id:
                return pipeline
        raise KeyError(pipeline_id)

    def component_map(self, pipeline_id: str) -> dict[str, Mapping[str, Any]]:
        return {str(item["component_id"]): item for item in self.pipeline(pipeline_id)["components"]}

    def expected_pipeline_revision(self, pipeline_id: str) -> str:
        digest = sha256_bytes(canonical_json_bytes(self.pipeline(pipeline_id)))
        return f"v3.1-config-{digest[:16]}"

    @property
    def all_config_sha256(self) -> str:
        return sha256_bytes(canonical_json_bytes(dict(sorted(self.config_hashes.items()))))


@lru_cache(maxsize=1)
def load_active_contract() -> ActiveV3Contract:
    paths = {
        "preregistration_v3.json": BASE_PREREG_PATH,
        "preregistration_v3_1.json": AMEND_PREREG_PATH,
        "preregistration_v3_2.json": GROUND_TRUTH_PREREG_PATH,
        "preregistration_v3_3.json": CALIBRATION_PREREG_PATH,
        "engineering_smoke_settings_v3_3.json": SMOKE_SETTINGS_PATH,
        "visual_observation_v3.json": BASE_OBSERVATION_PATH,
        "visual_observation_v3_1.json": AMEND_OBSERVATION_PATH,
    }
    contract = ActiveV3Contract(
        base_prereg=_read(BASE_PREREG_PATH),
        amend_prereg=_read(AMEND_PREREG_PATH),
        ground_truth_prereg=_read(GROUND_TRUTH_PREREG_PATH),
        calibration_prereg=_read(CALIBRATION_PREREG_PATH),
        base_observation=_read(BASE_OBSERVATION_PATH),
        amend_observation=_read(AMEND_OBSERVATION_PATH),
        config_hashes={name: sha256_file(path) for name, path in paths.items()},
    )
    if contract.observation_version != contract.amend_prereg["versions"]["observation"]:
        raise RuntimeError("v3.1 observation-version mismatch")
    if contract.pipeline_ids != tuple(contract.amend_prereg["candidate_shortlist"]["pipelines"]):
        raise RuntimeError("v3.1 pipeline shortlist mismatch")
    if contract.compiler_id != contract.amend_prereg["versions"]["compiler"]:
        raise RuntimeError("v3 compiler identity mismatch")
    if contract.ground_truth_prereg["versions"]["observation"] != contract.observation_version:
        raise RuntimeError("v3.2 must preserve the v3.1 observation contract")
    if contract.ground_truth_prereg["versions"]["compiler"] != contract.compiler_id:
        raise RuntimeError("v3.2 must preserve the v3.0 compiler")
    if contract.calibration_prereg["versions"]["calibration"] != "development-threshold-calibration-v3.3.0":
        raise RuntimeError("v3.3 calibration identity mismatch")
    if contract.calibration_prereg["candidate_grid"] != {
        "minimum": 0.0,
        "maximum": 1.0,
        "step": 0.01,
        "decimal_places": 2,
        "ordered_values": "0.00,0.01,...,1.00",
        "comparison": "inclusive greater-than-or-equal",
    }:
        raise RuntimeError("v3.3 candidate grid mismatch")
    return contract


# Compatibility alias for preparation code written before the v3.2
# ground-truth-only amendment. It has no effect on the scientific contract.
ActiveV31Contract = ActiveV3Contract
