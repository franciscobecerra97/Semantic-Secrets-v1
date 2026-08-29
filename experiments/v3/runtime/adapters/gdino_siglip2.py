"""Frozen `v3.1-gdino-siglip2` persistent bounded-observation adapter."""

from __future__ import annotations

from PIL import Image

from prototype.semantic_secrets.v3 import load_active_contract

from ..telemetry import Telemetry
from .common import MODELS, SiglipScorer, base_observation, component_event, confidence, padded_crop, pair_crop, serve, setting


class Pipeline:
    def __init__(self) -> None:
        import torch
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

        self.torch = torch
        self.contract = load_active_contract()
        self.pipeline_id = "v3.1-gdino-siglip2"
        self.components = self.contract.component_map(self.pipeline_id)
        self.labels = list(self.contract.amend_observation["shared_gate_entity_label_intersection"])
        self.processor = AutoProcessor.from_pretrained(MODELS / "grounding-dino-tiny", local_files_only=True)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(MODELS / "grounding-dino-tiny", local_files_only=True).eval().cuda()
        self.scorer = SiglipScorer()

    def __call__(self, request: dict) -> dict:
        if request["pipeline_id"] != self.pipeline_id:
            raise ValueError("wrong adapter pipeline")
        if request.get("operation") == "calibration_capture_entity":
            return self._capture_entity(request)
        if request.get("operation") == "calibration_capture_downstream":
            return self._capture_downstream(request)
        output = base_observation(request)
        image = Image.open(request["image_path"]).convert("RGB")
        gdino = self.components["grounding-dino-tiny"]
        with Telemetry() as meter:
            inputs = self.processor(images=image, text=". ".join(self.labels) + ".", return_tensors="pt").to("cuda")
            with self.torch.inference_mode():
                raw = self.model(**inputs)
            threshold = setting(request, "entity")
            rows = self.processor.post_process_grounded_object_detection(raw, inputs.input_ids, box_threshold=threshold["threshold"], text_threshold=threshold["threshold"], target_sizes=[image.size[::-1]])[0]
            for index, (box, score, label) in enumerate(zip(rows["boxes"], rows["scores"], rows["text_labels"]), start=1):
                token = str(label).strip().casefold().replace(" ", "_").replace("-", "_")
                if token not in self.labels:
                    continue
                x1, y1, x2, y2 = box.float().cpu().tolist()
                output["detections"].append({"local_id": f"gdino-{index:03d}", "category": token, "bbox": [x1 / image.width, y1 / image.height, x2 / image.width, y2 / image.height], "confidence": confidence(float(score), threshold), "component_id": "grounding-dino-tiny", "component_revision": gdino["revision"]})
            gdino_telemetry = meter.finish()
        output["component_events"].append(component_event("grounding-dino-tiny", gdino["revision"], "ok", gdino_telemetry))
        output["execution_telemetry"].append({"component_id": "grounding-dino-tiny", **gdino_telemetry})

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
                threshold = setting(request, "unary_action")
                values = list(self.contract.base_observation["unary_actions"])
                winner = self.scorer.winner(crop, [f"a photo of a {category} {value}" for value in values], values, threshold)
                if winner:
                    value, score = winner
                    output["unary_actions"].append({"detection_id": detection["local_id"], "action": value, "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
            threshold = setting(request, "binary_interaction")
            values = list(self.contract.base_observation["binary_interactions"])
            for source in output["detections"]:
                for target in output["detections"]:
                    if source is target:
                        continue
                    crop = pair_crop(image, source["bbox"], target["bbox"])
                    prompts = [f"a photo of the red-box {source['category']} {value} the blue-box {target['category']}" for value in values]
                    winner = self.scorer.winner(crop, prompts, values, threshold)
                    if winner:
                        value, score = winner
                        output["binary_interactions"].append({"source_detection_id": source["local_id"], "interaction": value, "target_detection_id": target["local_id"], "confidence": confidence(score, threshold), "component_id": "siglip2-base-384", "component_revision": siglip["revision"]})
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
        image = Image.open(request["image_path"]).convert("RGB")
        gdino = self.components["grounding-dino-tiny"]
        with Telemetry() as meter:
            query = ". ".join(self.labels) + "."
            inputs = self.processor(images=image, text=query, return_tensors="pt").to("cuda")
            with self.torch.inference_mode():
                raw = self.model(**inputs)
            candidates = {}
            for index in range(101):
                threshold = index / 100
                rows = self.processor.post_process_grounded_object_detection(
                    raw, inputs.input_ids, box_threshold=threshold, text_threshold=threshold,
                    target_sizes=[image.size[::-1]],
                )[0]
                detections = []
                for row_index, (box, score, label) in enumerate(zip(rows["boxes"], rows["scores"], rows["text_labels"]), start=1):
                    token = str(label).strip().casefold().replace(" ", "_").replace("-", "_")
                    if token not in self.labels:
                        continue
                    x1, y1, x2, y2 = box.float().cpu().tolist()
                    detections.append({
                        "local_id": f"gdino-{row_index:03d}", "category": token,
                        "bbox": [x1 / image.width, y1 / image.height, x2 / image.width, y2 / image.height],
                        "score": float(score),
                    })
                candidates[f"{threshold:.2f}"] = detections
            telemetry = meter.finish()
        return {
            "score_capture_version": "development-score-capture-v3.3.0",
            "component_provenance": {
                "component_id": "grounding-dino-tiny", "revision": gdino["revision"],
                "query": query, "label_order": self.labels, "processor_class": type(self.processor).__name__,
                "target_size": [image.height, image.width],
            },
            "raw_postprocess_inputs": {
                "logits": raw.logits.detach().float().cpu().tolist(),
                "pred_boxes": raw.pred_boxes.detach().float().cpu().tolist(),
                "input_ids": inputs.input_ids.detach().cpu().tolist(),
            },
            "entity_candidates": candidates,
            "component_events": [component_event("grounding-dino-tiny", gdino["revision"], "ok", telemetry)],
            "execution_telemetry": [{"component_id": "grounding-dino-tiny", **telemetry}],
        }

    def _capture_downstream(self, request: dict) -> dict:
        image = Image.open(request["image_path"]).convert("RGB")
        detections = request.get("entity_scope")
        if not isinstance(detections, list):
            raise ValueError("downstream calibration requires frozen entity_scope")
        tasks = {task: [] for task in ("colour", "size", "material", "pattern", "unary_action", "binary_interaction", "scene")}
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
                labels = list(self.contract.base_observation["unary_actions"])
                prompts = [f"a photo of a {category} {value}" for value in labels]
                tasks["unary_action"].append(self.scorer.calibration_vector(
                    crop, prompts, labels, {"detection_id": detection["local_id"]}, crop_info,
                ))
            labels = list(self.contract.base_observation["binary_interactions"])
            for source in detections:
                for target in detections:
                    if source is target:
                        continue
                    crop = pair_crop(image, source["bbox"], target["bbox"])
                    prompts = [f"a photo of the red-box {source['category']} {value} the blue-box {target['category']}" for value in labels]
                    tasks["binary_interaction"].append(self.scorer.calibration_vector(
                        crop, prompts, labels,
                        {"source_detection_id": source["local_id"], "target_detection_id": target["local_id"]},
                        {"kind": "ordered_pair_crop", "source_bbox": source["bbox"], "target_bbox": target["bbox"], "padding_fraction": 0.1, "source_border": "red-2px", "target_border": "blue-2px"},
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
                    "unary_action": "a photo of a {entity_category} {unary_action}",
                    "binary_interaction": "a photo of the red-box {source_category} {binary_interaction} the blue-box {target_category}",
                    "scene": "a photo taken in a {scene}",
                },
            },
            "entity_scope": detections, "siglip_tasks": tasks,
            "component_events": [component_event("siglip2-base-384", siglip["revision"], "ok", telemetry)],
            "execution_telemetry": [{"component_id": "siglip2-base-384", **telemetry}],
        }


def main() -> int:
    return serve(Pipeline())


if __name__ == "__main__":
    raise SystemExit(main())
