"""Generate and validate deterministic, label-separated concept manifests.

This P3 tool uses only the Python standard library. It writes metadata manifests;
it does not download public data, generate images, or run AI models.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
DESIGN_PATH = ROOT / "config" / "design_v1.json"
OUTPUT_ROOT = ROOT / "manifests"
ATOM_FIELD_ORDER = ("type", "id", "subject", "value", "object", "object2", "subtype")
EXECUTION_FIELDS = {
    "row_id",
    "stage",
    "pathway",
    "core_prompt",
    "render_prompt",
    "prompt_variant",
    "generator_seed",
    "style_id",
    "layout_id",
    "generator_slot",
    "extractor_slot",
    "text_input_id",
    "design_version",
}
TEXT_INPUT_FIELDS = {
    "text_input_id",
    "stage",
    "pathway",
    "core_prompt",
    "prompt_variant",
    "extractor_slot",
    "design_version",
}
LABEL_FIELDS = {
    "row_id",
    "family_id",
    "concept_id",
    "base_concept_id",
    "split",
    "trial_role",
    "relationship_to_base",
    "complexity_level",
    "frequency_band",
    "expected_atoms",
    "changed_atom_type",
    "source_id",
    "catalog_version",
    "ontology_version",
}
PAIR_FIELDS = {
    "pair_id",
    "anchor_row_id",
    "candidate_row_id",
    "split",
    "relationship",
    "family_id",
    "candidate_family_id",
    "changed_atom_type",
}
FORBIDDEN_EXECUTION_FIELDS = {
    "family_id",
    "concept_id",
    "base_concept_id",
    "split",
    "trial_role",
    "relationship_to_base",
    "complexity_level",
    "frequency_band",
    "expected_atoms",
    "changed_atom_type",
}


class DesignError(ValueError):
    """Raised when a frozen dataset-design invariant is violated."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise DesignError(f"Expected JSON object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_json(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def opaque_id(prefix: str, value: Any) -> str:
    return f"{prefix}_{hash_json(value)[:24]}"


def atom_signature(atom: dict[str, Any]) -> str:
    parts = [str(atom["type"])]
    for key in ATOM_FIELD_ORDER[1:]:
        if key in atom:
            parts.append(f"{key}={atom[key]}")
    return "|".join(parts)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DesignError(message)


def _validate_with_jsonschema(instance: Any, schema_path: Path) -> str:
    """Use jsonschema when installed; strict manual checks still run regardless."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return "manual-fallback"
    schema = read_json(schema_path)
    jsonschema.Draft202012Validator(schema).validate(instance)
    return "draft-2020-12"


def validate_catalog(
    catalog: dict[str, Any], ontology: dict[str, Any], expected_families: int
) -> dict[str, Any]:
    schema_mode = _validate_with_jsonschema(catalog, ROOT / "schema" / "concept.schema.json")
    _require(catalog.get("audit_status") == "blind-audit-complete", "Catalog audit is not complete")
    _require(catalog.get("ontology_id") == ontology.get("ontology_id"), "Ontology ID mismatch")

    families = catalog.get("families")
    _require(isinstance(families, list), "families must be a list")
    _require(len(families) == expected_families, "Unexpected family count")

    family_ids: set[str] = set()
    concept_ids: set[str] = set()
    atom_types: set[str] = set()
    complexities: set[int] = set()
    bands: set[str] = set()
    neighbour_changes: Counter[str] = Counter()

    atom_specs = ontology["atom_types"]
    allowed_types = set(atom_specs)
    allowed_bands = set(ontology["frequency_bands"]["values"])

    for family in families:
        family_id = family["family_id"]
        _require(family_id not in family_ids, f"Duplicate family ID: {family_id}")
        family_ids.add(family_id)
        complexities.add(family["complexity_level"])
        bands.add(family["frequency_band"])
        _require(family["frequency_band"] in allowed_bands, f"Invalid band in {family_id}")

        concepts = [family["base"], *family["near_neighbours"]]
        for concept in concepts:
            concept_id = concept["concept_id"]
            _require(concept_id not in concept_ids, f"Duplicate concept ID: {concept_id}")
            concept_ids.add(concept_id)
            prompts = concept["prompts"]
            _require(set(prompts) == {"canonical", "paraphrase_1", "paraphrase_2"}, f"Prompt variants incomplete: {concept_id}")
            _require(len(set(prompts.values())) == 3, f"Duplicate paraphrase: {concept_id}")

            objects = {atom["id"] for atom in concept["atoms"] if atom["type"] == "object"}
            signatures: set[str] = set()
            for atom in concept["atoms"]:
                atom_type = atom["type"]
                _require(atom_type in allowed_types, f"Unknown atom type in {concept_id}: {atom_type}")
                atom_types.add(atom_type)
                for required in atom_specs[atom_type]["required_fields"]:
                    _require(required in atom, f"Missing {required} in {concept_id} atom")
                for reference in ("subject", "object", "object2"):
                    if reference in atom:
                        _require(atom[reference] in objects, f"Broken {reference} in {concept_id}: {atom[reference]}")
                if "allowed_values" in atom_specs[atom_type]:
                    _require(atom["value"] in atom_specs[atom_type]["allowed_values"], f"Invalid value in {concept_id}: {atom['value']}")
                signature = atom_signature(atom)
                _require(signature not in signatures, f"Duplicate atom in {concept_id}: {signature}")
                signatures.add(signature)

        base_signatures = {atom_signature(atom) for atom in family["base"]["atoms"]}
        for neighbour in family["near_neighbours"]:
            near_signatures = {atom_signature(atom) for atom in neighbour["atoms"]}
            removed = base_signatures - near_signatures
            added = near_signatures - base_signatures
            change = neighbour["change"]
            _require(len(removed) == 1 and len(added) == 1, f"Near neighbour is not one replacement: {neighbour['concept_id']}")
            _require(removed == {change["from_signature"]}, f"from_signature mismatch: {neighbour['concept_id']}")
            _require(added == {change["to_signature"]}, f"to_signature mismatch: {neighbour['concept_id']}")
            removed_type = next(iter(removed)).split("|", 1)[0]
            added_type = next(iter(added)).split("|", 1)[0]
            _require(removed_type == added_type == change["atom_type"], f"Atom type mismatch: {neighbour['concept_id']}")
            neighbour_changes[change["atom_type"]] += 1

    _require(atom_types == allowed_types, f"Atom coverage mismatch: {sorted(atom_types)}")
    _require(complexities == {1, 2, 3, 4, 5}, f"Complexity coverage mismatch: {sorted(complexities)}")
    _require(bands == allowed_bands, f"Frequency-band coverage mismatch: {sorted(bands)}")

    return {
        "schema_validation": schema_mode,
        "families": len(families),
        "concepts": len(concept_ids),
        "atom_types": sorted(atom_types),
        "complexities": sorted(complexities),
        "frequency_bands": sorted(bands),
        "near_neighbour_change_counts": dict(sorted(neighbour_changes.items())),
    }


def assign_splits(families: list[dict[str, Any]], stage: dict[str, Any]) -> dict[str, str]:
    counts = stage["split_counts"]
    _require(sum(counts.values()) == len(families), "Split quotas do not sum to family count")
    seed = stage["split_seed"]
    ordered = sorted(
        (family["family_id"] for family in families),
        key=lambda family_id: hashlib.sha256(f"{seed}\0{family_id}".encode()).hexdigest(),
    )
    result: dict[str, str] = {}
    cursor = 0
    for split in ("train", "validation", "test"):
        for family_id in ordered[cursor : cursor + counts[split]]:
            result[family_id] = split
        cursor += counts[split]
    return result


def _render_prompt(core: str, style_text: str, layout_text: str) -> str:
    return f"{core} Rendering instruction: {style_text}. Composition instruction: {layout_text}."


def build_manifests(
    stage_name: str,
    design: dict[str, Any],
    ontology: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    stage = design["stages"][stage_name]
    splits = assign_splits(catalog["families"], stage)
    inputs: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    text_inputs: dict[str, dict[str, Any]] = {}
    row_lookup: dict[tuple[str, str], list[str]] = defaultdict(list)
    row_labels: dict[str, dict[str, Any]] = {}

    seeds = stage["generator_seeds"]
    prompt_variants = stage["prompt_variants"]
    styles = stage["styles"]
    layouts = stage["layouts"]
    models = stage["generator_slots"]

    def emit(
        family: dict[str, Any],
        concept: dict[str, Any],
        role: str,
        relationship: str,
        prompt_variant: str,
        seed: int,
        style: str,
        layout: str,
        model: str,
        changed_atom_type: str | None,
    ) -> None:
        core = concept["prompts"][prompt_variant]
        text_payload = {
            "stage": stage_name,
            "core_prompt": core,
            "prompt_variant": prompt_variant,
            "design_version": design["design_id"],
        }
        text_input_id = opaque_id("t", text_payload)
        text_inputs[text_input_id] = {
            "text_input_id": text_input_id,
            "stage": stage_name,
            "pathway": "text",
            "core_prompt": core,
            "prompt_variant": prompt_variant,
            "extractor_slot": stage["extractor_slot"],
            "design_version": design["design_id"],
        }
        identity = {
            "stage": stage_name,
            "family_id": family["family_id"],
            "concept_id": concept["concept_id"],
            "role": role,
            "prompt_variant": prompt_variant,
            "seed": seed,
            "style": style,
            "layout": layout,
            "model": model,
            "design_version": design["design_id"],
        }
        row_id = opaque_id("r", identity)
        input_row = {
            "row_id": row_id,
            "stage": stage_name,
            "pathway": "image",
            "core_prompt": core,
            "render_prompt": _render_prompt(core, ontology["styles"][style], ontology["layouts"][layout]),
            "prompt_variant": prompt_variant,
            "generator_seed": seed,
            "style_id": style,
            "layout_id": layout,
            "generator_slot": model,
            "extractor_slot": stage["extractor_slot"],
            "text_input_id": text_input_id,
            "design_version": design["design_id"],
        }
        label_row = {
            "row_id": row_id,
            "family_id": family["family_id"],
            "concept_id": concept["concept_id"],
            "base_concept_id": family["base"]["concept_id"],
            "split": splits[family["family_id"]],
            "trial_role": role,
            "relationship_to_base": relationship,
            "complexity_level": family["complexity_level"],
            "frequency_band": family["frequency_band"],
            "expected_atoms": concept["atoms"],
            "changed_atom_type": changed_atom_type,
            "source_id": "controlled_v1",
            "catalog_version": catalog["catalog_id"],
            "ontology_version": ontology["ontology_id"],
        }
        inputs.append(input_row)
        labels.append(label_row)
        row_lookup[(family["family_id"], role)].append(row_id)
        row_labels[row_id] = label_row

    for family in catalog["families"]:
        base = family["base"]
        neutral = (prompt_variants[0], seeds[0], styles[0], layouts[0], models[0])
        emit(family, base, "enrolment", "same", *neutral, None)
        for seed in seeds[1:]:
            emit(family, base, "seed", "same", prompt_variants[0], seed, styles[0], layouts[0], models[0], None)
        for prompt_variant in prompt_variants[1:]:
            emit(family, base, "paraphrase", "same", prompt_variant, seeds[0], styles[0], layouts[0], models[0], None)
        for style in styles[1:]:
            emit(family, base, "style", "same", prompt_variants[0], seeds[0], style, layouts[0], models[0], None)
        for layout in layouts[1:]:
            emit(family, base, "layout", "same", prompt_variants[0], seeds[0], styles[0], layout, models[0], None)
        for model in models[1:]:
            emit(family, base, "model", "same", prompt_variants[0], seeds[0], styles[0], layouts[0], model, None)
        for neighbour in family["near_neighbours"]:
            emit(
                family,
                neighbour,
                "near_negative",
                "near_negative",
                prompt_variants[0],
                seeds[0],
                styles[0],
                layouts[0],
                models[0],
                neighbour["change"]["atom_type"],
            )

    per_family = Counter(label["family_id"] for label in labels)
    _require(set(per_family.values()) == {stage["expected_image_rows_per_family"]}, "Unexpected row count per family")

    enrolments = {family_id: rows[0] for (family_id, role), rows in row_lookup.items() if role == "enrolment"}
    families_by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for family in catalog["families"]:
        families_by_split[splits[family["family_id"]]].append(family)

    unrelated_for: dict[str, str] = {}
    for split, split_families in families_by_split.items():
        ordered = sorted(split_families, key=lambda f: f["family_id"])
        _require(len(ordered) >= 2, f"Split {split} needs at least two families")
        for index, family in enumerate(ordered):
            candidates = ordered[index + 1 :] + ordered[:index]
            different = [
                candidate
                for candidate in candidates
                if candidate["complexity_level"] != family["complexity_level"]
                or candidate["frequency_band"] != family["frequency_band"]
            ]
            unrelated_for[family["family_id"]] = (different or candidates)[0]["family_id"]

    pairs: list[dict[str, Any]] = []
    for family in catalog["families"]:
        family_id = family["family_id"]
        anchor = enrolments[family_id]
        split = splits[family_id]
        same_rows = [
            label["row_id"]
            for label in labels
            if label["family_id"] == family_id
            and label["relationship_to_base"] == "same"
            and label["trial_role"] != "enrolment"
        ]
        near_rows = row_lookup[(family_id, "near_negative")]
        candidates = [(row_id, "same", family_id, None) for row_id in same_rows]
        candidates += [
            (row_id, "near_negative", family_id, row_labels[row_id]["changed_atom_type"])
            for row_id in near_rows
        ]
        unrelated_family = unrelated_for[family_id]
        candidates.append((enrolments[unrelated_family], "unrelated", unrelated_family, None))
        for candidate, relationship, candidate_family, changed_type in candidates:
            pair_identity = {"anchor": anchor, "candidate": candidate, "relationship": relationship}
            pairs.append(
                {
                    "pair_id": opaque_id("p", pair_identity),
                    "anchor_row_id": anchor,
                    "candidate_row_id": candidate,
                    "split": split,
                    "relationship": relationship,
                    "family_id": family_id,
                    "candidate_family_id": candidate_family,
                    "changed_atom_type": changed_type,
                }
            )

    return {
        "inputs": sorted(inputs, key=lambda row: row["row_id"]),
        "text_inputs": sorted(text_inputs.values(), key=lambda row: row["text_input_id"]),
        "labels": sorted(labels, key=lambda row: row["row_id"]),
        "pairs": sorted(pairs, key=lambda row: row["pair_id"]),
        "splits": dict(sorted(splits.items())),
    }


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(canonical_bytes(row) + b"\n" for row in rows)


def _output_payloads(stage_name: str, manifests: dict[str, Any]) -> dict[str, bytes]:
    return {
        f"{stage_name}_v1.inputs.jsonl": jsonl_bytes(manifests["inputs"]),
        f"{stage_name}_v1.text_inputs.jsonl": jsonl_bytes(manifests["text_inputs"]),
        f"{stage_name}_v1.labels.jsonl": jsonl_bytes(manifests["labels"]),
        f"{stage_name}_v1.pairs.jsonl": jsonl_bytes(manifests["pairs"]),
    }


def load_stage(stage_name: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    design = read_json(DESIGN_PATH)
    _require(stage_name in design["stages"], f"Unknown stage: {stage_name}")
    stage = design["stages"][stage_name]
    _require(stage["approved"] is True, f"Stage is not approved: {stage_name}")
    config_dir = DESIGN_PATH.parent
    ontology = read_json((config_dir / design["ontology"]).resolve())
    catalog_path = stage["catalog"]
    _require(catalog_path is not None, f"No catalog for stage: {stage_name}")
    catalog = read_json((config_dir / catalog_path).resolve())
    return design, stage, ontology, catalog


def generate(stage_name: str, output_dir: Path = OUTPUT_ROOT) -> dict[str, Any]:
    design, stage, ontology, catalog = load_stage(stage_name)
    validation = validate_catalog(catalog, ontology, stage["family_count"])
    manifests = build_manifests(stage_name, design, ontology, catalog)
    payloads = _output_payloads(stage_name, manifests)
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in payloads.items():
        (output_dir / filename).write_bytes(payload)

    provenance = {
        "$schema_version": "semantic-secrets-manifest-provenance-v1",
        "stage": stage_name,
        "design_id": design["design_id"],
        "design_sha256": hash_json(design),
        "ontology_id": ontology["ontology_id"],
        "ontology_sha256": hash_json(ontology),
        "catalog_id": catalog["catalog_id"],
        "catalog_sha256": hash_json(catalog),
        "split_algorithm": design["split_algorithm"],
        "split_seed": stage["split_seed"],
        "split_assignments": manifests["splits"],
        "validation": validation,
        "counts": {
            "families": len(catalog["families"]),
            "image_inputs": len(manifests["inputs"]),
            "text_inputs": len(manifests["text_inputs"]),
            "labels": len(manifests["labels"]),
            "pairs": len(manifests["pairs"]),
            "pairs_by_relationship": dict(sorted(Counter(row["relationship"] for row in manifests["pairs"]).items())),
            "families_by_split": dict(sorted(Counter(manifests["splits"].values()).items())),
        },
        "output_sha256": {filename: sha256_bytes(payload) for filename, payload in sorted(payloads.items())},
        "network_access": False,
        "images_or_models_executed": False,
    }
    provenance_path = output_dir / f"{stage_name}_v1.provenance.json"
    provenance_path.write_bytes(json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return provenance


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise DesignError(f"Invalid JSONL {path}:{number}: {error}") from error
        _require(isinstance(value, dict), f"Expected object at {path}:{number}")
        rows.append(value)
    return rows


def validate_outputs(stage_name: str, output_dir: Path = OUTPUT_ROOT) -> dict[str, Any]:
    design, stage, ontology, catalog = load_stage(stage_name)
    catalog_report = validate_catalog(catalog, ontology, stage["family_count"])
    expected = build_manifests(stage_name, design, ontology, catalog)
    expected_payloads = _output_payloads(stage_name, expected)
    provenance = read_json(output_dir / f"{stage_name}_v1.provenance.json")

    for filename, payload in expected_payloads.items():
        actual = (output_dir / filename).read_bytes()
        _require(actual == payload, f"Non-deterministic or stale output: {filename}")
        _require(provenance["output_sha256"][filename] == sha256_bytes(actual), f"Hash mismatch: {filename}")

    inputs = _read_jsonl(output_dir / f"{stage_name}_v1.inputs.jsonl")
    text_inputs = _read_jsonl(output_dir / f"{stage_name}_v1.text_inputs.jsonl")
    labels = _read_jsonl(output_dir / f"{stage_name}_v1.labels.jsonl")
    pairs = _read_jsonl(output_dir / f"{stage_name}_v1.pairs.jsonl")
    label_by_row = {row["row_id"]: row for row in labels}
    input_ids = {row["row_id"] for row in inputs}
    _require(len(input_ids) == len(inputs) == len(labels), "Input/label IDs are not one-to-one")
    _require(input_ids == set(label_by_row), "Input/label join mismatch")

    for row in inputs:
        _require(set(row) == EXECUTION_FIELDS, f"Execution schema fields changed: {row['row_id']}")
        _require(not (set(row) & FORBIDDEN_EXECUTION_FIELDS), f"Label leakage: {row['row_id']}")
    for row in text_inputs:
        _require(set(row) == TEXT_INPUT_FIELDS, f"Text execution schema fields changed: {row['text_input_id']}")
        _require(not (set(row) & FORBIDDEN_EXECUTION_FIELDS), f"Text label leakage: {row['text_input_id']}")
    for row in labels:
        _require(set(row) == LABEL_FIELDS, f"Label schema fields changed: {row['row_id']}")
    for row in pairs:
        _require(set(row) == PAIR_FIELDS, f"Pair schema fields changed: {row['pair_id']}")
    _validate_with_jsonschema(inputs[0], ROOT / "schema" / "input_manifest.schema.json")
    _validate_with_jsonschema(labels[0], ROOT / "schema" / "label_manifest.schema.json")
    _validate_with_jsonschema(pairs[0], ROOT / "schema" / "pair_manifest.schema.json")

    family_splits: dict[str, set[str]] = defaultdict(set)
    for label in labels:
        family_splits[label["family_id"]].add(label["split"])
    _require(all(len(splits) == 1 for splits in family_splits.values()), "Cross-split family leakage")
    for pair in pairs:
        _require(pair["anchor_row_id"] in input_ids and pair["candidate_row_id"] in input_ids, "Pair references missing row")
        _require(label_by_row[pair["anchor_row_id"]]["split"] == pair["split"], "Anchor split mismatch")
        _require(label_by_row[pair["candidate_row_id"]]["split"] == pair["split"], "Candidate split mismatch")
        if pair["relationship"] == "unrelated":
            _require(pair["family_id"] != pair["candidate_family_id"], "Unrelated pair shares family")
        else:
            _require(pair["family_id"] == pair["candidate_family_id"], "Related pair crosses family")

    expected_counts = stage["split_counts"]
    actual_counts = Counter(next(iter(splits)) for splits in family_splits.values())
    _require(dict(actual_counts) == expected_counts, "Split quota mismatch")
    return {
        "stage": stage_name,
        "catalog": catalog_report,
        "image_inputs": len(inputs),
        "labels": len(labels),
        "pairs": len(pairs),
        "families_by_split": dict(sorted(actual_counts.items())),
        "deterministic": True,
        "label_separation": True,
        "cross_split_family_leakage": False,
    }


def deterministic_recreation_check(stage_name: str) -> None:
    with tempfile.TemporaryDirectory(prefix="semantic-secrets-manifest-a-") as first_dir, tempfile.TemporaryDirectory(prefix="semantic-secrets-manifest-b-") as second_dir:
        first = Path(first_dir)
        second = Path(second_dir)
        generate(stage_name, first)
        generate(stage_name, second)
        first_files = {path.name: path.read_bytes() for path in first.iterdir()}
        second_files = {path.name: path.read_bytes() for path in second.iterdir()}
        _require(first_files == second_files, "Manifest recreation is not byte-identical")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "validate"):
        child = subparsers.add_parser(command)
        child.add_argument("--stage", choices=("smoke", "pilot", "full"), required=True)
        child.add_argument("--output-dir", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()

    if args.command == "generate":
        report = generate(args.stage, args.output_dir)
    else:
        report = validate_outputs(args.stage, args.output_dir)
        deterministic_recreation_check(args.stage)
        report["byte_identical_recreation"] = True
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
