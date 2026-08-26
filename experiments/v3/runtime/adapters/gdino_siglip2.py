"""Frozen `v3.1-gdino-siglip2` bounded-observation adapter."""

from __future__ import annotations

from PIL import Image

from prototype.semantic_secrets.v3 import load_active_contract

from ..telemetry import Telemetry
from .common import MODELS, SiglipScorer, base_observation, component_event, confidence, emit, padded_crop, pair_crop, read_request, setting


def main() -> int:
    import torch
    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

    request = read_request()
    if request["pipeline_id"] != "v3.1-gdino-siglip2":
        raise SystemExit("wrong adapter pipeline")
    contract = load_active_contract()
    components = contract.component_map(request["pipeline_id"])
    output = base_observation(request)
    image = Image.open(request["image_path"]).convert("RGB")
    labels = list(contract.amend_observation["shared_gate_entity_label_intersection"])

    gdino = components["grounding-dino-tiny"]
    with Telemetry() as meter:
        processor = AutoProcessor.from_pretrained(MODELS / "grounding-dino-tiny", local_files_only=True)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(MODELS / "grounding-dino-tiny", local_files_only=True).eval().cuda()
        query = ". ".join(labels) + "."
        inputs = processor(images=image, text=query, return_tensors="pt").to("cuda")
        with torch.inference_mode():
            raw = model(**inputs)
        threshold = setting(request, "entity")
        rows = processor.post_process_grounded_object_detection(
            raw, inputs.input_ids,
            box_threshold=threshold["threshold"], text_threshold=threshold["threshold"],
            target_sizes=[image.size[::-1]],
        )[0]
        detections = []
        for index, (box, score, label) in enumerate(zip(rows["boxes"], rows["scores"], rows["text_labels"]), start=1):
            token = str(label).strip().casefold().replace(" ", "_").replace("-", "_")
            if token not in labels:
                continue
            x1, y1, x2, y2 = box.float().cpu().tolist()
            bbox = [x1 / image.width, y1 / image.height, x2 / image.width, y2 / image.height]
            detections.append({"local_id": f"gdino-{index:03d}", "category": token, "bbox": bbox, "confidence": confidence(float(score), threshold), "component_id": "grounding-dino-tiny", "component_revision": gdino["revision"]})
        output["detections"] = detections
        gdino_telemetry = meter.finish()
    output["component_events"].append(component_event("grounding-dino-tiny", gdino["revision"], "ok", gdino_telemetry))
    output["execution_telemetry"].append({"component_id": "grounding-dino-tiny", **gdino_telemetry})
    del model, processor, raw, inputs
    torch.cuda.empty_cache()

    siglip = components["siglip2-base-384"]
    with Telemetry() as meter:
        scorer = SiglipScorer()
        for detection in output["detections"]:
            crop = padded_crop(image, detection["bbox"])
            category = detection["category"]
            for atom_type, values in contract.base_observation["attributes"].items():
                threshold = setting(request, atom_type)
                winner = scorer.winner(crop, [f"a photo of a {value} {category}" for value in values], list(values), threshold)
                if winner:
                    value, score = winner
                    output["attributes"].append({"detection_id": detection["local_id"], "attribute_type": atom_type, "value": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
            threshold = setting(request, "unary_action")
            values = list(contract.base_observation["unary_actions"])
            winner = scorer.winner(crop, [f"a photo of a {category} {value}" for value in values], values, threshold)
            if winner:
                value, score = winner
                output["unary_actions"].append({"detection_id": detection["local_id"], "action": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
        threshold = setting(request, "binary_interaction")
        values = list(contract.base_observation["binary_interactions"])
        for source in output["detections"]:
            for target in output["detections"]:
                if source is target:
                    continue
                crop = pair_crop(image, source["bbox"], target["bbox"])
                prompts = [f"a photo of the red-box {source['category']} {value} the blue-box {target['category']}" for value in values]
                winner = scorer.winner(crop, prompts, values, threshold)
                if winner:
                    value, score = winner
                    output["binary_interactions"].append({"source_detection_id": source["local_id"], "interaction": value, "target_detection_id": target["local_id"], "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
        threshold = setting(request, "scene")
        values = list(contract.base_observation["scenes"])
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
