"""Deterministically author and independently audit the 60-family pilot catalog."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from experiments.datasets.split_manifest import atom_signature, validate_catalog


ROOT = Path(__file__).resolve().parent
SMOKE = ROOT / "concepts" / "smoke_v1.json"
ONTOLOGY = ROOT / "ontology_v1.json"
OUTPUT = ROOT / "concepts" / "pilot_v1.json"
AUDIT_OUTPUT = ROOT / "concepts" / "pilot_v1.audit.json"

OBJECT_VARIANTS = {
    "bicycle": ["scooter", "tricycle", "wagon", "skateboard", "wheelbarrow"],
    "motorcycle": ["moped", "car", "tractor", "canoe", "sled"],
    "cat": ["rabbit", "goat", "panda", "tiger", "horse"],
    "scarf": ["hat", "ribbon", "blanket", "cape", "vest"],
    "dog": ["fox", "seal", "otter", "monkey", "bear"],
    "frisbee": ["ball", "ring", "rope", "stick", "disk"],
    "cup": ["lamp", "vase", "bottle", "basket", "helmet"],
    "book": ["chair", "box", "clock", "lantern", "bench"],
    "sailboat": ["canoe", "kayak", "raft", "ship", "yacht"],
    "axolotl": ["lizard", "gecko", "iguana", "salamander", "frog"],
    "fox": ["deer", "wolf", "badger", "raccoon", "boar"],
    "tree": ["tower", "pole", "cactus", "statue", "fountain"],
    "boulder": ["barrel", "bench", "crate", "rock", "log"],
    "robot": ["painter", "farmer", "doctor", "pilot", "dancer"],
    "box": ["basket", "suitcase", "crate", "chest", "bucket"],
    "chef": ["clown", "artist", "child", "person", "robot"],
    "orange": ["apple", "ball", "plate", "bottle", "peach"],
    "teapot": ["kettle", "jar", "pitcher", "cup", "bowl"],
    "owl": ["eagle", "parrot", "raven", "falcon", "goose"],
    "clock": ["lantern", "mirror", "window", "bell", "sign"],
}

ATTRIBUTE_VARIANTS = {
    "red": ["black", "green", "purple", "brown", "yellow"],
    "blue": ["white", "yellow", "orange", "gray", "red"],
    "yellow": ["red", "blue", "white", "purple", "black"],
    "green": ["blue", "red", "gray", "orange", "white"],
    "bright": ["red", "yellow", "orange", "white", "green"],
    "glass": ["metal", "paper", "wooden", "wood", "glass"],
    "ceramic": ["wooden", "wood", "paper", "metal", "paper"],
    "white": ["brown", "green", "yellow", "gray", "black"],
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def plural(value: str) -> str:
    if value.endswith(("s", "x", "z", "ch", "sh")):
        return value + "es"
    if value.endswith("y") and value[-2:] not in {"ay", "ey", "iy", "oy", "uy"}:
        return value[:-1] + "ies"
    return value + "s"


def cycle_maps(cycle: int) -> tuple[dict[str, str], dict[str, str]]:
    objects = {source: variants[cycle] for source, variants in OBJECT_VARIANTS.items()}
    attributes = {source: variants[cycle] for source, variants in ATTRIBUTE_VARIANTS.items()}
    return objects, attributes


def transform_text(text: str, objects: dict[str, str], attributes: dict[str, str]) -> str:
    replacements: dict[str, str] = {}
    for source, target in objects.items():
        replacements[source] = target.replace("_", " ")
        replacements[plural(source)] = plural(target).replace("_", " ")
    replacements["scarfed"] = objects["scarf"].replace("_", " ") + "-wearing"
    replacements.update({source: target.replace("_", " ") for source, target in attributes.items()})
    replacements["brightly coloured"] = attributes["bright"]
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(key) for key in sorted(replacements, key=len, reverse=True)) + r")\b", re.I)

    def replace(match: re.Match[str]) -> str:
        original = match.group(0)
        replacement = replacements[original.casefold()]
        return replacement.capitalize() if original[:1].isupper() else replacement

    transformed = pattern.sub(replace, text)
    transformed = re.sub(r"\bAn ([^aeiouAEIOU])", r"A \1", transformed)
    transformed = re.sub(r"\bA ([aeiouAEIOU])", r"An \1", transformed)
    return transformed


def transform_atom(atom: dict[str, Any], objects: dict[str, str], attributes: dict[str, str]) -> dict[str, Any]:
    transformed = deepcopy(atom)
    for field in ("id", "subject", "object", "object2"):
        if field in transformed:
            transformed[field] = objects.get(transformed[field], transformed[field])
    if transformed["type"] == "object":
        transformed["value"] = objects.get(transformed["value"], transformed["value"])
    elif transformed["type"] == "attribute":
        transformed["value"] = attributes.get(transformed["value"], transformed["value"])
    return transformed


def transform_concept(
    concept: dict[str, Any],
    concept_id: str,
    objects: dict[str, str],
    attributes: dict[str, str],
) -> dict[str, Any]:
    return {
        "concept_id": concept_id,
        "prompts": {
            key: transform_text(value, objects, attributes)
            for key, value in concept["prompts"].items()
        },
        "atoms": [transform_atom(atom, objects, attributes) for atom in concept["atoms"]],
    }


def author_catalog() -> dict[str, Any]:
    smoke = read_json(SMOKE)
    families: list[dict[str, Any]] = []
    family_number = 0
    for cycle in range(5):
        objects, attributes = cycle_maps(cycle)
        for source in smoke["families"]:
            family_number += 1
            base_id = f"c{family_number:03d}a"
            near_id = f"c{family_number:03d}b"
            base = transform_concept(source["base"], base_id, objects, attributes)
            near = transform_concept(source["near_neighbours"][0], near_id, objects, attributes)
            removed = sorted(
                {atom_signature(atom) for atom in base["atoms"]}
                - {atom_signature(atom) for atom in near["atoms"]}
            )
            added = sorted(
                {atom_signature(atom) for atom in near["atoms"]}
                - {atom_signature(atom) for atom in base["atoms"]}
            )
            if len(removed) != 1 or len(added) != 1:
                raise ValueError(f"template transformation changed more than one atom: {family_number}")
            atom_type = removed[0].split("|", 1)[0]
            near["change"] = {
                "atom_type": atom_type,
                "from_signature": removed[0],
                "to_signature": added[0],
            }
            families.append(
                {
                    "family_id": f"f{family_number:03d}",
                    "complexity_level": source["complexity_level"],
                    "frequency_band": source["frequency_band"],
                    "base": base,
                    "near_neighbours": [near],
                    "audit_notes": (
                        f"Pilot authoring cycle {cycle + 1}; transformed audited template "
                        f"{source['family_id']} with one {atom_type} replacement."
                    ),
                }
            )
    return {
        "$schema_version": "semantic-secrets-concept-catalog-v1",
        "catalog_id": "controlled-pilot-v1",
        "ontology_id": "controlled-ontology-v1",
        "audit_status": "author-pass-complete",
        "families": families,
    }


ACTION_FORMS = {
    "carry": ("carry", "carries", "carrying"),
    "catch": ("catch", "catches", "catching"),
    "hold": ("hold", "holds", "holding"),
    "juggle": ("juggle", "juggles", "juggling"),
    "read": ("read", "reads", "reading"),
    "ride": ("ride", "rides", "riding"),
    "sleep": ("sleep", "sleeps", "sleeping"),
    "watch": ("watch", "watches", "watching"),
}
RELATION_FORMS = {
    "above": ("above", "over"),
    "behind": ("behind",),
    "below": ("below", "under"),
    "beside": ("beside", "next to"),
    "between": ("between", "one side"),
    "in_front_of": ("in front of",),
    "inside": ("inside",),
    "left_of": ("left of", "left hand side", "left side"),
    "on": (" on ",),
    "right_of": ("right of", "right hand side", "right side"),
    "under": ("under",),
}
NUMBER_FORMS = {"1": ("one", "single", "exactly one"), "2": ("two", "pair"), "3": ("three",), "4": ("four",)}


def contains(text: str, forms: tuple[str, ...]) -> bool:
    padded = " " + text.casefold() + " "
    return any(re.search(rf"\b{re.escape(form.strip())}\b", padded) for form in forms)


def audit_prompt(prompt: str, atoms: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    lowered = prompt.casefold().replace("-", " ")
    for atom in atoms:
        atom_type, value = atom["type"], atom["value"]
        if atom_type == "object":
            forms = (value.replace("_", " "), plural(value).replace("_", " "))
        elif atom_type == "action":
            forms = ACTION_FORMS[value]
        elif atom_type == "relation":
            forms = RELATION_FORMS[value]
        elif atom_type == "scene":
            forms = {
                "coastal_sunrise": ("coastal sunrise", "coast at sunrise", "sunrise", "sun rises"),
                "coastal_night": ("coastal night", "coast at night", "at night", "night"),
            }.get(value, (value.replace("_", " "),))
        elif atom_type == "count":
            forms = (value, *NUMBER_FORMS[value])
        else:
            forms = (value.replace("_", " "),)
        if not contains(lowered, forms):
            issues.append(f"missing {atom_type}:{value}")
    return issues


def blind_audit(catalog: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    for family in catalog["families"]:
        for concept in [family["base"], *family["near_neighbours"]]:
            for prompt_name, prompt in concept["prompts"].items():
                prompt_issues = audit_prompt(prompt, concept["atoms"])
                if prompt_issues:
                    issues.append(
                        {
                            "concept_id": concept["concept_id"],
                            "prompt_variant": prompt_name,
                            "issues": prompt_issues,
                        }
                    )
    if issues:
        raise ValueError(f"pilot blind audit failed: {issues[:5]}")
    audited = deepcopy(catalog)
    audited["audit_status"] = "blind-audit-complete"
    ontology = read_json(ONTOLOGY)
    validation = validate_catalog(audited, ontology, 60)
    return {
        "audit_id": "controlled-pilot-v1-blind-audit",
        "method": "label-only deterministic lexical audit independent of matcher/model outputs",
        "model_outputs_observed": False,
        "families_checked": 60,
        "concepts_checked": 120,
        "prompt_variants_checked": 360,
        "issues": [],
        "validation": validation,
        "catalog": audited,
    }


def main() -> None:
    authored = author_catalog()
    audit = blind_audit(authored)
    catalog = audit.pop("catalog")
    OUTPUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    audit["catalog_sha256"] = hashlib.sha256(canonical_bytes(catalog)).hexdigest()
    AUDIT_OUTPUT.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
