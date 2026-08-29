"""Frozen `v3.1-egtr-siglip2` persistent isolated adapter."""

from __future__ import annotations

import json
import os
import subprocess
import threading

from PIL import Image

from prototype.semantic_secrets.v3 import load_active_contract

from ..io import canonical_bytes
from ..telemetry import Telemetry
from .common import SiglipScorer, base_observation, component_event, confidence, padded_crop, serve, setting


class Pipeline:
    def __init__(self) -> None:
        self.pipeline_id = "v3.1-egtr-siglip2"
        self.contract = load_active_contract()
        self.components = self.contract.component_map(self.pipeline_id)
        self.scorer = SiglipScorer()
        self.worker = subprocess.Popen(
            [os.environ.get("EGTR_PYTHON", "/opt/conda/bin/python"), "-m", "experiments.v3.runtime.adapters.egtr_worker"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self._worker_stderr: list[bytes] = []
        assert self.worker.stderr is not None
        self._worker_stderr_thread = threading.Thread(target=self._drain_worker_stderr, daemon=True)
        self._worker_stderr_thread.start()

    def _drain_worker_stderr(self) -> None:
        assert self.worker.stderr is not None
        for block in iter(lambda: self.worker.stderr.read1(4096), b""):
            self._worker_stderr.append(block)
            if sum(map(len, self._worker_stderr)) > 16000:
                self._worker_stderr = [b"".join(self._worker_stderr)[-8000:]]

    def _egtr(self, request: dict) -> dict:
        worker_request = dict(request)
        worker_request["allowed_entities"] = self.contract.amend_observation["shared_gate_entity_label_intersection"]
        worker_request["allowed_predicates"] = self.contract.pipeline(self.pipeline_id)["adapter"]["predicate_label_intersection"]
        assert self.worker.stdin is not None and self.worker.stdout is not None
        self.worker.stdin.write(canonical_bytes(worker_request))
        self.worker.stdin.flush()
        line = self.worker.stdout.readline()
        if not line:
            stderr = b"".join(self._worker_stderr)[-2000:].decode("utf-8", errors="replace")
            raise RuntimeError("EGTR legacy worker failed closed: " + stderr)
        return json.loads(line)

    def __call__(self, request: dict) -> dict:
        if request["pipeline_id"] != self.pipeline_id:
            raise ValueError("wrong adapter pipeline")
        if request.get("operation") == "calibration_capture_entity":
            return self._capture_entity(request)
        if request.get("operation") == "calibration_capture_downstream":
            return self._capture_downstream(request)
        output = base_observation(request)
        image = Image.open(request["image_path"]).convert("RGB")
        egtr_output = self._egtr(request)
        egtr = self.components["egtr-vg"]
        entity_threshold, predicate_threshold = setting(request, "entity"), setting(request, "predicate")
        connectivity_threshold = setting(request, "connectivity")
        for row in egtr_output["detections"]:
            output["detections"].append({**{key: row[key] for key in ("local_id", "category", "bbox")}, "confidence": confidence(row["score"], entity_threshold), "component_id": "egtr-vg", "component_revision": egtr["revision"]})
        for row in egtr_output["binary_interactions"]:
            output["binary_interactions"].append({**{key: row[key] for key in ("source_detection_id", "target_detection_id", "interaction")}, "confidence": confidence(row["predicate_score"], predicate_threshold), "connectivity_confidence": confidence(row["connectivity_score"], connectivity_threshold), "component_id": "egtr-vg", "component_revision": egtr["revision"]})
        output["component_events"].append(component_event("egtr-vg", egtr["revision"], "ok", egtr_output["telemetry"]))
        output["execution_telemetry"].append({"component_id": "egtr-vg", **egtr_output["telemetry"]})

        siglip = self.components["siglip2-base-384"]
        with Telemetry() as meter:
            for detection in output["detections"]:
                crop, category = padded_crop(image, detection["bbox"]), detection["category"]
                for atom_type, values in self.contract.base_observation["attributes"].items():
                    threshold = setting(request, atom_type)
                    winner = self.scorer.winner(crop, [f"a photo of a {value} {category}" for value in values], list(values), threshold)
                    if winner:
                        value, score = winner
                        output["attributes"].append({"detection_id": detection["local_id"], "attribute_type": atom_type, "value": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
            threshold, values = setting(request, "scene"), list(self.contract.base_observation["scenes"])
            winner = self.scorer.winner(image, [f"a photo taken in a {value}" for value in values], values, threshold)
            if winner:
                value, score = winner
                output["scenes"].append({"value": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
            siglip_telemetry = meter.finish()
        output["component_events"].append(component_event("siglip2-base-384", siglip["revision"], "ok", siglip_telemetry))
        output["execution_telemetry"].append({"component_id": "siglip2-base-384", **siglip_telemetry})
        return output

    def _capture_entity(self, request: dict) -> dict:
        result = self._egtr(request)
        egtr = self.components["egtr-vg"]
        candidates = {
            f"{index / 100:.2f}": [
                {key: row[key] for key in ("local_id", "category", "bbox", "score")}
                for row in result["objects"] if float(row["score"]) >= index / 100
            ]
            for index in range(101)
        }
        return {
            "score_capture_version": "development-score-capture-v3.3.0",
            "component_provenance": {
                "component_id": "egtr-vg", "revision": egtr["revision"],
                "vocabulary_sha256": result["vocabulary_sha256"],
                "object_vocabulary": result["object_vocabulary"],
                "predicate_vocabulary": result["predicate_vocabulary"],
                "score_domains": result["score_domains"],
            },
            "threshold_independent_objects": result["objects"],
            "entity_candidates": candidates, "relations": result["relations"],
            "component_events": [component_event("egtr-vg", egtr["revision"], "ok", result["telemetry"])],
            "execution_telemetry": [{"component_id": "egtr-vg", **result["telemetry"]}],
        }

    def _capture_downstream(self, request: dict) -> dict:
        image = Image.open(request["image_path"]).convert("RGB")
        detections = request.get("entity_scope")
        if not isinstance(detections, list):
            raise ValueError("downstream calibration requires frozen entity_scope")
        tasks = {task: [] for task in ("colour", "size", "material", "pattern", "scene")}
        siglip = self.components["siglip2-base-384"]
        with Telemetry() as meter:
            for detection in detections:
                crop, category = padded_crop(image, detection["bbox"]), detection["category"]
                crop_info = {"kind": "single_crop", "bbox": detection["bbox"], "padding_fraction": 0.1}
                for task, values in self.contract.base_observation["attributes"].items():
                    labels = list(values)
                    prompts = [f"a photo of a {value} {category}" for value in labels]
                    tasks[task].append(self.scorer.calibration_vector(
                        crop, prompts, labels, {"detection_id": detection["local_id"]}, crop_info,
                    ))
            labels = list(self.contract.base_observation["scenes"])
            tasks["scene"].append(self.scorer.calibration_vector(
                image, [f"a photo taken in a {value}" for value in labels], labels,
                {"image_id": request["image_id"]}, {"kind": "global_image", "size": list(image.size)},
            ))
            telemetry = meter.finish()
        return {
            "score_capture_version": "development-score-capture-v3.3.0",
            "component_provenance": {
                "component_id": "siglip2-base-384", "revision": siglip["revision"],
                "prompt_templates": {
                    "attribute": "a photo of a {attribute_value} {entity_category}",
                    "scene": "a photo taken in a {scene}",
                },
            },
            "entity_scope": detections, "siglip_tasks": tasks,
            "component_events": [component_event("siglip2-base-384", siglip["revision"], "ok", telemetry)],
            "execution_telemetry": [{"component_id": "siglip2-base-384", **telemetry}],
        }

    def close(self) -> None:
        if self.worker.poll() is None and self.worker.stdin is not None:
            self.worker.stdin.close()
            self.worker.wait(timeout=30)


def main() -> int:
    pipeline = Pipeline()
    try:
        return serve(pipeline)
    finally:
        pipeline.close()


if __name__ == "__main__":
    raise SystemExit(main())
