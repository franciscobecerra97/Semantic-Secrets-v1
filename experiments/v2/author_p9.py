from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments" / "v2" / "config" / "preregistration_v2.json"
GRAPH_CONFIG = ROOT / "experiments" / "v2" / "config" / "semantic_graph_v2.json"
MANIFEST_DIR = ROOT / "experiments" / "v2" / "manifests"
IMAGE_DIR = ROOT / "artifacts" / "downloads" / "p9_v2" / "capability"

COLOURS = {
    "red": (205, 48, 55), "orange": (232, 129, 45), "yellow": (235, 202, 62),
    "green": (68, 151, 83), "blue": (57, 105, 183), "purple": (130, 78, 164),
    "black": (38, 42, 47), "white": (241, 241, 235), "brown": (132, 91, 57),
    "gray": (130, 137, 145),
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def node(node_id: str, category: str, box: list[float], colour: str, size: str = "medium") -> dict[str, Any]:
    return {"id": node_id, "category": category, "bbox": box, "attributes": {"colour": colour, "size": size}}


def scenario(index: int) -> dict[str, Any]:
    kind = index % 8
    colour_shift = index // 8
    palette = ["red", "blue", "green", "orange", "purple", "brown", "yellow", "gray"]
    c1 = palette[colour_shift % len(palette)]
    c2 = palette[(colour_shift + 3) % len(palette)]
    mirrored = (colour_shift % 2) == 1

    if kind == 0:
        nodes = [node("person1", "person", [0.12, 0.27, 0.39, 0.88], c1, "large"),
                 node("cup1", "cup", [0.33, 0.48, 0.44, 0.65], c2, "small"),
                 node("tree1", "tree", [0.67, 0.16, 0.91, 0.88], "green", "large")]
        unary = [{"node": "person1", "action": "standing"}]
        binary = [{"source": "person1", "type": "holding", "target": "cup1"},
                  {"source": "person1", "type": "left_of", "target": "tree1"}]
        scene = "outdoor"
    elif kind == 1:
        nodes = [node("person1", "person", [0.16, 0.23, 0.40, 0.75], c1, "medium"),
                 node("bicycle1", "bicycle", [0.12, 0.55, 0.48, 0.88], c2, "large"),
                 node("car1", "car", [0.60, 0.55, 0.91, 0.84], "blue", "large")]
        unary = []
        binary = [{"source": "person1", "type": "riding", "target": "bicycle1"},
                  {"source": "bicycle1", "type": "left_of", "target": "car1"}]
        scene = "road"
    elif kind == 2:
        nodes = [node("bird1", "bird", [0.14, 0.17, 0.33, 0.38], c1, "small"),
                 node("bird2", "bird", [0.42, 0.23, 0.60, 0.43], c2, "small"),
                 node("boat1", "boat", [0.31, 0.62, 0.71, 0.85], "brown", "large")]
        unary = [{"node": "bird1", "action": "flying"}, {"node": "bird2", "action": "flying"}]
        binary = [{"source": "bird1", "type": "above", "target": "boat1"},
                  {"source": "bird2", "type": "above", "target": "boat1"}]
        scene = "beach"
    elif kind == 3:
        nodes = [node("cat1", "cat", [0.29, 0.48, 0.55, 0.69], c1, "small"),
                 node("sofa1", "sofa", [0.16, 0.42, 0.79, 0.86], c2, "large"),
                 node("book1", "book", [0.72, 0.30, 0.86, 0.46], "blue", "small")]
        unary = [{"node": "cat1", "action": "sleeping"}]
        binary = [{"source": "cat1", "type": "on", "target": "sofa1"},
                  {"source": "cat1", "type": "left_of", "target": "book1"}]
        scene = "bedroom"
    elif kind == 4:
        nodes = [node("person1", "person", [0.18, 0.30, 0.39, 0.78], c1, "medium"),
                 node("chair1", "chair", [0.14, 0.48, 0.43, 0.87], c2, "medium"),
                 node("table1", "table", [0.55, 0.45, 0.88, 0.83], "brown", "large"),
                 node("laptop1", "laptop", [0.60, 0.34, 0.79, 0.52], "gray", "small")]
        unary = [{"node": "person1", "action": "sitting"}]
        binary = [{"source": "person1", "type": "next_to", "target": "table1"},
                  {"source": "laptop1", "type": "on", "target": "table1"}]
        scene = "office"
    elif kind == 5:
        nodes = [node("dog1", "dog", [0.12, 0.56, 0.37, 0.80], c1, "small"),
                 node("bus1", "bus", [0.55, 0.43, 0.92, 0.80], c2, "large")]
        unary = [{"node": "dog1", "action": "running"}]
        binary = [{"source": "dog1", "type": "left_of", "target": "bus1"}]
        scene = "road"
    elif kind == 6:
        nodes = [node("horse1", "horse", [0.10, 0.39, 0.48, 0.80], c1, "large"),
                 node("flower1", "flower", [0.52, 0.60, 0.62, 0.81], c2, "small"),
                 node("flower2", "flower", [0.65, 0.57, 0.75, 0.81], "yellow", "small"),
                 node("tree1", "tree", [0.78, 0.18, 0.94, 0.82], "green", "large")]
        unary = [{"node": "horse1", "action": "standing"}]
        binary = [{"source": "horse1", "type": "eating", "target": "flower1"},
                  {"source": "horse1", "type": "left_of", "target": "tree1"}]
        scene = "park"
    else:
        nodes = [node("dog1", "dog", [0.32, 0.62, 0.54, 0.82], c1, "small"),
                 node("table1", "table", [0.18, 0.34, 0.68, 0.76], c2, "large"),
                 node("backpack1", "backpack", [0.73, 0.51, 0.88, 0.79], "blue", "small")]
        unary = [{"node": "dog1", "action": "sleeping"}]
        binary = [{"source": "dog1", "type": "under", "target": "table1"},
                  {"source": "table1", "type": "left_of", "target": "backpack1"}]
        scene = "indoor"

    if mirrored:
        for item in nodes:
            x0, y0, x1, y1 = item["bbox"]
            item["bbox"] = [round(1 - x1, 4), y0, round(1 - x0, 4), y1]
        for edge in binary:
            if edge["type"] == "left_of":
                edge["type"] = "right_of"

    layout_rng = random.Random(910000 + index)
    for item in nodes:
        x0, y0, x1, y1 = item["bbox"]
        dx = layout_rng.uniform(-0.025, 0.025)
        dy = layout_rng.uniform(-0.018, 0.018)
        scale = layout_rng.uniform(0.96, 1.04)
        cx, cy = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
        half_w, half_h = (x1 - x0) * scale / 2, (y1 - y0) * scale / 2
        item["bbox"] = [round(max(0.02, cx - half_w), 4), round(max(0.02, cy - half_h), 4),
                        round(min(0.98, cx + half_w), 4), round(min(0.98, cy + half_h), 4)]

    counts = []
    for category, count in sorted(Counter(item["category"] for item in nodes).items()):
        counts.append({"category": category, "bucket": "5_plus" if count >= 5 else str(count)})
    return {"nodes": nodes, "unary": unary, "binary": binary, "counts": counts, "scene": scene}


def px(box: list[float], size: int) -> tuple[int, int, int, int]:
    return tuple(int(round(value * size)) for value in box)  # type: ignore[return-value]


def ellipse(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int], outline=(35, 35, 35), width=3) -> None:
    draw.ellipse(box, fill=fill, outline=outline, width=width)


