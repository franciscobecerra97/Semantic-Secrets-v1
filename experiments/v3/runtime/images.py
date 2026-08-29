"""Frozen-config capability-image materialization.

Controlled images are deterministic renderings of already-authored scenario
specifications. Naturalistic images use only the exact SD-Turbo configuration
from preregistration_v3.json. Neither path consults perception outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

from prototype.semantic_secrets.v3 import load_active_contract

from .acquire import inventory
from .dataset import audit_scenario_specification
from .io import atomic_write, canonical_bytes, read_json, sha256_file


def _scenario_files(directory: Path, stratum: str) -> list[tuple[Path, dict[str, Any]]]:
    rows = []
    for path in sorted(directory.glob("*.json")):
        value = read_json(path)
        audit_scenario_specification(value)
        if value["stratum"] == stratum:
            rows.append((path, value))
    return rows


def render_controlled(scenarios: Path, render_plan_path: Path, asset_root: Path, output: Path) -> dict[str, Any]:
    rows = _scenario_files(scenarios, "A_controlled_geometric")
    if len(rows) != 120:
        raise ValueError(f"controlled rendering requires 120 final scenario specifications, found {len(rows)}")
    render_plan = read_json(render_plan_path)
    plan_rows = {row["image_id"]: row for row in render_plan.get("images", [])}
    expected = {scenario["image_id"] for _, scenario in rows}
    if set(plan_rows) != expected or render_plan.get("licence") != "project-authored":
        raise ValueError("controlled render plan must cover exactly the 120 A images with project-authored assets")
    output.mkdir(parents=True, exist_ok=True)
    for _, scenario in rows:
        destination = output / f"{scenario['image_id']}.png"
        if destination.exists():
            raise ValueError(f"controlled image already exists: {destination}")
        plan = plan_rows[scenario["image_id"]]
        assets = {row["reference_id"]: row for row in plan.get("assets", [])}
        if set(assets) != {row["reference_id"] for row in scenario["reference_entities"]}:
            raise ValueError(f"controlled render assets do not match scenario entities: {scenario['image_id']}")
        background = plan.get("background_rgba", [238, 238, 238, 255])
        if not isinstance(background, list) or len(background) != 4 or any(not isinstance(value, int) or not 0 <= value <= 255 for value in background):
            raise ValueError(f"invalid controlled background RGBA: {scenario['image_id']}")
        image = Image.new("RGBA", (512, 512), tuple(background))
        for entity in sorted(scenario["reference_entities"], key=lambda row: row["reference_id"]):
            box = tuple(round(value * 512) for value in entity["bbox_xyxy"])
            if box[2] <= box[0] or box[3] <= box[1]:
                raise ValueError(f"controlled entity rounds to an empty pixel box: {scenario['image_id']}/{entity['reference_id']}")
            asset_record = assets[entity["reference_id"]]
            asset = (asset_root / asset_record["relative_path"]).resolve()
            if asset_root.resolve() not in asset.parents or not asset.is_file() or sha256_file(asset) != asset_record.get("sha256"):
                raise ValueError(f"controlled asset provenance mismatch: {scenario['image_id']}/{entity['reference_id']}")
            sprite = Image.open(asset).convert("RGBA").resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
            image.alpha_composite(sprite, (box[0], box[1]))
        image.convert("RGB").save(destination, format="PNG", optimize=False, compress_level=9)
    return {"images": len(rows), "render_plan_sha256": sha256_file(render_plan_path), "output": str(output)}


def generate_naturalistic(prompt_plan: Path, model: Path, generator_manifest: Path, output: Path, receipt: Path, resume: bool = False) -> dict[str, Any]:
    import torch
    from diffusers import AutoPipelineForText2Image

    contract = load_active_contract()
    frozen = contract.base_prereg["dataset"]["strata"]["B_naturalistic_t2i"]["generator"]
    plan = read_json(prompt_plan)
    rows = plan.get("images") if isinstance(plan, dict) else None
    expected_ids = [f"cap-v3-B-F{family:02d}-{image:02d}" for family in range(1, 25) for image in range(1, 6)]
    if not isinstance(rows, list) or sorted(row.get("image_id") for row in rows) != expected_ids:
        raise ValueError("naturalistic prompt plan must contain every deterministic B-stratum image ID exactly once")
    if plan.get("model_id") != frozen["model_id"] or plan.get("revision") != frozen["revision"] or plan.get("seed_rule") != frozen["seed_rule"]:
        raise ValueError("naturalistic prompt plan does not declare the frozen generator/revision/seed rule")
    if not model.is_dir():
        raise ValueError("verified local SD-Turbo snapshot is missing")
    provenance = read_json(generator_manifest)
    recorded_files = [
        {key: row[key] for key in ("relative_path", "bytes", "sha256")}
        for row in provenance.get("files", []) if isinstance(row, dict) and all(key in row for key in ("relative_path", "bytes", "sha256"))
    ]
    if any((
        provenance.get("schema_version") != "generator-acquisition-v3.0.0",
        provenance.get("component_id") != "sd-turbo",
        provenance.get("model_id") != frozen["model_id"],
        provenance.get("revision") != frozen["revision"],
        provenance.get("verified") is not True,
        recorded_files != inventory(model),
    )):
        raise ValueError("SD-Turbo local snapshot does not match its exact-revision acquisition inventory")
    output.mkdir(parents=True, exist_ok=True)
    base_receipt = {
        "schema_version": "sd-turbo-generation-receipt-v3.0.0", "status": "partial",
        "images": 0, "model_id": frozen["model_id"], "revision": frozen["revision"],
        "generation_config": {key: frozen[key] for key in ("width", "height", "steps", "guidance_scale")},
        "generator_manifest_sha256": sha256_file(generator_manifest),
        "prompt_plan_sha256": sha256_file(prompt_plan), "image_files": [],
    }
    if receipt.exists():
        if not resume:
            raise ValueError("naturalistic generation receipt already exists; use an explicit verified --resume")
        prior = read_json(receipt)
        for key in ("schema_version", "model_id", "revision", "generation_config", "generator_manifest_sha256", "prompt_plan_sha256"):
            if prior.get(key) != base_receipt[key]:
                raise ValueError(f"naturalistic resume receipt mismatch for {key}")
        recorded = {row["image_id"]: row["sha256"] for row in prior.get("image_files", [])}
    else:
        recorded = {}
        atomic_write(receipt, canonical_bytes(base_receipt))
    pipeline = AutoPipelineForText2Image.from_pretrained(model, local_files_only=True, torch_dtype=torch.float16).to("cuda")
    for row in sorted(rows, key=lambda item: item["image_id"]):
        if not isinstance(row.get("prompt"), str) or not row["prompt"].strip() or not isinstance(row.get("seed"), int):
            raise ValueError(f"invalid frozen prompt/seed for {row.get('image_id')}")
        destination = output / f"{row['image_id']}.png"
        if destination.exists():
            if not resume or recorded.get(row["image_id"]) != sha256_file(destination):
                raise ValueError(f"unverified naturalistic image already exists: {destination}")
            continue
        generator = torch.Generator(device="cuda").manual_seed(row["seed"])
        result = pipeline(
            prompt=row["prompt"], width=int(frozen["width"]), height=int(frozen["height"]),
            num_inference_steps=int(frozen["steps"]), guidance_scale=float(frozen["guidance_scale"]),
            generator=generator,
        ).images[0]
        result.save(destination, format="PNG", optimize=False, compress_level=9)
        recorded[row["image_id"]] = sha256_file(destination)
        atomic_write(receipt, canonical_bytes({**base_receipt, "images": len(recorded), "image_files": [{"image_id": key, "sha256": recorded[key]} for key in sorted(recorded)]}))
    value = {
        **base_receipt, "status": "complete",
        "images": len(rows), "model_id": frozen["model_id"], "revision": frozen["revision"],
        "image_files": [
            {"image_id": row["image_id"], "sha256": sha256_file(output / f"{row['image_id']}.png")}
            for row in sorted(rows, key=lambda item: item["image_id"])
        ],
    }
    atomic_write(receipt, canonical_bytes(value))
    return {**value, "receipt": str(receipt), "receipt_sha256": sha256_file(receipt)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    controlled = sub.add_parser("controlled")
    controlled.add_argument("--scenarios", type=Path, required=True)
    controlled.add_argument("--render-plan", type=Path, required=True)
    controlled.add_argument("--asset-root", type=Path, required=True)
    controlled.add_argument("--output", type=Path, required=True)
    naturalistic = sub.add_parser("naturalistic")
    naturalistic.add_argument("--prompt-plan", type=Path, required=True)
    naturalistic.add_argument("--model", type=Path, required=True)
    naturalistic.add_argument("--generator-manifest", type=Path, required=True)
    naturalistic.add_argument("--output", type=Path, required=True)
    naturalistic.add_argument("--receipt", type=Path, required=True)
    naturalistic.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    value = render_controlled(args.scenarios, args.render_plan, args.asset_root, args.output) if args.command == "controlled" else generate_naturalistic(args.prompt_plan, args.model, args.generator_manifest, args.output, args.receipt, args.resume)
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
