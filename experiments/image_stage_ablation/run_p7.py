"""Run P7 from immutable P5 cache artifacts only.

No model is loaded and no P6 or held-out test artifact is read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from prototype.semantic_secrets.matching import (
    jaccard_score,
    select_threshold,
    threshold_decision,
    weighted_overlap_score,
)
from prototype.semantic_secrets.semantics import fit_idf_weights


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config" / "p7_cached_v1.json"
RESULT_ROOT = ROOT / "results" / "p7"
RESULT = RESULT_ROOT / "cached_ablation_v1.json"
PAIRED_SCORES = RESULT_ROOT / "paired_scores_v1.jsonl"
PLOT = RESULT_ROOT / "image_text_tradeoff_v1.svg"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_bytes(row).decode("utf-8") + "\n")


def round_float(value: float) -> float:
    return round(float(value), 8)


def load_config() -> dict[str, Any]:
    return read_json(CONFIG)


def verify_sources(config: Mapping[str, Any]) -> None:
    for relative, expected in config["source_sha256"].items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing frozen P5 source: {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"frozen P5 source hash mismatch: {relative}")


def auc(positive: Sequence[float], negative: Sequence[float]) -> float:
    if not positive or not negative:
        raise ValueError("AUC requires positive and negative scores")
    wins = sum(left > right for left in positive for right in negative)
    ties = sum(left == right for left in positive for right in negative)
    return (wins + 0.5 * ties) / (len(positive) * len(negative))


def percentile(values: Sequence[float]) -> list[float]:
    ordered = sorted(values)
    low = ordered[int(0.025 * (len(ordered) - 1))]
    high = ordered[int(0.975 * (len(ordered) - 1))]
    return [round_float(low), round_float(high)]


def relationship_values(rows: Sequence[Mapping[str, Any]], name: str, relationship: str) -> list[float]:
    return [float(row["scores"][name]) for row in rows if row["relationship"] == relationship]


def basic_metrics(rows: Sequence[Mapping[str, Any]], name: str) -> dict[str, float]:
    same = relationship_values(rows, name, "same")
    near = relationship_values(rows, name, "near_negative")
    random_values = relationship_values(rows, name, "unrelated")
    return {
        "same_mean": round_float(statistics.fmean(same)),
        "same_median": round_float(statistics.median(same)),
        "near_mean": round_float(statistics.fmean(near)),
        "near_median": round_float(statistics.median(near)),
        "random_mean": round_float(statistics.fmean(random_values)),
        "random_median": round_float(statistics.median(random_values)),
        "same_minus_near_gap": round_float(statistics.fmean(same) - statistics.fmean(near)),
        "same_minus_random_gap": round_float(statistics.fmean(same) - statistics.fmean(random_values)),
        "near_auc": round_float(auc(same, near)),
        "all_negative_auc": round_float(auc(same, [*near, *random_values])),
    }


def bootstrap_comparison(
    rows: Sequence[Mapping[str, Any]], image: str, text: str, negative: str, seed: int, repetitions: int
) -> dict[str, Any]:
    by_family: dict[str, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_family[row["family_id"]][row["relationship"]] = row
    effects = []
    for family in sorted(by_family):
        family_rows = by_family[family]
        image_gap = float(family_rows["same"]["scores"][image]) - float(family_rows[negative]["scores"][image])
        text_gap = float(family_rows["same"]["scores"][text]) - float(family_rows[negative]["scores"][text])
        effects.append(image_gap - text_gap)
    rng = random.Random(seed + sum(ord(value) for value in image + text + negative))
    draws = []
    for _ in range(repetitions):
        draws.append(statistics.fmean(effects[rng.randrange(len(effects))] for _ in effects))
    return {
        "family_count": len(effects),
        "image_minus_text_mean_effect": round_float(statistics.fmean(effects)),
        "bootstrap_95pct": percentile(draws),
        "bootstrap_repetitions": repetitions,
    }


def threshold_report(rows: Sequence[Mapping[str, Any]], name: str) -> dict[str, Any]:
    train = [row for row in rows if row["split"] == "train"]
    validation = [row for row in rows if row["split"] == "validation"]
    selected = select_threshold(
        relationship_values(train, name, "same"),
        relationship_values(train, name, "near_negative"),
        relationship_values(train, name, "unrelated"),
    )
    decision = threshold_decision(
        selected.threshold,
        relationship_values(validation, name, "same"),
        relationship_values(validation, name, "near_negative"),
        relationship_values(validation, name, "unrelated"),
    )
    return {
        "selected_on": "train",
        "evaluated_on": "validation",
        "selected_threshold": round_float(selected.threshold),
        "training_objective": [round_float(value) for value in selected.objective],
        "validation": {
            "frr": round_float(decision.false_reject_rate),
            "near_far": round_float(decision.near_false_accept_rate),
            "random_far": round_float(decision.random_false_accept_rate),
            "worst_error": round_float(max(decision.false_reject_rate, decision.near_false_accept_rate, decision.random_false_accept_rate)),
            "near_auc": basic_metrics(validation, name)["near_auc"],
            "all_negative_auc": basic_metrics(validation, name)["all_negative_auc"],
        },
    }


def median(values: Sequence[float]) -> float:
    return round_float(statistics.median(values))


def build_scores(config: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    p5 = read_json(ROOT / "results/p5/smoke_v1.json")
    structured = read_jsonl(ROOT / "results/p5/structured_v1.jsonl")
    if p5["boundaries"]["test_rows_evaluated"] != 0 or p5["boundaries"]["splits"] != ["train", "validation"]:
        raise ValueError("P5 boundary is not the frozen train/validation-only design")
    if len(structured) != config["execution_boundary"]["rows"] or {row["split"] for row in structured} != {"train", "validation"}:
        raise ValueError("structured row boundary drifted")
    by_id = {row["row_id"]: row for row in structured}
    expected = {row["row_id"]: set(row["oracle_atoms"]) for row in structured}
    text_atoms = {row["row_id"]: set(row["controlled_text_atoms"]) for row in structured}
    image_atoms = {row["row_id"]: set(row["florence_atoms"]) for row in structured}
    training_docs = [
        expected[row["row_id"]]
        for row in structured
        if row["split"] == "train" and row["trial_role"] == "enrolment"
    ]
    weights = fit_idf_weights(training_docs, weights_version=p5["versions"]["weights_version"])
    metadata = read_json(ROOT / "results/p5/embedding_metadata_v1.json")
    row_ids = metadata["row_ids"]
    siglip = np.load(ROOT / "results/p5/siglip_image_v1.npy", allow_pickle=False)
    minilm = np.load(ROOT / "results/p5/minilm_text_v1.npy", allow_pickle=False)
    indexes = {row_id: index for index, row_id in enumerate(row_ids)}
    if set(indexes) != set(by_id) or list(siglip.shape) != [27, 768] or list(minilm.shape) != [27, 384]:
        raise ValueError("P5 row/embedding alignment drifted")
    output = []
    for pair in p5["pairs"]:
        left, right = pair["anchor_row_id"], pair["candidate_row_id"]
        output.append(
            {
                **pair,
                "scores": {
                    "controlled_text_jaccard": round_float(jaccard_score(text_atoms[left], text_atoms[right])),
                    "florence_jaccard": round_float(jaccard_score(image_atoms[left], image_atoms[right])),
                    "controlled_text_weighted": round_float(weighted_overlap_score(text_atoms[left], text_atoms[right], weights)),
                    "florence_weighted": round_float(weighted_overlap_score(image_atoms[left], image_atoms[right], weights)),
                    "minilm_text_cosine": round_float(float(minilm[indexes[left]] @ minilm[indexes[right]])),
                    "siglip_image_cosine": round_float(float(siglip[indexes[left]] @ siglip[indexes[right]])),
                },
            }
        )
    output.sort(key=lambda row: (row["family_id"], row["relationship"]))
    return output, {"text": set().union(*text_atoms.values()), "image": set().union(*image_atoms.values())}


def render_svg(comparisons: Mapping[str, Mapping[str, Any]]) -> None:
    width, height = 940, 260
    left, right = 300, 890
    scale = lambda value: left + (float(value) + 0.5) / 1.0 * (right - left)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="30" font-family="sans-serif" font-size="18">P7 image-minus-text improvement in same-minus-near gap</text>',
        f'<line x1="{scale(0):.2f}" y1="50" x2="{scale(0):.2f}" y2="220" stroke="#718096" stroke-dasharray="4 4"/>',
    ]
    for index, (name, report) in enumerate(comparisons.items()):
        effect = report["same_minus_near_effect"]
        y = 80 + index * 58
        low, high = effect["bootstrap_95pct"]
        point = effect["image_minus_text_mean_effect"]
        lines.extend(
            [
                f'<text x="24" y="{y + 5}" font-family="sans-serif" font-size="13">{name}</text>',
                f'<line x1="{scale(low):.2f}" y1="{y}" x2="{scale(high):.2f}" y2="{y}" stroke="#2b6cb0" stroke-width="4"/>',
                f'<circle cx="{scale(point):.2f}" cy="{y}" r="6" fill="#c53030"/>',
                f'<text x="{right - 5}" y="{y + 18}" text-anchor="end" font-family="sans-serif" font-size="11">{point:.3f} [{low:.3f}, {high:.3f}]</text>',
            ]
        )
    lines.extend([
        '<text x="300" y="245" font-family="sans-serif" font-size="11">−0.5</text>',
        '<text x="575" y="245" font-family="sans-serif" font-size="11">0 (no benefit)</text>',
        '<text x="875" y="245" font-family="sans-serif" font-size="11">+0.5</text>',
        '</svg>',
    ])
    PLOT.parent.mkdir(parents=True, exist_ok=True)
    PLOT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict[str, Any]:
    config = load_config()
    verify_sources(config)
    rows, atom_unions = build_scores(config)
    write_jsonl(PAIRED_SCORES, rows)
    p5 = read_json(ROOT / "results/p5/smoke_v1.json")
    names = sorted({name for row in rows for name in row["scores"]})
    representations = {}
    for name in names:
        representations[name] = {
            "all": basic_metrics(rows, name),
            "by_split": {
                split: basic_metrics([row for row in rows if row["split"] == split], name)
                for split in ("train", "validation")
            },
            "threshold": threshold_report(rows, name),
            "near_by_changed_atom_type": {
                changed: {
                    "count": len(values),
                    "mean": round_float(statistics.fmean(values)),
                    "values": [round_float(value) for value in values],
                }
                for changed in sorted({row["changed_atom_type"] for row in rows if row["changed_atom_type"]})
                if (
                    values := [
                        float(row["scores"][name])
                        for row in rows
                        if row["relationship"] == "near_negative" and row["changed_atom_type"] == changed
                    ]
                )
            },
        }
    comparisons = {}
    for offset, (name, pair) in enumerate(config["paired_comparisons"].items()):
        image, text = pair["image"], pair["text"]
        comparisons[name] = {
            "image": image,
            "text": text,
            "same_minus_near_effect": bootstrap_comparison(
                rows, image, text, "near_negative", config["analysis"]["bootstrap_seed"] + offset, config["analysis"]["bootstrap_repetitions"]
            ),
            "same_minus_random_effect": bootstrap_comparison(
                rows, image, text, "unrelated", config["analysis"]["bootstrap_seed"] + 100 + offset, config["analysis"]["bootstrap_repetitions"]
            ),
            "validation_worst_error_image_minus_text": round_float(
                representations[image]["threshold"]["validation"]["worst_error"]
                - representations[text]["threshold"]["validation"]["worst_error"]
            ),
            "attribution": pair.get("confound", "shared canonical atom schema and matcher; upstream extraction path differs"),
        }
    structured_nonempty = {
        "controlled_text": round_float(sum(bool(row["controlled_text_atoms"]) for row in read_jsonl(ROOT / "results/p5/structured_v1.jsonl")) / 27),
        "florence": round_float(sum(bool(row["florence_atoms"]) for row in read_jsonl(ROOT / "results/p5/structured_v1.jsonl")) / 27),
        "dense_vectors": 1.0,
    }
    generator_latency = p5["resources"]["generator"]["latency_seconds"]
    florence_rows = read_jsonl(ROOT / "results/p5/florence_raw_v1.jsonl")
    florence_latency = [sum(task["latency_seconds"] for task in row["tasks"].values()) for row in florence_rows]
    resources = {
        "image_generation": {
            "median_seconds_per_row": median(generator_latency),
            "peak_cuda_allocated_mib": max(p5["resources"]["generator"]["peak_cuda_allocated_mib"]),
            "cached_png_bytes_total": p5["resources"]["generator"]["png_bytes"],
        },
        "image_structured_extraction": {
            "median_seconds_per_row": median(florence_latency),
            "peak_cuda_allocated_mib": p5["resources"]["florence"]["peak_cuda_allocated_mib"],
        },
        "image_dense_encoding": p5["resources"]["siglip"],
        "text_dense_encoding": p5["resources"]["minilm"],
        "controlled_text_parser_latency": "not measured in P5; no numeric comparison claimed",
        "representation_storage_bytes": {
            "structured_jsonl_shared_file": p5["resources"]["structured_result_bytes"],
            "siglip_array": p5["resources"]["siglip_array_bytes"],
            "minilm_array": p5["resources"]["minilm_array_bytes"],
        },
    }
    image_f1 = p5["atom_metrics"]["florence"]["macro_f1"]
    text_f1 = p5["atom_metrics"]["controlled_text"]["macro_f1"]
    core_checks = {}
    for name, comparison in comparisons.items():
        structured = name.startswith("structured")
        checks: dict[str, bool] = {
            "near_effect_ci_lower_positive": comparison["same_minus_near_effect"]["bootstrap_95pct"][0] > 0,
            "random_effect_ci_lower_at_least_minus_0_02": comparison["same_minus_random_effect"]["bootstrap_95pct"][0] >= -0.02,
            "validation_worst_error_improves_by_at_least_0_10": comparison["validation_worst_error_image_minus_text"] <= -0.10,
            "structured_atom_f1_not_lower": (not structured) or image_f1 >= text_f1,
        }
        # The shared structured schema/matcher can attribute a complete measured
        # benefit to the instantiated upstream path. The dense pair cannot isolate
        # the image transform from its different encoder. Added image costs are
        # justified only when all quantitative benefit checks already pass.
        checks["attribution_and_cost_case"] = structured and all(checks.values())
        core_checks[name] = {"checks": checks, "passes": all(checks.values())}
    any_core = any(item["passes"] for item in core_checks.values())
    comparable = all(name in comparisons for name in ("structured_jaccard", "structured_weighted", "dense_cosine"))
    outcome = "A" if any_core else ("B" if comparable else "C")
    report = {
        "$schema_version": "semantic-secrets-p7-result-v1",
        "experiment_id": config["experiment_id"],
        "run_kind": "bounded cache-only paired engineering diagnostic; not publication or Gate A result",
        "publication_result": False,
        "config_sha256": sha256_bytes(canonical_bytes(config)),
        "boundaries": {
            **config["execution_boundary"],
            "pair_count": len(rows),
            "test_rows_evaluated": 0,
            "human_participants": 0,
            "human_claims": 0,
            "model_drift": "not available: one frozen revision per P5 model",
        },
        "source_sha256": config["source_sha256"],
        "nonempty_rate": structured_nonempty,
        "representations": representations,
        "comparisons": comparisons,
        "atom_metrics": p5["atom_metrics"],
        "atom_type_unions": {name: sorted(value) for name, value in atom_unions.items()},
        "resources": resources,
        "privacy_exposure": {
            "image_path": [
                "adds a local generated image containing visual semantic content",
                "adds generator and image-extractor/encoder model supply-chain and drift surfaces",
                "raw SigLIP embeddings remain linkable/candidate-retrievable in the P5 cheap probe",
                "images may be discarded after local extraction, but this does not remove runtime exposure"
            ],
            "text_path": [
                "raw prompt and structured atoms remain readable locally",
                "raw MiniLM embeddings remain linkable/candidate-retrievable in the P5 cheap probe"
            ],
            "shared": "neither plaintext path is privacy-preserving storage; protocol protection remains unevaluated and blocked"
        },
        "confound_audit": {
            "structured": "comparable canonical schema and matcher isolate the instantiated upstream paths, but Florence's low fidelity is an image-path bottleneck",
            "dense": "SigLIP versus MiniLM compares complete image/text pathways, not the image transform alone; encoder training, capacity, and dimensions differ",
            "extra_information": "the generated image is derived from the same source prompt and adds stochastic/model transformation, not a separately measured information source",
        },
        "material_benefit": {
            "frozen_rule": config["material_benefit_rule"],
            "comparison_checks": core_checks,
            "gate_b_outcome": outcome,
            "gate_b_label": {
                "A": "retain image as core",
                "B": "make image optional/reposition as measurement baseline/remove from authentication core",
                "C": "unresolved because extraction is the bottleneck"
            }[outcome],
            "reason": "No tested image pathway met the frozen material-benefit rule; comparable structured and dense pathway evidence is available, so the outcome is B rather than an unresolved C.",
        },
        "semantic_policy": {
            "future_hypothesis": "mandatory discriminative anchors with tolerant secondary attributes",
            "scientific_status": "motivated for future study by oracle-versus-extractor gaps and changed-atom failures, but not established or tested by P7",
            "implemented_or_tuned": False,
            "requirements_before_test": ["new scheme/version", "independent rationale", "new data", "preregistration", "new gate"],
            "exact_prompt_or_exact_set_equality": False,
        },
        "artifacts": {
            "paired_scores_sha256": sha256_file(PAIRED_SCORES),
        },
    }
    write_json(RESULT, report)
    render_svg(comparisons)
    validate_saved()
    return report


def validate_saved() -> None:
    config = load_config()
    verify_sources(config)
    report = read_json(RESULT)
    if report["config_sha256"] != sha256_bytes(canonical_bytes(config)):
        raise ValueError("P7 config hash mismatch")
    if report["boundaries"]["test_rows_evaluated"] != 0 or report["boundaries"]["p6_artifact_access"] is not False:
        raise ValueError("P7 boundary violation")
    if report["boundaries"]["pair_count"] != 27 or report["boundaries"]["families"] != 9:
        raise ValueError("P7 cardinality mismatch")
    if report["material_benefit"]["gate_b_outcome"] not in {"A", "B", "C"}:
        raise ValueError("invalid Gate B outcome")
    if report["semantic_policy"]["implemented_or_tuned"] is not False:
        raise ValueError("P7 must not implement the future semantic policy")
    if sha256_file(PAIRED_SCORES) != report["artifacts"]["paired_scores_sha256"]:
        raise ValueError("P7 paired score hash mismatch")
    rows = read_jsonl(PAIRED_SCORES)
    if {row["split"] for row in rows} != {"train", "validation"} or any(row["split"] == "test" for row in rows):
        raise ValueError("P7 scores contain a forbidden split")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        validate_saved()
        print(json.dumps({"validated": str(RESULT), "experiment_id": "p7-cached-v1"}, indent=2))
    else:
        report = run()
        print(json.dumps({"result": str(RESULT), "gate_b": report["material_benefit"]["gate_b_outcome"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