def render_icon(draw: ImageDraw.ImageDraw, item: dict[str, Any], canvas: int, detailed: bool) -> None:
    x0, y0, x1, y1 = px(item["bbox"], canvas)
    w, h = x1 - x0, y1 - y0
    colour = COLOURS[item["attributes"]["colour"]]
    dark = tuple(max(0, c - 55) for c in colour)
    light = tuple(min(255, c + 45) for c in colour)
    cat = item["category"]
    line = max(2, canvas // 170)

    if detailed:
        draw.rounded_rectangle((x0 + 3, y0 + 5, x1 + 7, y1 + 9), radius=max(4, w // 8), fill=(0, 0, 0, 35))

    if cat == "person":
        ellipse(draw, (x0 + w * 3 // 8, y0, x0 + w * 5 // 8, y0 + h // 4), light, width=line)
        draw.line((x0 + w // 2, y0 + h // 4, x0 + w // 2, y0 + h * 3 // 5), fill=dark, width=line * 3)
        draw.line((x0 + w // 2, y0 + h * 2 // 5, x0 + w // 5, y0 + h // 2), fill=dark, width=line * 2)
        draw.line((x0 + w // 2, y0 + h * 2 // 5, x0 + w * 4 // 5, y0 + h // 2), fill=dark, width=line * 2)
        draw.line((x0 + w // 2, y0 + h * 3 // 5, x0 + w // 4, y1), fill=dark, width=line * 2)
        draw.line((x0 + w // 2, y0 + h * 3 // 5, x0 + w * 3 // 4, y1), fill=dark, width=line * 2)
    elif cat in {"cat", "dog"}:
        ellipse(draw, (x0 + w // 4, y0 + h // 3, x1, y1), colour, width=line)
        ellipse(draw, (x0, y0, x0 + w // 2, y0 + h * 3 // 5), light, width=line)
        if cat == "cat":
            draw.polygon([(x0 + w // 12, y0 + h // 5), (x0 + w // 5, y0), (x0 + w // 3, y0 + h // 4)], fill=colour, outline=dark)
            draw.polygon([(x0 + w // 3, y0 + h // 5), (x0 + w * 5 // 12, y0), (x0 + w // 2, y0 + h // 3)], fill=colour, outline=dark)
        else:
            draw.ellipse((x0 - w // 12, y0 + h // 8, x0 + w // 7, y0 + h // 2), fill=dark)
        draw.arc((x1 - w // 5, y0 + h // 4, x1 + w // 3, y1), 90, 270, fill=dark, width=line * 2)
    elif cat == "horse":
        draw.rounded_rectangle((x0 + w // 5, y0 + h // 3, x1, y0 + h * 3 // 4), radius=w // 8, fill=colour, outline=dark, width=line)
        draw.polygon([(x0 + w // 4, y0 + h // 2), (x0, y0 + h // 5), (x0 + w // 5, y0 + h // 8), (x0 + w // 2, y0 + h // 2)], fill=light, outline=dark)
        for legx in (x0 + w // 3, x0 + w * 4 // 5):
            draw.line((legx, y0 + h * 2 // 3, legx, y1), fill=dark, width=line * 2)
    elif cat == "bird":
        ellipse(draw, (x0 + w // 5, y0 + h // 4, x1, y1), colour, width=line)
        draw.polygon([(x0 + w // 2, y0 + h // 2), (x0, y0), (x0 + w // 3, y0 + h * 3 // 4)], fill=light, outline=dark)
        draw.polygon([(x1, y0 + h // 2), (x1 + w // 5, y0 + h * 3 // 5), (x1, y0 + h * 2 // 3)], fill=(230, 150, 35))
    elif cat in {"car", "bus"}:
        draw.rounded_rectangle((x0, y0 + h // 3, x1, y0 + h * 4 // 5), radius=max(4, h // 8), fill=colour, outline=dark, width=line)
        draw.polygon([(x0 + w // 5, y0 + h // 3), (x0 + w // 3, y0), (x0 + w * 3 // 4, y0), (x0 + w * 9 // 10, y0 + h // 3)], fill=light, outline=dark)
        for cx in (x0 + w // 4, x0 + w * 3 // 4):
            ellipse(draw, (cx - h // 8, y0 + h * 3 // 4, cx + h // 8, y1), (35, 35, 35), width=line)
    elif cat == "bicycle":
        r = min(w // 4, h // 3)
        c1, c2 = (x0 + r, y1 - r), (x1 - r, y1 - r)
        ellipse(draw, (c1[0] - r, c1[1] - r, c1[0] + r, c1[1] + r), (235, 235, 230), width=line)
        ellipse(draw, (c2[0] - r, c2[1] - r, c2[0] + r, c2[1] + r), (235, 235, 230), width=line)
        mid = (x0 + w // 2, y0 + h // 2)
        draw.line((c1, mid, c2, c1), fill=colour, width=line * 2)
        draw.line((mid, x0 + w * 3 // 5, y0 + h // 4, c2), fill=colour, width=line * 2)
    elif cat == "boat":
        draw.polygon([(x0, y0 + h // 2), (x1, y0 + h // 2), (x0 + w * 4 // 5, y1), (x0 + w // 5, y1)], fill=colour, outline=dark)
        draw.polygon([(x0 + w // 2, y0), (x0 + w // 2, y0 + h // 2), (x0 + w * 4 // 5, y0 + h // 2)], fill=light, outline=dark)
    elif cat in {"sofa", "chair"}:
        draw.rounded_rectangle((x0, y0 + h // 4, x1, y1), radius=max(5, w // 10), fill=colour, outline=dark, width=line)
        draw.rectangle((x0 + w // 8, y0, x1 - w // 8, y0 + h * 2 // 3), fill=light, outline=dark, width=line)
        draw.line((x0 + w // 5, y1, x0 + w // 6, y1 + h // 8), fill=dark, width=line * 2)
        draw.line((x1 - w // 5, y1, x1 - w // 6, y1 + h // 8), fill=dark, width=line * 2)
    elif cat == "table":
        draw.rounded_rectangle((x0, y0, x1, y0 + h // 4), radius=max(3, h // 12), fill=colour, outline=dark, width=line)
        draw.line((x0 + w // 6, y0 + h // 4, x0 + w // 6, y1), fill=dark, width=line * 3)
        draw.line((x1 - w // 6, y0 + h // 4, x1 - w // 6, y1), fill=dark, width=line * 3)
    elif cat == "tree":
        draw.rectangle((x0 + w * 2 // 5, y0 + h // 2, x0 + w * 3 // 5, y1), fill=COLOURS["brown"], outline=dark)
        ellipse(draw, (x0, y0, x1, y0 + h * 3 // 5), colour, width=line)
        ellipse(draw, (x0 + w // 5, y0 - h // 8, x1, y0 + h // 2), light, width=line)
    elif cat == "flower":
        draw.line((x0 + w // 2, y0 + h // 3, x0 + w // 2, y1), fill=COLOURS["green"], width=line * 2)
        for angle in range(0, 360, 72):
            cx = x0 + w // 2 + int(math.cos(math.radians(angle)) * w // 4)
            cy = y0 + h // 4 + int(math.sin(math.radians(angle)) * h // 6)
            ellipse(draw, (cx - w // 6, cy - h // 8, cx + w // 6, cy + h // 8), colour, width=line)
        ellipse(draw, (x0 + w * 2 // 5, y0 + h // 7, x0 + w * 3 // 5, y0 + h // 3), COLOURS["yellow"], width=line)
    elif cat == "cup":
        draw.rounded_rectangle((x0, y0, x0 + w * 3 // 4, y1), radius=max(3, w // 8), fill=colour, outline=dark, width=line)
        draw.arc((x0 + w // 2, y0 + h // 4, x1, y0 + h * 3 // 4), 250, 110, fill=dark, width=line * 2)
    elif cat in {"book", "laptop"}:
        draw.rectangle((x0, y0, x1, y1), fill=colour, outline=dark, width=line)
        if cat == "book":
            draw.line((x0 + w // 5, y0, x0 + w // 5, y1), fill=light, width=line)
        else:
            draw.rectangle((x0 + w // 8, y0 + h // 8, x1 - w // 8, y1 - h // 4), fill=(170, 205, 225), outline=dark)
    elif cat == "backpack":
        draw.rounded_rectangle((x0, y0 + h // 5, x1, y1), radius=max(4, w // 5), fill=colour, outline=dark, width=line)
        draw.arc((x0 + w // 4, y0, x1 - w // 4, y0 + h // 2), 180, 360, fill=dark, width=line * 2)
        draw.rectangle((x0 + w // 5, y0 + h * 3 // 5, x1 - w // 5, y1 - h // 10), outline=light, width=line)
    else:
        draw.rounded_rectangle((x0, y0, x1, y1), radius=max(4, w // 8), fill=colour, outline=dark, width=line)


def draw_background(draw: ImageDraw.ImageDraw, scene_name: str, size: int, detailed: bool) -> None:
    sky = (201, 226, 242) if detailed else (224, 239, 247)
    indoor = scene_name in {"indoor", "bedroom", "office", "kitchen"}
    if indoor:
        draw.rectangle((0, 0, size, size * 3 // 4), fill=(238, 229, 211))
        draw.rectangle((0, size * 3 // 4, size, size), fill=(179, 146, 112))
        if scene_name == "office":
            for x in range(size // 8, size, size // 4):
                draw.rectangle((x, size // 10, x + size // 8, size // 3), fill=(184, 220, 235), outline=(100, 120, 130), width=2)
    else:
        draw.rectangle((0, 0, size, size * 2 // 3), fill=sky)
        ground = (102, 174, 92)
        if scene_name == "road": ground = (104, 109, 116)
        if scene_name == "beach": ground = (232, 205, 138)
        draw.rectangle((0, size * 2 // 3, size, size), fill=ground)
        if scene_name == "road":
            draw.line((0, size * 5 // 6, size, size * 5 // 6), fill=(245, 220, 76), width=5)
        if scene_name == "beach":
            draw.rectangle((0, size // 2, size, size * 2 // 3), fill=(73, 158, 205))


def render_fixture(spec: dict[str, Any], path: Path, size: int = 512) -> None:
    detailed = spec["fixture_style"] == "synthetic_raster"
    image = Image.new("RGB", (size, size), (240, 240, 235))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_background(draw, spec["graph"]["scene"], size, detailed)
    if detailed:
        rng = random.Random(spec["seed"])
        for _ in range(160):
            x, y = rng.randrange(size), rng.randrange(size)
            r = rng.randrange(1, 4)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255, rng.randrange(8, 28)))
    for item in sorted(spec["graph"]["nodes"], key=lambda value: value["bbox"][1]):
        render_icon(draw, item, size, detailed)
    if detailed:
        image = image.filter(ImageFilter.GaussianBlur(radius=0.25))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def author_capability() -> dict[str, Any]:
    prereg = read_json(CONFIG)
    graph_config = read_json(GRAPH_CONFIG)
    expected = prereg["data"]["capability_images"]
    total = expected["development"] + expected["validation"]
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for index in range(total):
        split = "development" if index < expected["development"] else "validation"
        fixture_id = f"cap-v2-{index:03d}"
        fixture_style = "procedural_composite" if index % 2 == 0 else "synthetic_raster"
        spec = {
            "fixture_id": fixture_id,
            "split": split,
            "fixture_style": fixture_style,
            "seed": 920000 + index,
            "graph_version": graph_config["$schema_version"],
            "graph": scenario(index),
            "licence": "project-authored; repository licence",
            "human_subjects": False,
        }
        image_path = IMAGE_DIR / f"{fixture_id}.png"
        render_fixture(spec, image_path)
        spec["image_sha256"] = stable_hash(image_path)
        spec["image_relpath"] = display_path(image_path)
        records.append(spec)

    manifest_path = MANIFEST_DIR / "capability_v2.jsonl"
    manifest_path.write_text("".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in records), encoding="utf-8")
    validation = [record for record in records if record["split"] == "validation"]
    audit = {
        "manifest": display_path(manifest_path),
        "manifest_sha256": stable_hash(manifest_path),
        "record_count": len(records),
        "split_counts": dict(Counter(record["split"] for record in records)),
        "style_counts": dict(Counter(record["fixture_style"] for record in records)),
        "unique_image_hashes": len({record["image_sha256"] for record in records}),
        "all_image_hashes_unique": len({record["image_sha256"] for record in records}) == len(records),
        "task_positive_counts_validation": {
            "object": sum(len(record["graph"]["nodes"]) for record in validation),
            "attribute": sum(len(node["attributes"]) for record in validation for node in record["graph"]["nodes"]),
            "count": sum(len(record["graph"]["counts"]) for record in validation),
            "action": sum(len(record["graph"]["unary"]) + sum(edge["type"] in graph_config["binary_actions"] for edge in record["graph"]["binary"]) for record in validation),
            "relation": sum(sum(edge["type"] in graph_config["spatial_relations"] for edge in record["graph"]["binary"]) for record in validation),
            "scene": sum(record["graph"]["scene"] is not None for record in validation),
        },
        "task_applicable_negative_counts_validation": {
            "object": sum(len(graph_config["entity_categories"]) - len({node["category"] for node in record["graph"]["nodes"]}) for record in validation),
            "attribute": sum(
                sum(len(graph_config["attributes"][key]) - 1 for key in node["attributes"])
                for record in validation for node in record["graph"]["nodes"]
            ),
            "count": sum(len(graph_config["entity_categories"]) * len(graph_config["count_buckets"]) - len(record["graph"]["counts"]) for record in validation),
            "action": sum(
                len(record["graph"]["nodes"]) * len(graph_config["unary_actions"])
                + len(record["graph"]["nodes"]) * (len(record["graph"]["nodes"]) - 1) * len(graph_config["binary_actions"])
                - len(record["graph"]["unary"])
                - sum(edge["type"] in graph_config["binary_actions"] for edge in record["graph"]["binary"])
                for record in validation
            ),
            "relation": sum(
                len(record["graph"]["nodes"]) * (len(record["graph"]["nodes"]) - 1) * len(graph_config["spatial_relations"])
                - sum(edge["type"] in graph_config["spatial_relations"] for edge in record["graph"]["binary"])
                for record in validation
            ),
            "scene": sum(len(graph_config["scenes"]) - 1 for _record in validation),
        },
        "v1_sources_accessed": False,
        "image_directory_committed": False,
    }
    audit_path = MANIFEST_DIR / "capability_v2.audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["capability"])
    args = parser.parse_args()
    if args.command == "capability":
        print(json.dumps(author_capability(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
