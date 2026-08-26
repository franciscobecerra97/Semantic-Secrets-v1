"""Legacy-environment EGTR tensor adapter.

All architecture, transform, and category resources must exist locally inside
the reviewed artifact. Missing provenance fails closed; the worker never
contacts a model hub.
"""

from __future__ import annotations

import glob
import json
import os
import sys
import time
from pathlib import Path


def main() -> int:
    request = json.load(sys.stdin)
    repository = Path(os.environ.get("EGTR_REPOSITORY", "/opt/egtr"))
    artifact = Path(os.environ.get("SEMANTIC_SECRETS_MODELS", "/workspace/models")) / "egtr-vg"
    sys.path.insert(0, str(repository))

    import psutil
    import torch
    from PIL import Image
    from model.deformable_detr import DeformableDetrConfig, DeformableDetrFeatureExtractor
    from model.egtr import DetrForSceneGraphGeneration

    required = [artifact / "config.json", artifact / "feature_extractor" / "preprocessor_config.json", artifact / "base_model" / "config.json"]
    if not all(path.is_file() for path in required):
        raise RuntimeError("EGTR artifact lacks local config/transform/base-model provenance; implicit downloads are forbidden")
    checkpoints = sorted(glob.glob(str(artifact / "checkpoints" / "epoch=*.ckpt")))
    if len(checkpoints) != 1:
        raise RuntimeError("EGTR checkpoint identity is ambiguous; exactly one reviewed epoch checkpoint is required")

    started = time.perf_counter()
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    config = DeformableDetrConfig.from_pretrained(str(artifact), local_files_only=True)
    id2label = getattr(config, "id2label", None)
    id2relation = getattr(config, "id2relation", None) or getattr(config, "rel_categories", None)
    if not isinstance(id2label, dict) or not isinstance(id2relation, (dict, list)):
        raise RuntimeError("EGTR artifact lacks exact object/relation vocabulary metadata")
    extractor = DeformableDetrFeatureExtractor.from_pretrained(str(artifact / "feature_extractor"), local_files_only=True)
    model = DetrForSceneGraphGeneration.from_pretrained(
        str(artifact / "base_model"), config=config, ignore_mismatched_sizes=True, local_files_only=True
    )
    state = torch.load(checkpoints[0], map_location="cpu")
    if "state_dict" not in state:
        raise RuntimeError("EGTR checkpoint lacks the official state_dict wrapper")
    translated = {key[6:] if key.startswith("model.") else key: value for key, value in state["state_dict"].items()}
    model.load_state_dict(translated, strict=True)
    model.eval().cuda()
    image = Image.open(request["image_path"]).convert("RGB")
    inputs = extractor(images=image, return_tensors="pt")
    pixel_mask = inputs.get("pixel_mask")
    with torch.inference_mode():
        output = model(
            pixel_values=inputs["pixel_values"].cuda(),
            pixel_mask=pixel_mask.cuda() if pixel_mask is not None else None,
            output_attentions=False, output_attention_states=True, output_hidden_states=True,
        )

    entity_setting = request["thresholds"]["entity"]
    predicate_setting = request["thresholds"]["predicate"]
    connectivity_setting = request["thresholds"]["connectivity"]
    allowed_entities = set(request["allowed_entities"])
    allowed_predicates = set(request["allowed_predicates"])
    scores, labels = output.logits.softmax(-1)[0].max(-1)
    objects, retained = [], {}
    for query, (score, label_index, box) in enumerate(zip(scores, labels, output.pred_boxes[0])):
        label = str(id2label.get(int(label_index), id2label.get(str(int(label_index)), ""))).strip().casefold().replace(" ", "_").replace("-", "_")
        if label not in allowed_entities or float(score) < entity_setting["threshold"]:
            continue
        cx, cy, width, height = [float(value) for value in box]
        bbox = [max(0.0, cx - width / 2), max(0.0, cy - height / 2), min(1.0, cx + width / 2), min(1.0, cy + height / 2)]
        local_id = f"egtr-q{query:03d}"
        retained[query] = local_id
        objects.append({"local_id": local_id, "category": label, "bbox": bbox, "score": float(score)})
    interactions = []
    for source_query, source_id in retained.items():
        for target_query, target_id in retained.items():
            if source_query == target_query:
                continue
            connectivity = float(output.pred_connectivity[0, source_query, target_query, 0])
            if connectivity < connectivity_setting["threshold"]:
                continue
            relation_score, relation_index = output.pred_rel[0, source_query, target_query].max(-1)
            relation = id2relation[int(relation_index)] if isinstance(id2relation, list) else id2relation.get(int(relation_index), id2relation.get(str(int(relation_index)), ""))
            relation = str(relation).strip().casefold().replace(" ", "_").replace("-", "_")
            if relation in allowed_predicates and float(relation_score) >= predicate_setting["threshold"]:
                interactions.append({"source_detection_id": source_id, "target_detection_id": target_id, "interaction": relation, "predicate_score": float(relation_score), "connectivity_score": connectivity})
    torch.cuda.synchronize()
    telemetry = {
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "peak_process_rss_bytes": psutil.Process().memory_info().rss,
        "framework_peak_gpu_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "framework_peak_gpu_reserved_bytes": int(torch.cuda.max_memory_reserved()),
    }
    print(json.dumps({"detections": objects, "binary_interactions": interactions, "telemetry": telemetry}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
