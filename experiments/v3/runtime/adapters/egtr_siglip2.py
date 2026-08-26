"""Frozen `v3.1-egtr-siglip2` isolated bounded-observation adapter."""

from __future__ import annotations

import json
import os
import subprocess

from PIL import Image

from prototype.semantic_secrets.v3 import load_active_contract

from ..io import canonical_bytes
from ..telemetry import Telemetry
from .common import SiglipScorer, base_observation, component_event, confidence, emit, padded_crop, read_request, setting


def main() -> int:
    request = read_request()
    if request["pipeline_id"] != "v3.1-egtr-siglip2":
        raise SystemExit("wrong adapter pipeline")
    contract = load_active_contract()
    components = contract.component_map(request["pipeline_id"])
    output = base_observation(request)
    image = Image.open(request["image_path"]).convert("RGB")
    worker_request = dict(request)
    worker_request["allowed_entities"] = contract.amend_observation["shared_gate_entity_label_intersection"]
    worker_request["allowed_predicates"] = contract.pipeline(request["pipeline_id"])["adapter"]["predicate_label_intersection"]
    process = subprocess.run(
        [os.environ.get("EGTR_PYTHON", "/opt/conda/bin/python"), "-m", "experiments.v3.runtime.adapters.egtr_worker"],
        input=canonical_bytes(worker_request), capture_output=True, timeout=request["timeout_seconds"],
    )
    if process.returncode != 0:
        raise RuntimeError("EGTR legacy worker failed closed: " + process.stderr.decode("utf-8", errors="replace")[-2000:])
    egtr_output = json.loads(process.stdout)
    egtr = components["egtr-vg"]
    entity_threshold = setting(request, "entity")
    predicate_threshold = setting(request, "predicate")
    connectivity_threshold = setting(request, "connectivity")
    for row in egtr_output["detections"]:
        output["detections"].append({**{key: row[key] for key in ("local_id", "category", "bbox")}, "confidence": confidence(row["score"], entity_threshold), "component_id": "egtr-vg", "component_revision": egtr["revision"]})
    for row in egtr_output["binary_interactions"]:
        output["binary_interactions"].append({**{key: row[key] for key in ("source_detection_id", "target_detection_id", "interaction")}, "confidence": confidence(row["predicate_score"], predicate_threshold), "connectivity_confidence": confidence(row["connectivity_score"], connectivity_threshold), "component_id": "egtr-vg", "component_revision": egtr["revision"]})
    output["component_events"].append(component_event("egtr-vg", egtr["revision"], "ok", egtr_output["telemetry"]))
    output["execution_telemetry"].append({"component_id": "egtr-vg", **egtr_output["telemetry"]})

    siglip = components["siglip2-base-384"]
    with Telemetry() as meter:
        scorer = SiglipScorer()
        for detection in output["detections"]:
            crop, category = padded_crop(image, detection["bbox"]), detection["category"]
            for atom_type, values in contract.base_observation["attributes"].items():
                threshold = setting(request, atom_type)
                winner = scorer.winner(crop, [f"a photo of a {value} {category}" for value in values], list(values), threshold)
                if winner:
                    value, score = winner
                    output["attributes"].append({"detection_id": detection["local_id"], "attribute_type": atom_type, "value": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
        threshold, values = setting(request, "scene"), list(contract.base_observation["scenes"])
        winner = scorer.winner(image, [f"a photo taken in a {value}" for value in values], values, threshold)
        if winner:
            value, score = winner
            output["scenes"].append({"value": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
        siglip_telemetry = meter.finish()
    output["component_events"].append(component_event("siglip2-base-384", siglip["revision"], "ok", siglip_telemetry))
    output["execution_telemetry"].append({"component_id": "siglip2-base-384", **siglip_telemetry})
    emit(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
