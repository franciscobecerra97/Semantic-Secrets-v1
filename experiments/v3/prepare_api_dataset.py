"""Author/materialize public P9-v3 fixtures; never infer naturalistic labels.

Run from the repository root: python -m experiments.v3.prepare_api_dataset prepare
and node experiments/v3/generate_remote_dataset.mjs --execute
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import importlib.metadata
import platform
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "artifacts/downloads/p9_v3"
CONFIG = ROOT / "experiments/v3/config/remote_generation_v3_4.json"
PALETTE = {"red": "#db3434", "blue": "#2876ca", "green": "#299955", "yellow": "#e5ba28", "purple": "#9753b6"}
# A family is an interaction/object/setting concept. Five views/colours remain
# within that family. No family moves between development and validation.
FAMILIES = [
    ("holding", "book", "indoor"), ("holding", "cup", "outdoor"),
    ("holding", "bottle", "indoor"), ("holding", "flower", "outdoor"),
    ("holding", "umbrella", "outdoor"), ("holding", "phone", "indoor"),
    ("wearing", "hat", "outdoor"), ("using", "laptop", "indoor"),
    ("holding", "plate", "indoor"), ("looking_at", "cat", "indoor"),
    ("looking_at", "dog", "outdoor"), ("carrying", "book", "outdoor"),
    ("carrying", "umbrella", "indoor"), ("carrying", "bottle", "outdoor"),
    ("using", "phone", "outdoor"), ("looking_at", "flower", "indoor"),
    ("holding", "hat", "indoor"), ("carrying", "laptop", "outdoor"),
    ("looking_at", "book", "indoor"), ("carrying", "plate", "outdoor"),
    ("using", "cup", "indoor"), ("looking_at", "bottle", "outdoor"),
    ("looking_at", "umbrella", "indoor"), ("holding", "cat", "outdoor"),
]
VIEWS = ["front view", "three-quarter view from the left", "side view", "three-quarter view from the right", "slightly elevated view"]


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_once(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    if p.exists():
        if p.read_bytes() != payload:
            raise ValueError(f"Refusing to overwrite different content: {p}")
    else:
        with p.open("xb") as f:
            f.write(payload)


def save_png(p, image):
    import io
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=False, compress_level=9)
    payload = stream.getvalue()
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        if p.read_bytes() != payload:
            raise ValueError(f"Refusing to overwrite changed image {p}")
    else:
        with p.open("xb") as f:
            f.write(payload)


def atom(kind, value, source=None, target=None, scope=None):
    return {"reference_atom_id": "", "atom_type": kind, "value": str(value),
            "source_reference_id": source, "target_reference_id": target, "scope_category": scope}


def geometry(entities):
    """Same declared box geometry as compiler, retaining all true alternatives."""
    out = []
    for a in entities:
        for b in entities:
            if a is b:
                continue
            x, y = a["bbox_xyxy"], b["bbox_xyxy"]
            aw, ah, bw, bh = x[2]-x[0], x[3]-x[1], y[2]-y[0], y[3]-y[1]
            iw, ih = max(0, min(x[2],y[2])-max(x[0],y[0])), max(0,min(x[3],y[3])-max(x[1],y[1]))
            inter = iw*ih
            ax, ay, bx, by = (x[0]+x[2])/2, (x[1]+x[3])/2, (y[0]+y[2])/2, (y[1]+y[3])/2
            values = []
            if ax + .05 <= bx: values.append("left_of")
            if ay + .05 <= by: values.append("above")
            if inter/(aw*ah) >= .90: values.append("inside")
            if abs(x[3]-y[1]) <= .08 and iw/aw >= .50: values.append("on")
            if abs(x[1]-y[3]) <= .08 and iw/aw >= .50: values.append("under")
            # Symmetric facts use the same entity ordering as canonical node IDs.
            if (a["category"], x, a["reference_id"]) < (b["category"], y, b["reference_id"]):
                if inter/(aw*ah+bw*bh-inter) >= .20: values.append("overlap")
                if math.dist((ax,ay),(bx,by)) <= .25: values.append("near")
            out.extend(atom("geometry_relation", v, a["reference_id"], b["reference_id"]) for v in values)
    return out


def sprite(category, colour, striped=False, interaction="holding"):
    """Project-authored pictograms, not downloaded/model-generated assets."""
    im = Image.new("RGBA", (240, 360))
    d = ImageDraw.Draw(im)
    ink, c = "#28323d", PALETTE[colour]
    if category == "person":
        d.ellipse((63, 0, 121, 61), fill="#dda77f", outline=ink, width=3)
        d.pieslice((62, -7, 123, 43), 180, 345, fill="#4c3527")
        d.ellipse((104, 23, 110, 29), fill=ink)
        d.rounded_rectangle((45, 65, 137, 223), 15, fill=c, outline=ink, width=3)
        if striped:
            for yy in range(83,212,24): d.rectangle((49,yy,133,yy+7), fill="#f5f0de")
        d.line([(66,218),(64,322),(44,350)], fill=ink, width=25)
        d.line([(115,218),(124,321),(146,350)], fill=ink, width=25)
        d.line([(54,81),(16,151),(28,213)], fill=c, width=23)
        d.ellipse((15,201,39,226), fill="#dda77f", outline=ink, width=2)
        end = (225, 140) if interaction not in {"wearing", "looking_at"} else (168, 191)
        d.line([(127,85),(163,150),end], fill=c, width=23)
        d.ellipse((end[0]-12,end[1]-12,end[0]+12,end[1]+12), fill="#dda77f", outline=ink, width=2)
    elif category == "book":
        d.polygon([(5,20),(110,6),(233,25),(233,335),(117,354),(5,335)], fill=c, outline=ink, width=6)
        d.line([(115,12),(115,345)], fill="#f1e7c9", width=9)
        for yy in range(65,300,38):
            d.line((22,yy,94,yy-6), fill="#f1e7c9", width=4)
            d.line((135,yy-6,215,yy), fill="#f1e7c9", width=4)
    elif category == "cup":
        d.ellipse((133,74,235,266), outline=ink, width=17)
        d.rounded_rectangle((5,30,172,330), 28, fill=c, outline=ink, width=7)
        d.ellipse((6,12,172,60), fill="#50392b", outline=ink, width=6)
    elif category == "bottle":
        d.rounded_rectangle((72,1,163,65), 8, fill=c, outline=ink, width=5)
        d.polygon([(77,61),(158,61),(209,127),(211,350),(28,350),(30,127)], fill=c, outline=ink, width=6)
        d.rounded_rectangle((40,160,197,267), 7, fill="#f1e7c9", outline=ink, width=3)
        d.line((60,111,60,145), fill="#ffffff", width=10)
    elif category == "flower":
        d.line((120,139,120,352), fill="#2e874b", width=14)
        d.ellipse((24,216,117,266), fill="#409e51", outline=ink, width=3)
        d.ellipse((122,262,217,309), fill="#409e51", outline=ink, width=3)
        for xx,yy in [(120,40),(175,77),(162,139),(79,139),(61,77)]:
            d.ellipse((xx-36,yy-35,xx+36,yy+35), fill=c, outline=ink, width=3)
        d.ellipse((87,71,151,131), fill="#e6bb34", outline=ink, width=4)
    elif category == "umbrella":
        # Lean the shaft toward the authored hand, instead of leaving a gap.
        d.line((121,80,45,315), fill=ink, width=9)
        d.arc((1,274,54,354), 0,180, fill=ink, width=10)
        d.pieslice((1,1,238,228),180,360, fill=c, outline=ink, width=5)
        d.line((2,115,236,115), fill=ink, width=5)
        d.line((120,4,52,114), fill="#f2e7cc", width=5)
        d.line((120,4,188,114), fill="#f2e7cc", width=5)
    elif category == "phone":
        d.rounded_rectangle((19,1,220,358),24, fill=c, outline=ink, width=7)
        d.rounded_rectangle((32,37,207,310),8, fill="#a6cee2", outline=ink, width=4)
        d.ellipse((104,324,134,347), fill=ink)
    elif category == "hat":
        d.rounded_rectangle((42,2,195,260),24, fill=c, outline=ink, width=6)
        d.rectangle((46,200,191,249), fill=ink)
        d.ellipse((2,243,237,354),fill=c, outline=ink, width=6)
    elif category == "laptop":
        d.rounded_rectangle((17,1,223,249), 9, fill=ink)
        d.rectangle((28,16,212,231), fill=c)
        d.polygon([(17,251),(223,251),(239,350),(1,350)], fill="#abb4bb", outline=ink, width=5)
        for yy in range(272,325,17): d.line((27,yy,213,yy), fill=ink, width=4)
    elif category == "plate":
        d.ellipse((2,2,237,357), fill=c, outline=ink, width=6)
        d.ellipse((32,45,208,310), outline="#ece6db", width=12)
    elif category in {"cat", "dog"}:
        d.ellipse((51,115,200,297), fill=c, outline=ink, width=5)
        d.ellipse((38,18,171,151),fill=c, outline=ink,width=5)
        if category == "cat":
            d.polygon([(45,52),(43,1),(92,27)],fill=c,outline=ink,width=4)
            d.polygon([(126,26),(173,1),(169,69)],fill=c,outline=ink,width=4)
            d.arc((163,183,239,307),260,95,fill=ink,width=15)
        else:
            d.ellipse((11,27,57,167),fill="#74513b",outline=ink,width=4)
            d.ellipse((157,27,201,167),fill="#74513b",outline=ink,width=4)
            d.line((187,186,229,151),fill=ink,width=14)
        for xx in [79,129]: d.ellipse((xx,63,xx+12,79),fill=ink)
        d.ellipse((96,94,116,111),fill=ink)
        for xx in [70,151]: d.rounded_rectangle((xx,262,xx+32,357),12,fill=c,outline=ink,width=4)
    elif category == "table":
        d.rectangle((16,73,37,358),fill="#9f683c",outline=ink,width=5)
        d.rectangle((201,73,223,358),fill="#9f683c",outline=ink,width=5)
        d.rounded_rectangle((1,1,238,90), 6, fill="#bb874d",outline=ink,width=5)
        for yy in range(15,80,15): d.line((9,yy,229,yy+4),fill="#87572f",width=3)
    else:
        raise ValueError(f"No authored sprite for {category}")
    bounds = im.getbbox()
    return im.crop(bounds)


def controlled_scenario(family, variant):
    relation, target, scene = FAMILIES[family-1]
    local = (family-1)%12+1
    colour = list(PALETTE)[variant-1]
    actor_box = [.13, .18, .57, .91]
    object_box = [.52, .40, .73, .65]
    if target == "umbrella": object_box = [.43,.05,.91,.62]
    if relation == "wearing": object_box = [.245,.10,.365,.23]
    if target in {"cat","dog"}:
        object_box = [.62,.56,.90,.91] if relation=="looking_at" else [.52,.36,.80,.70]
    if target == "laptop": object_box = [.53,.43,.86,.67]
    # Five deterministic composition variants, including left/right inversions.
    shift = (variant-3)*.012
    boxes = [actor_box, object_box]
    if local >= 7: boxes.append([.64,.73,.96,.96])
    boxes = [[round(max(0,min(1,v+(shift if i%2==0 else 0))),5) for i,v in enumerate(b)] for b in boxes]
    if variant in {2,4}:
        boxes = [[round(1-b[2],5),b[1],round(1-b[0],5),b[3]] for b in boxes]
    entities = [{"reference_id":"r1","category":"person","bbox_xyxy":boxes[0]},
                {"reference_id":"r2","category":target,"bbox_xyxy":boxes[1]}]
    if local >= 7: entities.append({"reference_id":"r3","category":"table","bbox_xyxy":boxes[2]})
    atoms = [atom("entity",e["category"],e["reference_id"]) for e in entities]
    atoms += [atom("colour",colour,"r1"), atom("size","small","r2"),
              atom("pattern","striped" if variant%2 else "solid","r1"),
              atom("binary_interaction",relation,"r1","r2"),atom("unary_action","standing","r1"),atom("scene",scene)]
    if local>=7: atoms.append(atom("material","wood","r3"))
    for category,count in sorted(Counter(e["category"] for e in entities).items()): atoms.append(atom("count",count,scope=category))
    atoms += geometry(entities)
    for n,a in enumerate(atoms): a["reference_atom_id"] = f"a{n:03d}"
    image_id = f"cap-v3-A-F{family:02d}-{variant:02d}"
    return {"schema_version":"capability-scenario-specification-v3.2.0", "scenario_specification_id":f"scenario-{image_id}",
            "image_id":image_id,"family_id":f"F{family:02d}","stratum":"A_controlled_geometric",
            "split":"development" if family<=12 else "validation", "authoring_method":"controlled_scene_specification",
            "model_output_blind":True,"reference_entities":entities,"reference_atoms":atoms}


def prompt_row(family, variant):
    relation, obj, scene = FAMILIES[family-1]
    colour = list(PALETTE)[variant-1]
    action = {"looking_at":"looking at", "using":"using", "carrying":"carrying", "holding":"holding", "wearing":"wearing"}[relation]
    extra = " A wooden table is clearly visible next to the person." if (family-1)%12>=6 else ""
    prompt = (f"A realistic photograph, {VIEWS[variant-1]}, full body. One adult person in a {colour} "
              f"{'striped' if variant%2 else 'plain solid-colour'} shirt, standing {'inside a simple room' if scene=='indoor' else 'outside in daylight'}, "
              f"{action} one {obj}. The person and the {obj} are clearly visible, separated from the background."
              f"{extra} Simple composition with two to four main objects, natural lighting, no text.")
    return {"image_id":f"cap-v3-B-F{family:02d}-{variant:02d}","family_id":f"F{family:02d}",
            "split":"development" if family<=12 else "validation", "prompt":prompt,"seed":925031+100*family+variant,
            "intended_facts_not_ground_truth":{"interaction":relation,"target":obj,"shirt_colour":colour,"scene":scene}}


def prepare(data):
    """Freeze plans before the first remote generation request."""
    from experiments.v3.runtime.dataset import audit_scenario_specification
    data.mkdir(parents=True, exist_ok=True)
    cfg = read(CONFIG)
    plan = {"schema_version":"remote-prompt-plan-v3.4.0", "generation_amendment_sha256":digest(CONFIG),
            "space_id":cfg["space_id"],"model_id":cfg["requested_model_id"],"seed_rule":cfg["seed_rule"],
            "requested_parameters":cfg["requested_parameters"],
            "images":[prompt_row(f,v) for f in range(1,25) for v in range(1,6)]}
    controlled = [controlled_scenario(f,v) for f in range(1,25) for v in range(1,6)]
    for s in controlled: audit_scenario_specification(s)
    write_once(data/"plans/naturalistic_prompt_plan_v3_4.json", plan)
    write_once(data/"plans/controlled_scenario_plan_v3_4.json", {"scenarios":controlled})
    write_once(data/"plans/remote_generation_v3_4.json", cfg)
    support = read(ROOT/"experiments/v3/config/preregistration_v3_1.json")["dataset_support"]
    write_once(data/"plans/support_layout_before_generation.json",support)
    render_rows=[]
    for s in controlled:
        f,v = int(s["family_id"][1:]),int(s["image_id"][-2:])
        relation,target,scene=FAMILIES[f-1]
        colour=list(PALETTE)[v-1]
        assets=[]
        for e in s["reference_entities"]:
            img=sprite(e["category"],colour,striped=bool(v%2),interaction=relation)
            if v in {2,4}: img=img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            ap=data/"controlled_assets"/s["image_id"]/f"{e['reference_id']}.png"
            save_png(ap,img)
            assets.append({"reference_id":e["reference_id"],"relative_path":ap.relative_to(data/"controlled_assets").as_posix(),"sha256":digest(ap)})
        write_once(data/"scenarios"/f"{s['image_id']}.json", s)
        render_rows.append({"image_id":s["image_id"],"background_rgba":[237,229,214,255] if scene=="indoor" else [204,231,245,255],"assets":assets})
    write_once(data/"plans/controlled_render_plan_v3_4.json",{"licence":"project-authored","images":render_rows})
    # Existing renderer remains immutable. Render to a staging directory so reruns
    # verify already-created images instead of overriding its overwrite guard.
    from experiments.v3.runtime.images import render_controlled
    import tempfile
    with tempfile.TemporaryDirectory(prefix="controlled-",dir=data) as tmp:
        render_controlled(data/"scenarios",data/"plans/controlled_render_plan_v3_4.json",data/"controlled_assets",Path(tmp))
        for p in Path(tmp).glob("*.png"):
            with Image.open(p) as im: save_png(data/"images"/p.name,im)
    for row in plan["images"]:
        # Explicitly invalid as final ground truth: no prompt-derived boxes/facts.
        write_once(data/"reference_drafts"/f"{row['image_id']}.json",{
            "status":"project_author_review_required", "image_id":row["image_id"],
            "instruction":"Inspect the returned image; author visible labels and boxes without perception model output. Do not copy intended prompt facts.",
            "reference_entities":[],"reference_atoms":[]})
    return {"controlled_images":120,"controlled_references":120,"naturalistic_requests_planned":120,"data_root":str(data)}


def inventory(data):
    plan=read(data/"plans/naturalistic_prompt_plan_v3_4.json")
    receipt_path=data/"provenance/remote_generation_receipt_v3_4.json"
    receipt=read(receipt_path) if receipt_path.exists() else {"records":[]}
    records={r["image_id"]:r for r in receipt["records"]}
    materialized_path=data/"provenance/png_materialization.json"
    materialized=read(materialized_path) if materialized_path.exists() else {"records":[]}
    converted={r["image_id"]:r for r in materialized["records"]}
    rows=[]
    by_hash={}
    uniform_images=[]
    for stratum in "AB":
        for f in range(1,25):
            for v in range(1,6):
                iid=f"cap-v3-{stratum}-F{f:02d}-{v:02d}"
                ip=data/"images"/f"{iid}.png"
                sp=data/"scenarios"/f"{iid}.json"
                row={"image_id":iid,"stratum":stratum,"split":"development" if f<=12 else "validation",
                     "image_present":ip.is_file(),"reference_present":sp.is_file()}
                if ip.exists():
                    with Image.open(ip) as im:
                        im.load()
                        if im.size!=(512,512): raise ValueError(f"Wrong image dimensions: {iid}")
                        if all(lo==hi for lo,hi in im.convert("RGB").getextrema()): uniform_images.append(iid)
                    row["image_sha256"]=digest(ip)
                    by_hash.setdefault(row["image_sha256"],[]).append(iid)
                    if stratum=="B" and (iid not in records or iid not in converted or converted[iid]["image_sha256"]!=row["image_sha256"] or
                                         converted[iid]["raw_image_sha256"]!=records[iid]["raw_image_sha256"]):
                        raise ValueError(f"Missing/mismatched remote receipt: {iid}")
                rows.append(row)
    freeze_path=data/"ground_truth_freeze_v3_2.json"
    frozen=False
    if freeze_path.exists():
        from experiments.v3.runtime.dataset import audit_ground_truth_freeze
        audit_ground_truth_freeze(read(freeze_path),data/"capability_manifest_v3_2.json",data/"support_opportunities_v3_2.csv",data)
        frozen=True
    result={"schema_version":"dataset-preparation-status-v3.4.0","updated_at_utc":datetime.now(timezone.utc).isoformat(),
            "expected_images":240,"controlled_images":sum(r["image_present"] for r in rows if r["stratum"]=="A"),
            "naturalistic_raw_responses":len(records),
            "naturalistic_images":sum(r["image_present"] for r in rows if r["stratum"]=="B"),
            "controlled_references":sum(r["reference_present"] for r in rows if r["stratum"]=="A"),
            "naturalistic_references":sum(r["reference_present"] for r in rows if r["stratum"]=="B"),
            "identical_image_groups":[ids for ids in by_hash.values() if len(ids)>1],"uniform_images":uniform_images,
            "ground_truth_frozen":frozen,"ready_for_extraction":frozen,
            "remaining":None if frozen else "Project-author naturalistic image review and reference records, then complete manifest/opportunities/freeze audits.",
            "prompt_plan_sha256":digest(data/"plans/naturalistic_prompt_plan_v3_4.json"),"images":rows}
    (data/"STATUS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    (data/"README.md").write_text(
        "# P9-v3 shared dataset\n\n"
        f"Status updated: {result['updated_at_utc']}\n\n"
        f"- Controlled PNG images: **{result['controlled_images']}/120**.\n"
        f"- Naturalistic responses saved: **{result['naturalistic_raw_responses']}/120**.\n"
        f"- Naturalistic PNG images: **{result['naturalistic_images']}/120**.\n"
        f"- Controlled construction references: **{result['controlled_references']}/120**.\n"
        f"- Naturalistic project-author references: **{result['naturalistic_references']}/120**.\n"
        f"- Ready for extraction: **{'yes' if frozen else 'no'}**.\n\n"
        "Images are in `images/`; exact server bytes are retained in `raw_images/`. "
        "Plans and provenance are in their named subfolders. Contact sheets are "
        "in `previews/`, separated by stratum and development/validation split.\n\n"
        "After all naturalistic PNGs exist, open `review.html` to author reference "
        "boxes and visible facts. Prompts are not ground truth. Empty "
        "`reference_drafts/` files must not be used for scoring. Export your checked "
        "references, then import/finalize from the repository root:\n\n"
        "```powershell\n"
        "python -m experiments.v3.prepare_api_dataset import-references --review-plan path/to/naturalistic_reviewed_scenarios_v3_4.json --author 'Project author'\n"
        "python -m experiments.v3.prepare_api_dataset finalize --author 'Project author'\n"
        "python -m experiments.v3.prepare_api_dataset inventory\n"
        "```\n\n"
        "If an image lacks predeclared support, flag it; do not fabricate labels or "
        "replace images to improve results. No extraction model or precision "
        "measurement has run. The public API's actual weights/settings are "
        "unattested; this is explicitly recorded in the v3.4 generation amendment. "
        "Full instructions: `docs/p9_v3_remote_dataset.md` in the repository.\n",
        encoding="utf-8")
    return {k:v for k,v in result.items() if k!="images"}


def materialize_remote(data):
    """Decode retained server bytes, verify dimensions, then save RGB PNGs."""
    receipt=read(data/"provenance/remote_generation_receipt_v3_4.json")
    rows=[]
    for record in receipt["records"]:
        iid=record["image_id"]
        raw=data/"raw_images"/f"{iid}.bin"
        if digest(raw)!=record["raw_image_sha256"]: raise ValueError(f"Raw hash mismatch {iid}")
        dest=data/"images"/f"{iid}.png"
        with Image.open(raw) as im:
            im.load()
            if im.size!=(512,512): raise ValueError(f"Wrong remote dimensions: {iid}")
            fmt=im.format
            save_png(dest,im.convert("RGB"))
        rows.append({"image_id":iid,"raw_image_sha256":digest(raw),"remote_encoding":fmt,
                     "image_sha256":digest(dest),"operation":"Pillow decode and RGB PNG encode; no resize/crop/content changes"})
    value={"schema_version":"remote-png-materialization-v3.4.0","pillow_version":importlib.metadata.version("Pillow"),
           "python_version":platform.python_version(),"records":rows}
    # An append-only receipt can grow while generation continues; every previous
    # conversion must remain byte-identical.
    p=data/"provenance/png_materialization.json"
    if p.exists():
        old={r["image_id"]:r for r in read(p)["records"]}
        new={r["image_id"]:r for r in rows}
        if any(new.get(k)!=v for k,v in old.items()): raise ValueError("PNG conversion provenance changed")
    p.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")
    return {"naturalistic_images_materialized":len(rows)}


def import_references(data, plan_path, reviewed_by):
    """Import project-authored final-image records, never intended prompt facts."""
    from experiments.v3.runtime.dataset import audit_scenario_specification
    review=read(plan_path)
    records=review.get("scenarios",[])
    expected={r["image_id"] for r in read(data/"plans/naturalistic_prompt_plan_v3_4.json")["images"]}
    if len(records)!=120 or {r["image_id"] for r in records}!=expected:
        raise ValueError("Review export must contain exactly all 120 naturalistic scenarios")
    if review.get("reviewed_without_perception_models") is not True:
        raise ValueError("Project-author model-output-blind declaration missing")
    reviewed_hashes=review.get("image_sha256",{})
    for s in records:
        ip=data/"images"/f"{s['image_id']}.png"
        if reviewed_hashes.get(s["image_id"])!=digest(ip): raise ValueError("Reviewed image hash mismatch")
        audit_scenario_specification(s)
        validate_reference_semantics(s)
        validate_required_support(s)
        if s["stratum"]!="B_naturalistic_t2i" or not 2<=len(s["reference_entities"])<=4:
            raise ValueError("Naturalistic references need two to four visible entities; record any protocol shortfall rather than inventing entities")
        if s["family_id"]!=s["image_id"].split('-')[-2] or s["split"]!=("development" if int(s["family_id"][1:])<=12 else "validation"):
            raise ValueError("Reviewed family/split mismatch")
    for s in records: write_once(data/"scenarios"/f"{s['image_id']}.json",s)
    write_once(data/"provenance/project_author_review.json",{
        "reviewed_by":reviewed_by,"review_export_sha256":digest(plan_path),
        "reviewed_without_perception_models":True,"image_sha256":reviewed_hashes})
    return {"naturalistic_references_imported":120}


def validate_reference_semantics(s):
    """Catch authoring mistakes using boxes/counts, never image predictions."""
    es=s["reference_entities"]
    atoms=s["reference_atoms"]
    keys=[(a["atom_type"],a["value"],a["source_reference_id"],a["target_reference_id"],a["scope_category"]) for a in atoms]
    if len(keys)!=len(set(keys)): raise ValueError("Duplicate reference facts")
    counts=Counter(e["category"] for e in es)
    actual_counts={a["scope_category"]:a["value"] for a in atoms if a["atom_type"]=="count"}
    if sum(a["atom_type"]=="count" for a in atoms)!=len(actual_counts): raise ValueError("Repeated/conflicting category counts")
    expected_counts={k:str(v) if v<5 else "5_plus" for k,v in counts.items()}
    if actual_counts!=expected_counts: raise ValueError("Reference counts contradict authored entities")
    fact=lambda a:(a["value"],a["source_reference_id"],a["target_reference_id"])
    actual_geometry={fact(a) for a in atoms if a["atom_type"]=="geometry_relation"}
    if actual_geometry!={fact(a) for a in geometry(es)}: raise ValueError("Reference geometry contradicts authored boxes")
    entities={(a["value"],a["source_reference_id"]) for a in atoms if a["atom_type"]=="entity"}
    if entities!={(e["category"],e["reference_id"]) for e in es}: raise ValueError("Missing/contradictory entity facts")
    if sum(a["atom_type"]=="scene" for a in atoms)!=1: raise ValueError("Exactly one visible scene reference is required")
    for kind in ("colour","size","material","pattern"):
        by_source={}
        for a in atoms:
            if a["atom_type"]!=kind: continue
            previous=by_source.setdefault(a["source_reference_id"],a["value"])
            if previous!=a["value"]: raise ValueError(f"Conflicting {kind} references for one entity")


def validate_required_support(s):
    layout=read(ROOT/"experiments/v3/config/preregistration_v3_1.json")["dataset_support"]["validation_plan_each_stratum"]
    local=(int(s["family_id"][1:])-1)%12+1
    counts=Counter(a["atom_type"] for a in s["reference_atoms"])
    for kind,rule in layout.items():
        lo,hi=(int(x[1:]) for x in rule["families"].split("-"))
        if lo<=local<=hi and counts[kind]<rule["per_contributing_image"]["positive"]:
            raise ValueError(f"{s['image_id']}: missing planned visible support for {kind}; flag the shortfall, never invent a fact")


def finalize(data, frozen_by):
    """Build a compatible manifest only after every real image/reference exists."""
    from experiments.v3.runtime.dataset import audit_manifest, build_opportunities, create_ground_truth_freeze
    cfg=read(CONFIG)
    plan=read(data/"plans/naturalistic_prompt_plan_v3_4.json")
    receipt_path=data/"provenance/remote_generation_receipt_v3_4.json"
    receipt=read(receipt_path)
    conversion=read(data/"provenance/png_materialization.json")
    if receipt["status"]!="complete" or len(receipt["records"])!=120: raise ValueError("Remote generation is incomplete")
    if receipt["generation_amendment_sha256"]!=digest(CONFIG) or receipt["prompt_plan_sha256"]!=digest(data/"plans/naturalistic_prompt_plan_v3_4.json"):
        raise ValueError("Remote receipt/plan/config hash mismatch")
    prompt_rows={r["image_id"]:r for r in plan["images"]}
    raw_rows={r["image_id"]:r for r in receipt["records"]}
    png_rows={r["image_id"]:r for r in conversion["records"]}
    if len(raw_rows)!=120 or set(raw_rows)!=set(prompt_rows) or set(png_rows)!=set(prompt_rows): raise ValueError("Remote receipt IDs mismatch")
    author_review=read(data/"provenance/project_author_review.json")
    rows=[]
    for code in "AB":
        for f in range(1,25):
            for v in range(1,6):
                iid=f"cap-v3-{code}-F{f:02d}-{v:02d}"
                ip,sp=data/"images"/f"{iid}.png",data/"scenarios"/f"{iid}.json"
                if not ip.is_file() or not sp.is_file(): raise ValueError(f"Missing final image or project-author reference: {iid}")
                validate_reference_semantics(read(sp))
                validate_required_support(read(sp))
                natural=code=="B"
                if natural:
                    raw=raw_rows[iid]
                    if digest(data/"raw_images"/f"{iid}.bin")!=raw["raw_image_sha256"] or png_rows[iid]["image_sha256"]!=digest(ip) or png_rows[iid]["raw_image_sha256"]!=raw["raw_image_sha256"]:
                        raise ValueError("Remote raw/PNG provenance mismatch")
                    if author_review["image_sha256"].get(iid)!=digest(ip): raise ValueError("Author review image changed")
                rows.append({"image_id":iid,"family_id":f"F{f:02d}","stratum":"B_naturalistic_t2i" if natural else "A_controlled_geometric",
                    "split":"development" if f<=12 else "validation","source_type":"remote_sd_turbo_unattested_weights" if natural else "deterministic_controlled_renderer",
                    "licence":"Requested SD-Turbo: Stability AI Community License; actual remote weight identity unverified" if natural else "project-authored",
                    "generator_or_asset_revision":f"space:{cfg['space_id']}@{raw_rows[iid]['space_commit']};requested:sd-turbo;weights-unverified;receipt-sha256:{digest(receipt_path)}" if natural else "controlled-renderer-v3.4.0",
                    "prompt_hash_if_applicable":hashlib.sha256(prompt_rows[iid]["prompt"].encode()).hexdigest() if natural else None,
                    "seed_if_applicable":prompt_rows[iid]["seed"] if natural else None,"relative_path":f"images/{iid}.png","image_sha256":digest(ip),
                    "scenario_specification_id":f"scenario-{iid}","scenario_specification_path":f"scenarios/{iid}.json","scenario_specification_sha256":digest(sp)})
    manifest={"schema_version":"capability-manifest-v3.2.0","dataset_version":"p9-v3-capability-data-v3.0.0",
        "ground_truth_version":"project-authored-ground-truth-v3.2.0","created_at_utc":datetime.now(timezone.utc).isoformat(),"images":rows}
    audit_manifest(manifest,data)
    mp=data/"capability_manifest_v3_2.json"
    write_once(mp,manifest)
    op=data/"support_opportunities_v3_2.csv"
    build_opportunities(op,mp,data)
    # A separate hash inventory binds the API amendment/receipts/PNG decoding in
    # addition to the original image/scenario/config-bound ground-truth freeze.
    write_once(data/"provenance/remote_dataset_binding_v3_4.json",{
        "generation_amendment_sha256":digest(CONFIG),"receipt_sha256":digest(receipt_path),
        "png_materialization_sha256":digest(data/"provenance/png_materialization.json"),
        "author_review_sha256":digest(data/"provenance/project_author_review.json"),"manifest_sha256":digest(mp)})
    return create_ground_truth_freeze(data/"ground_truth_freeze_v3_2.json",mp,op,data,data/"extraction_results",frozen_by)


def contact_sheets(data):
    out=data/"previews"
    out.mkdir(exist_ok=True)
    for stratum in "AB":
        for split,start,end in [("development",1,12),("validation",13,24)]:
            # Keep held-out previews separate; never feed them into calibration.
            sheet=Image.new("RGB",(5*180,12*200),"white")
            d=ImageDraw.Draw(sheet)
            for row,f in enumerate(range(start,end+1)):
                for col,v in enumerate(range(1,6)):
                    iid=f"cap-v3-{stratum}-F{f:02d}-{v:02d}"
                    ip=data/"images"/f"{iid}.png"
                    if ip.exists():
                        with Image.open(ip) as im: sheet.paste(im.convert("RGB").resize((176,176)),(col*180,row*200))
                    d.text((col*180+2,row*200+178),iid,fill="black")
            sheet.save(out/f"{stratum}_{split}.jpg",quality=88)


def review_page(data):
    vocab=read(ROOT/"experiments/v3/config/visual_observation_v3.json")
    entities=read(ROOT/"experiments/v3/config/visual_observation_v3_1.json")["shared_gate_entity_label_intersection"]
    plan=read(data/"plans/naturalistic_prompt_plan_v3_4.json")
    images=[]
    for row in plan["images"]:
        ip=data/"images"/f"{row['image_id']}.png"
        images.append({"image_id":row["image_id"],"split":row["split"],"image_sha256":digest(ip) if ip.exists() else None})
    if any(r["image_sha256"] is None for r in images): raise ValueError("Generate/materialize all 120 images before preparing the review page")
    catalog={"plan_sha256":digest(data/"plans/naturalistic_prompt_plan_v3_4.json"),"images":images,"entities":entities,
             "labels":{**vocab["attributes"],"unary_action":vocab["unary_actions"],"binary_interaction":vocab["binary_interactions"],"scene":vocab["scenes"]}}
    html=(ROOT/"experiments/v3/reference_review.html").read_text(encoding="utf-8").replace("__CATALOG__",json.dumps(catalog))
    (data/"review.html").write_text(html,encoding="utf-8")
    return {"review_page":str(data/"review.html")}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=["prepare","materialize-remote","inventory","previews","review-page","import-references","finalize"])
    p.add_argument("--data-root",type=Path,default=DEFAULT_DATA)
    p.add_argument("--review-plan",type=Path)
    p.add_argument("--author")
    args=p.parse_args()
    if args.command=="prepare": result=prepare(args.data_root)
    elif args.command=="materialize-remote": result=materialize_remote(args.data_root)
    elif args.command=="import-references":
        if not args.review_plan or not args.author: p.error("import-references needs --review-plan and --author")
        result=import_references(args.data_root,args.review_plan,args.author)
    elif args.command=="finalize":
        if not args.author: p.error("finalize needs --author")
        result=finalize(args.data_root,args.author)
    elif args.command=="inventory": result=inventory(args.data_root)
    elif args.command=="review-page": result=review_page(args.data_root)
    else: contact_sheets(args.data_root); result={"previews":str(args.data_root/"previews")}
    print(json.dumps(result,indent=2))


if __name__=="__main__": main()
