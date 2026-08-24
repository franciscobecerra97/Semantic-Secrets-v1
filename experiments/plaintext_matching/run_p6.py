"""Run the frozen P6 plaintext-matching pilot without opening pilot test data."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

from prototype.semantic_secrets.matching import (
    cardinality_score,
    jaccard_score,
    select_threshold,
    threshold_decision,
    weighted_overlap_score,
)
from prototype.semantic_secrets.semantics import (
    canonicalize_extraction,
    canonicalize_label_atoms,
    extract_controlled_text,
    fit_idf_weights,
    normalise_token,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config" / "p6_pilot_v1.json"
MANIFEST_ROOT = REPO_ROOT / "experiments" / "datasets" / "manifests"
RESULT_ROOT = REPO_ROOT / "results" / "p6"
REPRESENTATIONS = RESULT_ROOT / "representations_v1.jsonl"
ROW_INDEX = RESULT_ROOT / "matrix_rows_v1.json"
CARDINALITY_MATRIX = RESULT_ROOT / "cardinality_v1.npy"
JACCARD_MATRIX = RESULT_ROOT / "jaccard_v1.npy"
WEIGHTED_MATRIX = RESULT_ROOT / "weighted_overlap_v1.npy"
MINILM_MATRIX = RESULT_ROOT / "minilm_cosine_v1.npy"
MINILM_ARRAY = RESULT_ROOT / "minilm_text_v1.npy"
EMBEDDING_METADATA = RESULT_ROOT / "embedding_metadata_v1.json"
PAIR_SCORES = RESULT_ROOT / "pair_scores_v1.jsonl"
FINAL_RESULT = RESULT_ROOT / "pilot_v1.json"
FINAL_PLOT = RESULT_ROOT / "security_reliability_v1.svg"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=json_scalar,
    ).encode("utf-8")


def json_scalar(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, default=json_scalar) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical_bytes(row) + b"\n" for row in rows))


def round_float(value: float) -> float:
    return round(float(value), 8)


def load_selected_rows(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    inputs = {row["row_id"]: row for row in read_jsonl(MANIFEST_ROOT / "pilot_v1.inputs.jsonl")}
    labels = read_jsonl(MANIFEST_ROOT / "pilot_v1.labels.jsonl")
    allowed_splits = set(config["dataset"]["evaluation_splits"])
    allowed_roles = set(config["dataset"]["roles"])
    rows = [
        {"input": inputs[label["row_id"]], "label": label}
        for label in labels
        if label["split"] in allowed_splits and label["trial_role"] in allowed_roles
    ]
    rows.sort(key=lambda row: row["input"]["row_id"])
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_family[row["label"]["family_id"]].append(row)
    expected = {"enrolment": 1, "paraphrase": 2, "near_negative": 1}
    for family_id, family_rows in by_family.items():
        observed = {
            role: sum(row["label"]["trial_role"] == role for row in family_rows)
            for role in expected
        }
        if observed != expected:
            raise ValueError(f"unexpected selected roles for {family_id}: {observed}")
    split_counts = {
        split: len({row["label"]["family_id"] for row in rows if row["label"]["split"] == split})
        for split in allowed_splits
    }
    if split_counts != config["dataset"]["family_counts"]:
        raise ValueError(f"evaluated family counts changed: {split_counts}")
    if any(row["label"]["split"] == "test" for row in rows):
        raise ValueError("pilot test rows must remain sealed")
    return rows


def reconstruct_p5_weights(config: Mapping[str, Any]) -> dict[str, float]:
    labels = read_jsonl(MANIFEST_ROOT / "smoke_v1.labels.jsonl")
    documents = [
        canonicalize_label_atoms(row["expected_atoms"]).atoms
        for row in labels
        if row["split"] == "train" and row["trial_role"] == "enrolment"
    ]
    weights = fit_idf_weights(documents, weights_version=config["weighting"]["weights_version"])
    observed = sha256_bytes(canonical_bytes(weights))
    if observed != config["weighting"]["expected_sha256"]:
        raise ValueError(f"frozen P5 weight hash mismatch: {observed}")
    return weights


def build_representations(
    rows: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    lexicon = sorted(
        {
            normalise_token(atom["value"], singular=True)
            for row in rows
            if row["label"]["split"] == config["canonicalisation"]["object_lexicon_fit_split"]
            for atom in row["label"]["expected_atoms"]
            if atom["type"] == "object"
        }
    )
    output: list[dict[str, Any]] = []
    atoms_by_row: dict[str, set[str]] = {}
    for row in rows:
        result = canonicalize_extraction(
            extract_controlled_text(row["input"]["core_prompt"], object_lexicon=lexicon),
            minimum_confidence=config["canonicalisation"]["minimum_confidence"],
        )
        row_id = row["input"]["row_id"]
        atoms_by_row[row_id] = set(result.atoms)
        output.append(
            {
                "row_id": row_id,
                "family_id": row["label"]["family_id"],
                "split": row["label"]["split"],
                "trial_role": row["label"]["trial_role"],
                "prompt_variant": row["input"]["prompt_variant"],
                "complexity_level": row["label"]["complexity_level"],
                "frequency_band": row["label"]["frequency_band"],
                "changed_atom_type": row["label"]["changed_atom_type"],
                "atoms": list(result.atoms),
                "warnings": list(result.warnings),
            }
        )
    return output, atoms_by_row


def run_embeddings(config: Mapping[str, Any]) -> None:
    import torch
    from transformers import AutoModel, AutoTokenizer

    rows = load_selected_rows(config)
    texts = [row["input"]["core_prompt"] for row in rows]
    cfg = config["minilm"]
    cache_dir = (HERE / cfg["cache_dir"]).resolve()
    if not cache_dir.is_dir():
        raise FileNotFoundError(f"pinned local model cache is missing: {cache_dir}")
    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(
        cfg["model_id"],
        revision=cfg["revision"],
        local_files_only=cfg["local_files_only"],
        cache_dir=cache_dir,
    )
    model = AutoModel.from_pretrained(
        cfg["model_id"],
        revision=cfg["revision"],
        local_files_only=cfg["local_files_only"],
        cache_dir=cache_dir,
        torch_dtype=torch.float32,
    ).eval().to(cfg["device"])
    load_seconds = time.perf_counter() - start

    def embed() -> tuple[np.ndarray, float, float]:
        batches = []
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        with torch.inference_mode():
            for offset in range(0, len(texts), cfg["batch_size"]):
                encoded = tokenizer(
                    texts[offset : offset + cfg["batch_size"]],
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                )
                encoded = {key: value.to(cfg["device"]) for key, value in encoded.items()}
                hidden = model(**encoded)[0]
                mask = encoded["attention_mask"].unsqueeze(-1).expand(hidden.size()).float()
                pooled = torch.sum(hidden * mask, dim=1) / torch.clamp(mask.sum(dim=1), min=1e-9)
                batches.append(torch.nn.functional.normalize(pooled.float(), p=2, dim=-1).cpu())
        torch.cuda.synchronize()
        array = torch.cat(batches).numpy().astype("<f4", copy=False)
        return array, time.perf_counter() - started, torch.cuda.max_memory_allocated() / 1048576

    first, first_seconds, first_peak = embed()
    second, second_seconds, second_peak = embed()
    if not np.array_equal(first, second):
        raise RuntimeError("MiniLM pilot embeddings did not repeat exactly")
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    np.save(MINILM_ARRAY, first, allow_pickle=False)
    p5_metadata = read_json(REPO_ROOT / "results" / "p5" / "embedding_metadata_v1.json")
    write_json(
        EMBEDDING_METADATA,
        {
            "$schema_version": "semantic-secrets-p6-embedding-metadata-v1",
            "run_id": config["run_id"],
            "backend": cfg,
            "row_ids": [row["input"]["row_id"] for row in rows],
            "shape": list(first.shape),
            "fixed_input_equal": True,
            "embedding_sha256": sha256_bytes(first.tobytes()),
            "array_file_sha256": sha256_file(MINILM_ARRAY),
            "load_seconds": round(load_seconds, 6),
            "run_seconds": [round(first_seconds, 6), round(second_seconds, 6)],
            "peak_cuda_allocated_mib": [round(first_peak, 2), round(second_peak, 2)],
            "p5_model_artifact": p5_metadata["minilm"]["artifact"],
            "publication_result": False,
        },
    )


def build_matrices(
    rows: Sequence[Mapping[str, Any]],
    atoms: Mapping[str, set[str]],
    weights: Mapping[str, float],
    dense: np.ndarray,
) -> dict[str, np.ndarray]:
    count = len(rows)
    if dense.shape != (count, 384):
        raise ValueError(f"unexpected MiniLM array shape: {dense.shape}")
    cardinality = np.empty((count, count), dtype="<i4")
    jaccard = np.empty((count, count), dtype="<f4")
    weighted = np.empty((count, count), dtype="<f4")
    row_ids = [row["input"]["row_id"] for row in rows]
    for i, left_id in enumerate(row_ids):
        for j, right_id in enumerate(row_ids):
            cardinality[i, j] = cardinality_score(atoms[left_id], atoms[right_id])
            jaccard[i, j] = jaccard_score(atoms[left_id], atoms[right_id])
            weighted[i, j] = weighted_overlap_score(atoms[left_id], atoms[right_id], weights)
    cosine = np.clip(dense @ dense.T, -1.0, 1.0).astype("<f4", copy=False)
    return {
        "cardinality": cardinality,
        "jaccard": jaccard,
        "weighted_overlap": weighted,
        "minilm_cosine": cosine,
    }


def build_pairs(
    rows: Sequence[Mapping[str, Any]], matrices: Mapping[str, np.ndarray]
) -> list[dict[str, Any]]:
    indexes = {row["input"]["row_id"]: index for index, row in enumerate(rows)}
    by_split_family: dict[str, dict[str, list[Mapping[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        by_split_family[row["label"]["split"]][row["label"]["family_id"]].append(row)
    output: list[dict[str, Any]] = []
    for split, families in sorted(by_split_family.items()):
        enrolments = {
            family_id: next(row for row in family_rows if row["label"]["trial_role"] == "enrolment")
            for family_id, family_rows in families.items()
        }
        for family_id, family_rows in sorted(families.items()):
            anchor = enrolments[family_id]
            candidates: list[tuple[Mapping[str, Any], str, str | None]] = []
            candidates.extend(
                (row, "same", None)
                for row in family_rows
                if row["label"]["trial_role"] == "paraphrase"
            )
            candidates.extend(
                (row, "near_negative", row["label"]["changed_atom_type"])
                for row in family_rows
                if row["label"]["trial_role"] == "near_negative"
            )
            candidates.extend(
                (candidate, "random_negative", None)
                for candidate_family, candidate in sorted(enrolments.items())
                if candidate_family != family_id
            )
            anchor_id = anchor["input"]["row_id"]
            for candidate, relationship, changed_type in candidates:
                candidate_id = candidate["input"]["row_id"]
                i, j = indexes[anchor_id], indexes[candidate_id]
                identity = canonical_bytes(
                    {"anchor": anchor_id, "candidate": candidate_id, "relationship": relationship}
                )
                output.append(
                    {
                        "pair_id": "p6_" + sha256_bytes(identity)[:20],
                        "anchor_row_id": anchor_id,
                        "candidate_row_id": candidate_id,
                        "family_id": family_id,
                        "candidate_family_id": candidate["label"]["family_id"],
                        "split": split,
                        "relationship": relationship,
                        "changed_atom_type": changed_type,
                        "complexity_level": anchor["label"]["complexity_level"],
                        "frequency_band": anchor["label"]["frequency_band"],
                        "scores": {
                            name: int(matrix[i, j]) if name == "cardinality" else round_float(matrix[i, j])
                            for name, matrix in matrices.items()
                        },
                    }
                )
    return sorted(output, key=lambda row: row["pair_id"])


def relationship_scores(rows: Sequence[Mapping[str, Any]], matcher: str, relationship: str) -> list[float]:
    return [float(row["scores"][matcher]) for row in rows if row["relationship"] == relationship]


def auc(positive: Sequence[float], negative: Sequence[float]) -> float:
    if not positive or not negative:
        raise ValueError("AUC requires both classes")
    wins = sum(p > n for p in positive for n in negative)
    ties = sum(p == n for p in positive for n in negative)
    return (wins + 0.5 * ties) / (len(positive) * len(negative))


def eer(positive: Sequence[float], negative: Sequence[float]) -> dict[str, float]:
    values = sorted(set([*positive, *negative]))
    candidates = values + [math.nextafter(max(values), math.inf)]
    observations = []
    for threshold in candidates:
        frr = sum(value < threshold for value in positive) / len(positive)
        far = sum(value >= threshold for value in negative) / len(negative)
        observations.append((abs(frr - far), frr + far, -threshold, threshold, frr, far))
    _, _, _, threshold, frr, far = min(observations)
    return {"threshold": round_float(threshold), "eer": round_float((frr + far) / 2), "frr": round_float(frr), "far": round_float(far)}


def percentile_interval(values: Sequence[float]) -> list[float]:
    return [round_float(np.quantile(values, 0.025)), round_float(np.quantile(values, 0.975))]


def cluster_bootstrap(
    rows: Sequence[Mapping[str, Any]],
    repetitions: int,
    seed: int,
    metric: Callable[[list[Mapping[str, Any]]], float],
) -> list[float]:
    by_family: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_family[row["family_id"]].append(row)
    families = sorted(by_family)
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(repetitions):
        sample = rng.integers(0, len(families), size=len(families))
        sampled_rows = [row for index in sample for row in by_family[families[int(index)]]]
        values.append(float(metric(sampled_rows)))
    return values


def point_metrics(rows: Sequence[Mapping[str, Any]], matcher: str, threshold: float) -> dict[str, float]:
    positive = relationship_scores(rows, matcher, "same")
    near = relationship_scores(rows, matcher, "near_negative")
    random = relationship_scores(rows, matcher, "random_negative")
    decision = threshold_decision(threshold, positive, near, random)
    return {
        "frr": decision.false_reject_rate,
        "near_far": decision.near_false_accept_rate,
        "random_far": decision.random_false_accept_rate,
        "all_negative_auc": auc(positive, [*near, *random]),
        "near_auc": auc(positive, near),
        "same_minus_near_gap": statistics.mean(positive) - statistics.mean(near),
    }


def score_summary(rows: Sequence[Mapping[str, Any]], matcher: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for relationship in ("same", "near_negative", "random_negative"):
        values = relationship_scores(rows, matcher, relationship)
        output[relationship] = {
            "count": len(values),
            "mean": round_float(statistics.mean(values)),
            "median": round_float(statistics.median(values)),
            "standard_deviation": round_float(statistics.stdev(values)) if len(values) > 1 else 0.0,
            "minimum": round_float(min(values)),
            "maximum": round_float(max(values)),
        }
    return output


def bootstrap_primary(
    rows: Sequence[Mapping[str, Any]], matcher: str, threshold: float, config: Mapping[str, Any]
) -> dict[str, Any]:
    repetitions = config["uncertainty"]["bootstrap_repetitions"]
    seed = config["uncertainty"]["bootstrap_seed"]
    metrics = {
        name: cluster_bootstrap(
            rows,
            repetitions,
            seed + offset,
            lambda sample, metric_name=name: point_metrics(sample, matcher, threshold)[metric_name],
        )
        for offset, name in enumerate(
            ["frr", "near_far", "random_far", "all_negative_auc", "near_auc", "same_minus_near_gap"]
        )
    }
    points = point_metrics(rows, matcher, threshold)
    family_count = len({row["family_id"] for row in rows})
    output: dict[str, Any] = {}
    for name, point in points.items():
        interval = percentile_interval(metrics[name])
        if name in {"frr", "near_far", "random_far"} and point == 0:
            interval[1] = max(interval[1], round_float(min(1.0, 3 / family_count)))
        output[name] = {"point": round_float(point), "cluster_bootstrap_95pct": interval}
    return output


def matcher_report(
    pairs: Sequence[Mapping[str, Any]], matcher: str, config: Mapping[str, Any]
) -> dict[str, Any]:
    train = [row for row in pairs if row["split"] == "train"]
    validation = [row for row in pairs if row["split"] == "validation"]
    selected = select_threshold(
        relationship_scores(train, matcher, "same"),
        relationship_scores(train, matcher, "near_negative"),
        relationship_scores(train, matcher, "random_negative"),
    )
    train_points = point_metrics(train, matcher, selected.threshold)
    validation_points = point_metrics(validation, matcher, selected.threshold)
    positive = relationship_scores(validation, matcher, "same")
    negatives = [
        *relationship_scores(validation, matcher, "near_negative"),
        *relationship_scores(validation, matcher, "random_negative"),
    ]
    return {
        "selected_threshold": round_float(selected.threshold),
        "selection_objective": [round_float(value) for value in selected.objective],
        "train": {key: round_float(value) for key, value in train_points.items()},
        "validation": {key: round_float(value) for key, value in validation_points.items()},
        "score_summary": {
            "train": score_summary(train, matcher),
            "validation": score_summary(validation, matcher),
        },
        "validation_uncertainty": bootstrap_primary(validation, matcher, selected.threshold, config),
        "validation_eer_all_negatives": eer(positive, negatives),
        "validation_eer_near_only": eer(
            positive, relationship_scores(validation, matcher, "near_negative")
        ),
    }


def subgroup_report(
    pairs: Sequence[Mapping[str, Any]], matcher: str, threshold: float
) -> dict[str, Any]:
    validation = [row for row in pairs if row["split"] == "validation"]
    output: dict[str, Any] = {"complexity": {}, "frequency_band": {}, "changed_atom_type": {}}
    for field in ("complexity_level", "frequency_band"):
        destination = "complexity" if field == "complexity_level" else field
        for value in sorted({str(row[field]) for row in validation}):
            subset = [row for row in validation if str(row[field]) == value]
            positive = relationship_scores(subset, matcher, "same")
            near = relationship_scores(subset, matcher, "near_negative")
            output[destination][value] = {
                "families": len({row["family_id"] for row in subset}),
                "positive_trials": len(positive),
                "frr": round_float(sum(score < threshold for score in positive) / len(positive)) if positive else None,
                "near_trials": len(near),
                "near_far": round_float(sum(score >= threshold for score in near) / len(near)) if near else None,
            }
    near_rows = [row for row in validation if row["relationship"] == "near_negative"]
    for atom_type in sorted({row["changed_atom_type"] for row in near_rows}):
        subset = [row for row in near_rows if row["changed_atom_type"] == atom_type]
        output["changed_atom_type"][atom_type] = {
            "families": len(subset),
            "near_far": round_float(
                sum(float(row["scores"][matcher]) >= threshold for row in subset) / len(subset)
            ),
            "mean_score": round_float(statistics.mean(float(row["scores"][matcher]) for row in subset)),
        }
    return output


def acceptance_region_report(
    pairs: Sequence[Mapping[str, Any]], matcher: str, config: Mapping[str, Any]
) -> list[dict[str, Any]]:
    validation = [row for row in pairs if row["split"] == "validation"]
    scores = [float(row["scores"][matcher]) for row in validation]
    lower, upper = min(scores), max(scores)
    grid = np.linspace(lower, upper, config["acceptance_region"]["threshold_grid_points"])
    mixture = config["acceptance_region"]["controlled_mixture"]
    output = []
    for threshold in grid:
        metrics = point_metrics(validation, matcher, float(threshold))
        candidate_rows = [row for row in validation if row["relationship"] in {"near_negative", "random_negative"}]
        accepted_by_family: dict[str, int] = defaultdict(int)
        total_by_family: dict[str, int] = defaultdict(int)
        for row in candidate_rows:
            total_by_family[row["family_id"]] += 1
            accepted_by_family[row["family_id"]] += float(row["scores"][matcher]) >= threshold
        region_counts = [accepted_by_family[family] for family in sorted(total_by_family)]
        output.append(
            {
                "threshold": round_float(threshold),
                "frr": round_float(metrics["frr"]),
                "near_acceptance": round_float(metrics["near_far"]),
                "random_acceptance": round_float(metrics["random_far"]),
                "controlled_mixture_acceptance": round_float(
                    mixture["random"] * metrics["random_far"]
                    + mixture["targeted_near"] * metrics["near_far"]
                ),
                "finite_dictionary_mean_accepted": round_float(statistics.mean(region_counts)),
                "finite_dictionary_max_accepted": max(region_counts),
            }
        )
    return output


def partial_information_report(
    pairs: Sequence[Mapping[str, Any]],
    atoms: Mapping[str, set[str]],
    matcher: str,
    threshold: float,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    validation_random = [
        row for row in pairs if row["split"] == "validation" and row["relationship"] == "random_negative"
    ]
    output: dict[str, Any] = {}
    for k in config["acceptance_region"]["partial_information_k"]:
        subset = [
            row
            for row in validation_random
            if len(atoms[row["anchor_row_id"]] & atoms[row["candidate_row_id"]]) >= k
        ]
        output[str(k)] = {
            "candidate_pairs": len(subset),
            "families_with_candidates": len({row["family_id"] for row in subset}),
            "accepted_fraction": (
                round_float(sum(float(row["scores"][matcher]) >= threshold for row in subset) / len(subset))
                if subset
                else None
            ),
            "boundary": "conditioned on shared extracted atoms in the finite validation dictionary",
        }
    return output


def render_svg(curve: Sequence[Mapping[str, Any]], chosen_threshold: float) -> None:
    width, height = 900, 430
    margin_left, margin_top, plot_width, plot_height = 70, 45, 780, 300
    thresholds = [float(row["threshold"]) for row in curve]
    low, high = min(thresholds), max(thresholds)

    def x(value: float) -> float:
        return margin_left + (value - low) / (high - low or 1) * plot_width

    def y(value: float) -> float:
        return margin_top + (1 - value) * plot_height

    series = {
        "FRR": ("frr", "#1f77b4"),
        "near acceptance": ("near_acceptance", "#d62728"),
        "random acceptance": ("random_acceptance", "#ff7f0e"),
        "80/20 controlled attack": ("controlled_mixture_acceptance", "#9467bd"),
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="70" y="25" font-family="sans-serif" font-size="16">P6 validation reliability–acceptance trade-off (controlled weighted text)</text>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333"/>',
    ]
    for index in range(6):
        value = index / 5
        yy = y(value)
        lines.append(f'<line x1="{margin_left}" y1="{yy:.2f}" x2="{margin_left + plot_width}" y2="{yy:.2f}" stroke="#ddd"/>')
        lines.append(f'<text x="35" y="{yy + 4:.2f}" font-family="sans-serif" font-size="11">{value:.1f}</text>')
    for name, (field, color) in series.items():
        points = " ".join(f"{x(float(row['threshold'])):.2f},{y(float(row[field])):.2f}" for row in curve)
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{points}"/>')
    chosen_x = x(chosen_threshold)
    lines.append(f'<line x1="{chosen_x:.2f}" y1="{margin_top}" x2="{chosen_x:.2f}" y2="{margin_top + plot_height}" stroke="#111" stroke-dasharray="5,4"/>')
    lines.append(f'<text x="{chosen_x + 5:.2f}" y="{margin_top + 14}" font-family="sans-serif" font-size="11">train-selected τ={chosen_threshold:.3f}</text>')
    for index, (name, (_, color)) in enumerate(series.items()):
        xx = 75 + index * 195
        lines.append(f'<line x1="{xx}" y1="390" x2="{xx + 24}" y2="390" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<text x="{xx + 30}" y="394" font-family="sans-serif" font-size="11">{name}</text>')
    lines.append('<text x="390" y="420" font-family="sans-serif" font-size="12">inclusive similarity threshold</text>')
    lines.append("</svg>")
    FINAL_PLOT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_analysis(config: Mapping[str, Any]) -> None:
    if not MINILM_ARRAY.exists():
        raise FileNotFoundError("run the embeddings stage first")
    rows = load_selected_rows(config)
    representations, atoms = build_representations(rows, config)
    weights = reconstruct_p5_weights(config)
    dense = np.load(MINILM_ARRAY, allow_pickle=False)
    matrices = build_matrices(rows, atoms, weights, dense)
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    write_jsonl(REPRESENTATIONS, representations)
    row_ids = [row["input"]["row_id"] for row in rows]
    write_json(
        ROW_INDEX,
        {
            "$schema_version": "semantic-secrets-p6-matrix-index-v1",
            "run_id": config["run_id"],
            "row_ids": row_ids,
            "evaluated_splits": config["dataset"]["evaluation_splits"],
            "test_rows": 0,
        },
    )
    matrix_paths = {
        "cardinality": CARDINALITY_MATRIX,
        "jaccard": JACCARD_MATRIX,
        "weighted_overlap": WEIGHTED_MATRIX,
        "minilm_cosine": MINILM_MATRIX,
    }
    for name, path in matrix_paths.items():
        np.save(path, matrices[name], allow_pickle=False)
    pairs = build_pairs(rows, matrices)
    write_jsonl(PAIR_SCORES, pairs)
    reports = {name: matcher_report(pairs, name, config) for name in matrix_paths}
    primary = "weighted_overlap"
    threshold = reports[primary]["selected_threshold"]
    validation_representations = [row for row in representations if row["split"] == "validation"]
    nonempty_rate = sum(bool(row["atoms"]) for row in validation_representations) / len(validation_representations)
    representation_quality = {}
    for split in config["dataset"]["evaluation_splits"]:
        split_rows = [row for row in representations if row["split"] == split]
        warning_counts: dict[str, int] = defaultdict(int)
        for row in split_rows:
            for warning in row["warnings"]:
                warning_counts[warning] += 1
        representation_quality[split] = {
            "rows": len(split_rows),
            "nonempty_rows": sum(bool(row["atoms"]) for row in split_rows),
            "nonempty_rate": round_float(sum(bool(row["atoms"]) for row in split_rows) / len(split_rows)),
            "warning_counts": dict(sorted(warning_counts.items())),
        }
    uncertainty = reports[primary]["validation_uncertainty"]
    bounds = config["viability"]
    checks = {
        "frr_point": uncertainty["frr"]["point"] <= bounds["validation_frr_point_max"],
        "frr_upper": uncertainty["frr"]["cluster_bootstrap_95pct"][1] <= bounds["validation_frr_cluster_95_upper_max"],
        "near_far_point": uncertainty["near_far"]["point"] <= bounds["validation_near_far_point_max"],
        "near_far_upper": uncertainty["near_far"]["cluster_bootstrap_95pct"][1] <= bounds["validation_near_far_cluster_95_upper_max"],
        "random_far_point": uncertainty["random_far"]["point"] <= bounds["validation_random_far_point_max"],
        "random_far_upper": uncertainty["random_far"]["cluster_bootstrap_95pct"][1] <= bounds["validation_random_far_cluster_95_upper_max"],
        "auc_lower": uncertainty["all_negative_auc"]["cluster_bootstrap_95pct"][0] >= bounds["validation_all_negative_auc_cluster_95_lower_min"],
        "gap_lower": uncertainty["same_minus_near_gap"]["cluster_bootstrap_95pct"][0] >= bounds["validation_same_minus_near_gap_cluster_95_lower_min"],
        "nonempty_rate": nonempty_rate >= bounds["validation_nonempty_representation_rate_min"],
    }
    gate_pass = all(checks.values())
    curve = acceptance_region_report(pairs, primary, config)
    render_svg(curve, threshold)
    result = {
        "$schema_version": "semantic-secrets-p6-result-v1",
        "run_id": config["run_id"],
        "publication_result": False,
        "config_sha256": sha256_file(CONFIG),
        "boundaries": {
            "evaluated_families": {"train": 36, "validation": 12},
            "evaluated_rows": len(rows),
            "pilot_test_families_evaluated": 0,
            "pilot_test_rows_evaluated": 0,
            "image_models_executed": 0,
            "human_subjects": 0,
            "calibration": "not meaningful: matcher scores are not asserted probabilities",
            "population_guessability": "not estimated",
        },
        "versions": {
            "canonical_scheme": config["canonicalisation"]["scheme_version"],
            "weights_version": config["weighting"]["weights_version"],
            "weights_sha256": sha256_bytes(canonical_bytes(weights)),
            "catalog_sha256": read_json(MANIFEST_ROOT / "pilot_v1.provenance.json")["catalog_sha256"],
            "minilm_revision": config["minilm"]["revision"],
        },
        "matrix": {
            "rows": len(rows),
            "shape": [len(rows), len(rows)],
            "pair_rows": len(pairs),
            "files": {name: {"path": path.name, "sha256": sha256_file(path)} for name, path in matrix_paths.items()},
            "pair_scores_sha256": sha256_file(PAIR_SCORES),
            "representations_sha256": sha256_file(REPRESENTATIONS),
        },
        "matcher_reports": reports,
        "representation_quality": representation_quality,
        "primary_subgroups_exploratory": subgroup_report(pairs, primary, threshold),
        "acceptance_region": {
            "curve": curve,
            "chosen_threshold_partial_information": partial_information_report(
                pairs, atoms, primary, threshold, config
            ),
            "distribution_boundary": config["acceptance_region"]["boundary"],
        },
        "private_computability": {
            "cardinality": {
                "candidate": "PSI-cardinality or private threshold intersection",
                "expected_work": "linear in credential set sizes plus protocol setup",
                "leakage_boundary": "cardinality leaks if revealed; threshold-only construction preferred",
            },
            "jaccard": {
                "candidate": "private intersection plus public/protected set sizes",
                "expected_work": "set protocol plus integer threshold comparison",
                "leakage_boundary": "sizes and exact similarity must not be revealed by default",
            },
            "weighted_overlap": {
                "candidate": "private weighted intersection and fixed-point threshold comparison",
                "expected_work": "linear token processing with extra fixed-point additions/comparison",
                "leakage_boundary": "weights are frozen research metadata; atoms, overlap, and score remain private",
            },
            "minilm_cosine": {
                "candidate": "MPC/HE private dot product with protected vectors",
                "expected_work": "384-dimensional arithmetic plus normalization/threshold machinery",
                "leakage_boundary": "raw embeddings and exact cosine are linkable/leaky and cannot be stored plaintext",
            },
            "selection": "weighted overlap remains the least implausible private primary only if Gate A passes",
        },
        "gate_a": {
            "predeclared_checks": checks,
            "pass": gate_pass,
            "outcome": "pass" if gate_pass else "stop-or-reframe",
            "protocol_engineering_allowed": gate_pass,
            "reason": (
                "all frozen pilot bounds passed"
                if gate_pass
                else "one or more frozen reliability/near-neighbour bounds failed; P9/P10 protocol engineering remains forbidden"
            ),
        },
        "determinism": {
            "minilm_two_pass_exact": read_json(EMBEDDING_METADATA)["fixed_input_equal"],
            "analysis_outputs_are_timestamp_free": True,
            "bootstrap_seed": config["uncertainty"]["bootstrap_seed"],
            "bootstrap_repetitions": config["uncertainty"]["bootstrap_repetitions"],
        },
        "resources": {
            "minilm": {
                "load_seconds": read_json(EMBEDDING_METADATA)["load_seconds"],
                "two_run_seconds": read_json(EMBEDDING_METADATA)["run_seconds"],
                "peak_cuda_allocated_mib": read_json(EMBEDDING_METADATA)["peak_cuda_allocated_mib"],
            },
            "embedding_array_bytes": MINILM_ARRAY.stat().st_size,
            "matrix_bytes": {name: path.stat().st_size for name, path in matrix_paths.items()},
            "pair_score_bytes": PAIR_SCORES.stat().st_size,
            "representation_bytes": REPRESENTATIONS.stat().st_size,
            "cryptographic_protocol_cost": "not measured because Gate A failed before protocol engineering",
        },
    }
    write_json(FINAL_RESULT, result)
    validate_saved(config)


def validate_saved(config: Mapping[str, Any]) -> None:
    result = read_json(FINAL_RESULT)
    if result["config_sha256"] != sha256_file(CONFIG):
        raise ValueError("P6 config hash mismatch")
    if result["boundaries"]["pilot_test_rows_evaluated"] != 0:
        raise ValueError("pilot test data was evaluated")
    if result["matrix"]["rows"] != 192 or result["matrix"]["shape"] != [192, 192]:
        raise ValueError("P6 matrix dimensions changed")
    for name, details in result["matrix"]["files"].items():
        path = RESULT_ROOT / details["path"]
        if sha256_file(path) != details["sha256"]:
            raise ValueError(f"matrix hash mismatch: {name}")
        if np.load(path, allow_pickle=False).shape != (192, 192):
            raise ValueError(f"matrix shape mismatch: {name}")
    pairs = read_jsonl(PAIR_SCORES)
    if len(pairs) != result["matrix"]["pair_rows"] or any(row["split"] == "test" for row in pairs):
        raise ValueError("pair export boundary mismatch")
    primary_report = result["matcher_reports"]["weighted_overlap"]
    train = [row for row in pairs if row["split"] == "train"]
    selected = select_threshold(
        relationship_scores(train, "weighted_overlap", "same"),
        relationship_scores(train, "weighted_overlap", "near_negative"),
        relationship_scores(train, "weighted_overlap", "random_negative"),
    )
    if round_float(selected.threshold) != primary_report["selected_threshold"]:
        raise ValueError("saved threshold is not the frozen training selection")
    if result["gate_a"]["pass"] != all(result["gate_a"]["predeclared_checks"].values()):
        raise ValueError("Gate A decision is inconsistent")
    print(json.dumps({"validated": str(FINAL_RESULT), "run_id": config["run_id"], "gate_a": result["gate_a"]}, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("embeddings", "analyze", "all"), default="all")
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = read_json(CONFIG)
    if args.validate_only:
        validate_saved(config)
        return
    if args.stage in {"embeddings", "all"}:
        run_embeddings(config)
    if args.stage in {"analyze", "all"}:
        run_analysis(config)


if __name__ == "__main__":
    main()
