"""Deterministic P9-v3B validation metrics and Gate V3-A1 evaluation.

This module consumes only frozen validation records and the pre-inference
support-opportunity table.  It never changes observations, thresholds, or
ground truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from prototype.semantic_secrets.v3 import load_active_contract

from .dataset import OPPORTUNITY_FIELDS, audit_opportunities
from .guard import git_commit
from .io import atomic_write, canonical_bytes, read_json, sha256_file
from .results import observation_projection


ATOM_TYPES = (
    "entity", "colour", "size", "material", "pattern", "count",
    "unary_action", "binary_interaction", "geometry_relation", "scene",
)


def _iou(a: Sequence[float], b: Sequence[float]) -> float:
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - intersection
    return 0.0 if union <= 0 else intersection / union


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float | None]:
    if total == 0:
        return [None, None]
    point = successes / total
    denominator = 1 + z * z / total
    centre = (point + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(point * (1 - point) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, centre - radius), min(1.0, centre + radius)]


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _f1(tp: int, fp: int, fn: int) -> float | None:
    denominator = 2 * tp + fp + fn
    return None if denominator == 0 else 2 * tp / denominator


def _percentile(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def _bootstrap(
    family_counts: Mapping[str, tuple[int, int, int, int, int]],
    repetitions: int,
    seed: int,
) -> dict[str, list[float | None]]:
    families = sorted(family_counts)
    if not families:
        return {name: [None, None] for name in ("precision", "recall", "f1")}
    rng = random.Random(seed)
    samples: dict[str, list[float]] = {name: [] for name in ("precision", "recall", "f1")}
    for _ in range(repetitions):
        selected = [families[rng.randrange(len(families))] for _ in families]
        tp = sum(family_counts[item][0] for item in selected)
        fp = sum(family_counts[item][1] for item in selected)
        fn = sum(family_counts[item][2] for item in selected)
        for name, value in (
            ("precision", _rate(tp, tp + fp)),
            ("recall", _rate(tp, tp + fn)),
            ("f1", _f1(tp, fp, fn)),
        ):
            if value is not None:
                samples[name].append(value)
    return {name: [_percentile(samples[name], 0.025), _percentile(samples[name], 0.975)] for name in ("precision", "recall", "f1")}


def _load_records(directory: Path) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(directory.rglob("*.json")):
        record = read_json(path)
        request = record.get("request", {})
        key = (request.get("pipeline_id"), request.get("image_id"))
        if None in key or key in rows:
            raise ValueError(f"invalid or duplicate result key in {path}")
        rows[key] = record
    return rows


def _read_opportunities(path: Path) -> dict[str, list[dict[str, str]]]:
    rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != OPPORTUNITY_FIELDS:
            raise ValueError("support-opportunity header does not match v3.2 exactly")
        for row in reader:
            if row["split"] == "validation":
                rows[row["image_id"]].append(row)
    return rows


def _node_maps(result: Mapping[str, Any]) -> tuple[dict[str, str], dict[str, list[float]]]:
    graph = result["graph"]
    categories = {row["id"]: row["category"] for row in graph["nodes"]}
    boxes = {row["id"]: row["bbox"] for row in result["audit"]["node_boxes"]}
    return categories, boxes


def _reference_mapping(scenario: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, str]:
    """Maximum-IoU category-equal one-to-one assignment at IoU >= 0.50."""

    categories, boxes = _node_maps(result)
    references = sorted(scenario["reference_entities"], key=lambda row: row["reference_id"])
    best_score = -1.0
    best_key: tuple[str, ...] | None = None
    best: dict[str, str] = {}

    def visit(index: int, used: set[str], score: float, mapping: dict[str, str]) -> None:
        nonlocal best_score, best_key, best
        if index == len(references):
            key = tuple(mapping.get(row["reference_id"], "~") for row in references)
            if score > best_score or (score == best_score and (best_key is None or key < best_key)):
                best_score, best_key, best = score, key, dict(mapping)
            return
        reference = references[index]
        visit(index + 1, used, score, mapping)
        for node in sorted(boxes):
            overlap = _iou(reference["bbox_xyxy"], boxes[node])
            if node not in used and categories.get(node) == reference["category"] and overlap >= 0.50:
                mapping[reference["reference_id"]] = node
                visit(index + 1, used | {node}, score + overlap, mapping)
                mapping.pop(reference["reference_id"])

    visit(0, set(), 0.0, {})
    return best


def _scope_prediction(
    opportunity: Mapping[str, str], result: Mapping[str, Any], scenario: Mapping[str, Any],
    mapping: Mapping[str, str],
) -> tuple[bool, bool]:
    """Return (exact reference-value prediction, non-abstained type prediction)."""

    graph = result["graph"]
    categories, boxes = _node_maps(result)
    entities = {row["reference_id"]: row for row in scenario["reference_entities"]}
    atom_type, value = opportunity["atom_type"], opportunity["reference_value"]
    source_ref, target_ref = opportunity["source_reference_id"], opportunity["target_reference_id"]

    if atom_type == "entity":
        source = entities[source_ref]
        candidates = [
            categories[node] for node, box in boxes.items()
            if _iou(source["bbox_xyxy"], box) >= 0.50
        ]
        return value in candidates, bool(candidates)

    source_node = mapping.get(source_ref)
    target_node = mapping.get(target_ref)

    if atom_type in {"colour", "size", "material", "pattern"}:
        values = [row["value"] for row in graph["attributes"] if row["node"] == source_node and row["type"] == atom_type]
    elif atom_type == "unary_action":
        values = [row["action"] for row in graph["unary"] if row["node"] == source_node]
    elif atom_type in {"binary_interaction", "geometry_relation"}:
        geometry = set(load_active_contract().base_observation["derived_spatial_relations"])
        values = [
            row["relation"] for row in graph["binary"]
            if row["source"] == source_node and row["target"] == target_node
            and ((row["relation"] in geometry) == (atom_type == "geometry_relation"))
        ]
    elif atom_type == "scene":
        values = [row["value"] for row in graph["scenes"]]
    elif atom_type == "count":
        category = opportunity.get("scope_category")
        if not category:
            raise ValueError(
                f"{opportunity['opportunity_id']}: count ground truth lacks one unambiguous scope_category"
            )
        values = [row["bucket"] for row in graph["counts"] if row["category"] == category]
    else:
        raise ValueError(f"unsupported opportunity type {atom_type}")
    return value in values, bool(values)


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    covered: int = 0
    opportunities: int = 0

    def add(self, polarity: str, exact: bool, covered: bool) -> None:
        self.opportunities += 1
        self.covered += int(covered)
        if polarity == "positive":
            self.tp += int(exact)
            self.fn += int(not exact)
        elif exact:
            self.fp += 1

    def tuple(self) -> tuple[int, int, int, int, int]:
        return self.tp, self.fp, self.fn, self.covered, self.opportunities


def _metric_record(counts: Counts, family: Mapping[str, Counts], repetitions: int, seed: int) -> dict[str, Any]:
    precision = _rate(counts.tp, counts.tp + counts.fp)
    recall = _rate(counts.tp, counts.tp + counts.fn)
    coverage = _rate(counts.covered, counts.opportunities)
    return {
        "counts": {"tp": counts.tp, "fp": counts.fp, "fn": counts.fn, "covered": counts.covered, "opportunities": counts.opportunities},
        "precision": precision,
        "precision_wilson_95": wilson(counts.tp, counts.tp + counts.fp),
        "recall": recall,
        "recall_wilson_95": wilson(counts.tp, counts.tp + counts.fn),
        "f1": _f1(counts.tp, counts.fp, counts.fn),
        "coverage": coverage,
        "coverage_wilson_95": wilson(counts.covered, counts.opportunities),
        "abstention_rate": None if coverage is None else 1 - coverage,
        "family_bootstrap_95": _bootstrap({key: value.tuple() for key, value in family.items()}, repetitions, seed),
    }


def evaluate(
    results: Path, manifest_path: Path, opportunities_path: Path, data_root: Path,
    compiler_report: Path,
) -> dict[str, Any]:
    contract = load_active_contract()
    manifest = read_json(manifest_path)
    audit_opportunities(opportunities_path, manifest, data_root)
    validation = _load_records(results / "validation")
    repeat = _load_records(results / "validation-repeat")
    development = _load_records(results / "development")
    expected = {
        (pipeline, row["image_id"])
        for pipeline in contract.pipeline_ids for row in manifest["images"] if row["split"] == "validation"
    }
    if set(validation) != expected or set(repeat) != expected:
        raise ValueError("validation and repeat must each contain every frozen pipeline/image pair exactly once")
    expected_development = {
        (pipeline, row["image_id"])
        for pipeline in contract.pipeline_ids for row in manifest["images"] if row["split"] == "development"
    }
    if set(development) != expected_development:
        raise ValueError("development must contain every frozen pipeline/image pair exactly once")
    opportunities = _read_opportunities(opportunities_path)
    manifest_rows = {row["image_id"]: row for row in manifest["images"]}
    scenarios = {
        image_id: read_json(data_root / row["scenario_specification_path"])
        for image_id, row in manifest_rows.items() if row["split"] == "validation"
    }
    prereg = contract.base_prereg
    repetitions = int(prereg["uncertainty"]["bootstrap_repetitions"])
    seed = int(prereg["uncertainty"]["bootstrap_seed"])
    support_plan = contract.amend_prereg["dataset_support"]["validation_plan_each_stratum"]
    compiler = read_json(compiler_report)
    if any((
        compiler.get("schema_version") != "compiler-invariant-report-v3.0.0",
        compiler.get("compiler_id") != contract.compiler_id,
        compiler.get("config_hashes") != dict(contract.config_hashes),
        compiler.get("git_commit") != git_commit(),
    )):
        raise ValueError("invalid compiler invariant report")

    pipelines: dict[str, Any] = {}
    for pipeline in contract.pipeline_ids:
        totals: dict[tuple[str, str], Counts] = defaultdict(Counts)
        families: dict[tuple[str, str], dict[str, Counts]] = defaultdict(lambda: defaultdict(Counts))
        failures = 0
        telemetry: list[dict[str, float]] = []
        observation_equal = graph_equal = 0
        for key in sorted(item for item in expected if item[0] == pipeline):
            record, repeated = validation[key], repeat[key]
            image_id = key[1]
            row = manifest_rows[image_id]
            failed = record["pipeline_failure"] is not None or record["compiler_result"] is None or record["compiler_result"].get("status") != "graph"
            failures += int(failed)
            if not failed:
                correspondence = _reference_mapping(scenarios[image_id], record["compiler_result"])
                for opportunity in opportunities[image_id]:
                    metric_key = (row["stratum"], opportunity["atom_type"])
                    exact, covered = _scope_prediction(opportunity, record["compiler_result"], scenarios[image_id], correspondence)
                    totals[metric_key].add(opportunity["polarity"], exact, covered)
                    families[metric_key][row["family_id"]].add(opportunity["polarity"], exact, covered)
            else:
                for opportunity in opportunities[image_id]:
                    metric_key = (row["stratum"], opportunity["atom_type"])
                    totals[metric_key].add(opportunity["polarity"], False, False)
                    families[metric_key][row["family_id"]].add(opportunity["polarity"], False, False)
            if (record["pipeline_failure"] is None) == (repeated["pipeline_failure"] is None):
                if record["pipeline_failure"] is not None:
                    equal = record["pipeline_failure"]["code"] == repeated["pipeline_failure"]["code"]
                    observation_equal += int(equal)
                    graph_equal += int(equal)
                else:
                    observation_equal += int(observation_projection(record["observation"]) == observation_projection(repeated["observation"]))
                    graph_equal += int(record["compiler_result"] == repeated["compiler_result"])

        for collection in (development, validation, repeat):
            for key, record in collection.items():
                if key[0] != pipeline or record["pipeline_failure"] is not None or record["observation"] is None:
                    continue
                if record["request"].get("resource_warmup"):
                    continue
                events = record["observation"].get("execution_telemetry", [])
                controller = record.get("controller_telemetry") or {}
                separate_gpu_processes = pipeline == "v3.1-egtr-siglip2"
                telemetry.append({
                    "elapsed_seconds": float(record["complete_pipeline_elapsed_seconds"]),
                    "rss_bytes": (
                        (sum(float(item["peak_process_rss_bytes"]) for item in events) if separate_gpu_processes else max((float(item["peak_process_rss_bytes"]) for item in events), default=0))
                        + float(controller.get("peak_process_rss_bytes", 0))
                    ),
                    "vram_allocated_bytes": sum(float(item["framework_peak_gpu_allocated_bytes"]) for item in events) if separate_gpu_processes else max((float(item["framework_peak_gpu_allocated_bytes"]) for item in events), default=0),
                    "vram_reserved_bytes": sum(float(item["framework_peak_gpu_reserved_bytes"]) for item in events) if separate_gpu_processes else max((float(item["framework_peak_gpu_reserved_bytes"]) for item in events), default=0),
                })

        metric_rows: dict[str, dict[str, Any]] = {}
        eligible: set[str] = set()
        thresholds = prereg["perception_metrics"]["type_eligibility_thresholds"]
        for stratum in ("A_controlled_geometric", "B_naturalistic_t2i"):
            metric_rows[stratum] = {}
            for atom_type in ATOM_TYPES:
                record = _metric_record(totals[(stratum, atom_type)], families[(stratum, atom_type)], repetitions, seed)
                support = support_plan[atom_type]
                evaluable = bool(support["gate_evaluable"])
                bootstrap = record["family_bootstrap_95"]
                passes = evaluable and all((
                    (record["precision"] or 0) >= thresholds["precision_point_min"],
                    (bootstrap["precision"][0] or 0) >= thresholds["precision_family_bootstrap_lower_min"],
                    (record["recall"] or 0) >= thresholds["recall_point_min"],
                    (bootstrap["recall"][0] or 0) >= thresholds["recall_family_bootstrap_lower_min"],
                    (record["f1"] or 0) >= thresholds["f1_point_min"],
                    (bootstrap["f1"][0] or 0) >= thresholds["f1_family_bootstrap_lower_min"],
                    (record["coverage"] or 0) >= thresholds["coverage_point_min"],
                    (record["coverage_wilson_95"][0] or 0) >= thresholds["coverage_wilson_lower_min"],
                ))
                record.update(gate_evaluable=evaluable, eligibility_pass=passes)
                metric_rows[stratum][atom_type] = record
        for atom_type in ATOM_TYPES:
            if all(metric_rows[stratum][atom_type]["eligibility_pass"] for stratum in metric_rows):
                eligible.add(atom_type)

        total_images = len([key for key in expected if key[0] == pipeline])
        failure_interval = wilson(failures, total_images)
        repeat_n = total_images
        repeatability = {
            "pairs": repeat_n,
            "canonical_observation_equality": observation_equal / repeat_n,
            "canonical_observation_equality_wilson_95": wilson(observation_equal, repeat_n),
            "canonical_graph_equality": graph_equal / repeat_n,
            "canonical_graph_equality_wilson_95": wilson(graph_equal, repeat_n),
        }
        resources = {
            "measured_images": len(telemetry),
            "median_seconds_per_image": statistics.median([row["elapsed_seconds"] for row in telemetry]) if telemetry else None,
            "p95_seconds_per_image": _percentile([row["elapsed_seconds"] for row in telemetry], 0.95),
            "peak_rss_bytes": max((row["rss_bytes"] for row in telemetry), default=None),
            "peak_vram_allocated_bytes": max((row["vram_allocated_bytes"] for row in telemetry), default=None),
            "peak_vram_reserved_bytes": max((row["vram_reserved_bytes"] for row in telemetry), default=None),
        }
        gate = prereg["gate_v3_a1"]
        minimum = gate["minimum_eligible_language"]
        language_pass = (
            set(minimum["required_types"]) <= eligible
            and len(eligible - set(minimum["required_types"])) >= minimum["minimum_additional_types"]
            and len(eligible & set(minimum["minimum_structural_types_from"])) >= minimum["minimum_structural_type_count"]
        )
        repeat_cfg = prereg["repeatability"]
        compute = contract.amend_prereg["compute"]
        checks = {
            "compiler_invariants": compiler.get("passed") is True and compiler.get("cases_passed", 0) >= 320,
            "pipeline_failure_rate": failures / total_images <= gate["pipeline_failure_rate_point_max"] and failure_interval[1] <= gate["pipeline_failure_rate_wilson_upper_max"],
            "repeatability": (
                repeatability["canonical_observation_equality"] >= repeat_cfg["canonical_observation_equality_point_min"]
                and repeatability["canonical_observation_equality_wilson_95"][0] >= repeat_cfg["canonical_observation_equality_wilson_lower_min"]
                and repeatability["canonical_graph_equality"] >= repeat_cfg["canonical_graph_equality_point_min"]
                and repeatability["canonical_graph_equality_wilson_95"][0] >= repeat_cfg["canonical_graph_equality_wilson_lower_min"]
            ),
            "resources": bool(telemetry) and (
                resources["peak_vram_allocated_bytes"] <= compute["pipeline_peak_vram_gib_max"] * 1024 ** 3
                and resources["peak_rss_bytes"] <= compute["pipeline_peak_rss_gib_max"] * 1024 ** 3
                and resources["median_seconds_per_image"] <= compute["median_seconds_per_image_max"]
                and resources["p95_seconds_per_image"] <= compute["p95_seconds_per_image_max"]
            ),
            "minimum_eligible_language": language_pass,
        }
        pipelines[pipeline] = {
            "metrics_by_stratum_and_type": metric_rows,
            "pipeline_failure_rate": failures / total_images,
            "pipeline_failure_rate_wilson_95": failure_interval,
            "repeatability": repeatability,
            "resources": resources,
            "eligible_L_cred": sorted(eligible),
            "gate_checks": checks,
            "gate_pass": all(checks.values()),
        }

    return {
        "schema_version": "p9-v3b-evaluation-v3.2.0",
        "config_hashes": dict(contract.config_hashes),
        "manifest_sha256": sha256_file(manifest_path),
        "opportunities_sha256": sha256_file(opportunities_path),
        "compiler_report_sha256": sha256_file(compiler_report),
        "pipelines": pipelines,
        "gate_v3_a1": {
            "decision": "pass" if any(row["gate_pass"] for row in pipelines.values()) else "fail",
            "passing_pipelines": sorted(key for key, row in pipelines.items() if row["gate_pass"]),
            "cross_pipeline_type_union_used": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute frozen P9-v3B metrics and Gate V3-A1")
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--opportunities", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--compiler-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    value = evaluate(args.results, args.manifest, args.opportunities, args.data_root, args.compiler_report)
    if args.output.exists():
        raise SystemExit("REFUSED: evaluation output already exists")
    atomic_write(args.output, canonical_bytes(value))
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output), "gate": value["gate_v3_a1"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
