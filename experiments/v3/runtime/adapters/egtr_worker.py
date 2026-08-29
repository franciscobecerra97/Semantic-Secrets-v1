"""Persistent legacy-environment EGTR tensor adapter."""

from __future__ import annotations

import glob
import json
import os
import sys
import time
import hashlib
from pathlib import Path


class Worker:
    def __init__(self) -> None:
        repository = Path(os.environ.get("EGTR_REPOSITORY", "/opt/egtr"))
        artifact = Path(os.environ.get("SEMANTIC_SECRETS_MODELS", "/workspace/models")) / "egtr-vg"
        sys.path.insert(0, str(repository))
        import psutil
        import torch
        from model.deformable_detr import DeformableDetrConfig, DeformableDetrFeatureExtractor
        from model.egtr import DetrForSceneGraphGeneration

        self.psutil, self.torch = psutil, torch
        required = [artifact / "config.json", artifact / "feature_extractor" / "preprocessor_config.json", artifact / "base_model" / "config.json"]
        if not all(path.is_file() for path in required):
            raise RuntimeError("EGTR artifact lacks local config/transform/base-model provenance; implicit downloads are forbidden")
        checkpoints = sorted(glob.glob(str(artifact / "checkpoints" / "epoch=*.ckpt")))
        if len(checkpoints) != 1:
            raise RuntimeError("EGTR checkpoint identity is ambiguous; exactly one reviewed epoch checkpoint is required")
        self.config = DeformableDetrConfig.from_pretrained(str(artifact), local_files_only=True)
        self.id2label = getattr(self.config, "id2label", None)
        self.id2relation = getattr(self.config, "id2relation", None) or getattr(self.config, "rel_categories", None)
        if not isinstance(self.id2label, dict) or not isinstance(self.id2relation, (dict, list)):
            raise RuntimeError("EGTR artifact lacks exact object/relation vocabulary metadata")
        self.extractor = DeformableDetrFeatureExtractor.from_pretrained(str(artifact / "feature_extractor"), local_files_only=True)
        self.model = DetrForSceneGraphGeneration.from_pretrained(str(artifact / "base_model"), config=self.config, ignore_mismatched_sizes=True, local_files_only=True)
        state = torch.load(checkpoints[0], map_location="cpu")
        if "state_dict" not in state:
            raise RuntimeError("EGTR checkpoint lacks the official state_dict wrapper")
        translated = {key[6:] if key.startswith("model.") else key: value for key, value in state["state_dict"].items()}
        self.model.load_state_dict(translated, strict=True)
        self.model.eval().cuda()

    def __call__(self, request: dict) -> dict:
        from PIL import Image

        started = time.perf_counter()
        self.torch.cuda.synchronize()
        self.torch.cuda.reset_peak_memory_stats()
        image = Image.open(request["image_path"]).convert("RGB")
        inputs = self.extractor(images=image, return_tensors="pt")
        pixel_mask = inputs.get("pixel_mask")
        with self.torch.inference_mode():
            output = self.model(pixel_values=inputs["pixel_values"].cuda(), pixel_mask=pixel_mask.cuda() if pixel_mask is not None else None, output_attentions=False, output_attention_states=True, output_hidden_states=True)
        if request.get("operation") == "calibration_capture_entity":
            allowed_entities, allowed_predicates = set(request["allowed_entities"]), set(request["allowed_predicates"])
            scores, labels = output.logits.softmax(-1)[0].max(-1)
            objects = []
            for query, (score, label_index, box) in enumerate(zip(scores, labels, output.pred_boxes[0])):
                label = str(self.id2label.get(int(label_index), self.id2label.get(str(int(label_index)), ""))).strip().casefold().replace(" ", "_").replace("-", "_")
                if label not in allowed_entities:
                    continue
                cx, cy, width, height = [float(value) for value in box]
                objects.append({
                    "local_id": f"egtr-q{query:03d}", "query_index": query,
                    "category": label, "score": float(score),
                    "bbox": [max(0.0, cx - width / 2), max(0.0, cy - height / 2), min(1.0, cx + width / 2), min(1.0, cy + height / 2)],
                })
            relations = []
            for source in objects:
                for target in objects:
                    if source["query_index"] == target["query_index"]:
                        continue
                    source_query, target_query = source["query_index"], target["query_index"]
                    relation_score, relation_index = output.pred_rel[0, source_query, target_query].max(-1)
                    relation = self.id2relation[int(relation_index)] if isinstance(self.id2relation, list) else self.id2relation.get(int(relation_index), self.id2relation.get(str(int(relation_index)), ""))
                    relation = str(relation).strip().casefold().replace(" ", "_").replace("-", "_")
                    if relation not in allowed_predicates:
                        continue
                    relations.append({
                        "source_detection_id": source["local_id"], "target_detection_id": target["local_id"],
                        "interaction": relation, "predicate_score": float(relation_score),
                        "connectivity_score": float(output.pred_connectivity[0, source_query, target_query, 0]),
                    })
            self.torch.cuda.synchronize()
            telemetry = {
                "elapsed_seconds": round(time.perf_counter() - started, 6),
                "peak_process_rss_bytes": self.psutil.Process().memory_info().rss,
                "framework_peak_gpu_allocated_bytes": int(self.torch.cuda.max_memory_allocated()),
                "framework_peak_gpu_reserved_bytes": int(self.torch.cuda.max_memory_reserved()),
            }
            vocabulary = json.dumps({"objects": self.id2label, "relations": self.id2relation}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            return {
                "objects": objects, "relations": relations, "telemetry": telemetry,
                "vocabulary_sha256": hashlib.sha256(vocabulary).hexdigest(),
                "object_vocabulary": self.id2label, "predicate_vocabulary": self.id2relation,
                "score_domains": {"entity": "egtr_object_softmax", "predicate": "egtr_relation_sigmoid", "connectivity": "egtr_connectivity_sigmoid"},
            }
        entity_setting, predicate_setting = request["thresholds"]["entity"], request["thresholds"]["predicate"]
        connectivity_setting = request["thresholds"]["connectivity"]
        allowed_entities, allowed_predicates = set(request["allowed_entities"]), set(request["allowed_predicates"])
        scores, labels = output.logits.softmax(-1)[0].max(-1)
        objects, retained = [], {}
        for query, (score, label_index, box) in enumerate(zip(scores, labels, output.pred_boxes[0])):
            label = str(self.id2label.get(int(label_index), self.id2label.get(str(int(label_index)), ""))).strip().casefold().replace(" ", "_").replace("-", "_")
            if label not in allowed_entities or float(score) < entity_setting["threshold"]:
                continue
            cx, cy, width, height = [float(value) for value in box]
            local_id = f"egtr-q{query:03d}"
            retained[query] = local_id
            objects.append({"local_id": local_id, "category": label, "bbox": [max(0.0, cx - width / 2), max(0.0, cy - height / 2), min(1.0, cx + width / 2), min(1.0, cy + height / 2)], "score": float(score)})
        interactions = []
        for source_query, source_id in retained.items():
            for target_query, target_id in retained.items():
                if source_query == target_query:
                    continue
                connectivity = float(output.pred_connectivity[0, source_query, target_query, 0])
                if connectivity < connectivity_setting["threshold"]:
                    continue
                relation_score, relation_index = output.pred_rel[0, source_query, target_query].max(-1)
                relation = self.id2relation[int(relation_index)] if isinstance(self.id2relation, list) else self.id2relation.get(int(relation_index), self.id2relation.get(str(int(relation_index)), ""))
                relation = str(relation).strip().casefold().replace(" ", "_").replace("-", "_")
                if relation in allowed_predicates and float(relation_score) >= predicate_setting["threshold"]:
                    interactions.append({"source_detection_id": source_id, "target_detection_id": target_id, "interaction": relation, "predicate_score": float(relation_score), "connectivity_score": connectivity})
        self.torch.cuda.synchronize()
        telemetry = {
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            "peak_process_rss_bytes": self.psutil.Process().memory_info().rss,
            "framework_peak_gpu_allocated_bytes": int(self.torch.cuda.max_memory_allocated()),
            "framework_peak_gpu_reserved_bytes": int(self.torch.cuda.max_memory_reserved()),
        }
        return {"detections": objects, "binary_interactions": interactions, "telemetry": telemetry}


def main() -> int:
    worker = Worker()
    for line in sys.stdin.buffer:
        if line.strip():
            print(json.dumps(worker(json.loads(line)), sort_keys=True, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
