#!/usr/bin/env python3
"""Prepare a per-image comparison; record visual findings only after inspection.

Requires Pillow. File checks never certify aesthetics or raster text accuracy.
"""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from manifest_model import questions
from check_manifest import check as check_manifest

ASSETS = Path(__file__).resolve().parents[1] / "assets"
HOME_TOPICS = {"door", "window", "bed", "lamp", "sofa", "table", "chair", "clothes", "fridge", "refrigerator", "washing machine", "cup", "umbrella"}

def is_home_topic(folder):
    manifest = folder / "manifest.json"
    if not manifest.is_file():
        return False
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if data.get("visual_family"):
        return data["visual_family"] == "home"
    if data.get("manifest_mode") != "legacy" or not data.get("legacy_manifest_reason"):
        raise ValueError("New topics must explicitly declare visual_family: home or general")
    return data.get("topic_en", "").strip().casefold() in HOME_TOPICS
CHECKS = {
    "cover": ["subject_identity", "subject_scale", "hand_drawn_style", "page_rhythm", "heading_picture_relation", "study_variety", "text_accuracy", "picture_meaning", "connectors", "connector_neatness"],
    "practice": ["cover_continuity", "subject_scale", "hand_drawn_style", "page_rhythm", "no_text_or_circles", "picture_meaning", "connectors", "connector_neatness"],
    "qa": ["subject_identity", "hand_drawn_style", "page_rhythm", "whole_page_template", "four_text_fields", "type_readability", "art_integration", "picture_meaning"],
    "video": ["subject_identity", "hand_drawn_style", "framing", "answer_details", "no_text", "subtitle_space"],
}

CRITERIA = {
    "subject_identity": "Identify the shared shape, color/material and motifs across current-topic art; allow only explicitly taught variations, never accidental redesign or leaked reference subjects.",
    "subject_scale": "Compare subject/title/right-group balance at equal page width; reject both a dominating tall slab and a tiny isolated object. Percentages alone cannot establish a pass.",
    "hand_drawn_style": "Compare irregular ink, pencil/watercolor grain, paper, restrained fills and soft edges across the main art and studies; reject hard clip art or mismatched batches.",
    "page_rhythm": "Inspect the whole page for balanced density, meaningful whitespace and flowing grouped content; reject mechanical grids, dead gaps, crowding and overlap.",
    "heading_picture_relation": "Trace every branch-tip heading to its nearby own pictures and captions; reject detached heading sidebars or distant icon columns. Meaningful local callouts are allowed.",
    "study_variety": "Name the whole-object, part, action, material/location/scene studies actually used; reject repeated rectangular whole-object tiles that do not add distinct information.",
    "text_accuracy": "Read every visible heading/keyword against the frozen manifest; check label-to-picture correspondence and the small brand, not just text in source files.",
    "picture_meaning": "Verify each learning point against its pictures, including a clear separate study of every named physical part; reject irrelevant decorative substitutions.",
    "connectors": "Record every group ID and actual destination after tracing each visible line; confirm one attached connector per group, no missing/doubled/dangling/misdirected lines or former-circle endpoints.",
    "connector_neatness": "Compare actual full-page arcs with approved Dog/Window templates: smooth ordered fan, consistent visible coral stroke, balanced separation, anchored starts and correct ends, no crossings, tangles, giant loops, text/art intrusion or unrelated blank-space wandering. Geometry checks do not establish an aesthetic pass.",
    "cover_continuity": "Compare practice directly with the selected cover: same recognizable subject, study content, group order and relationships; no fresh unrelated composition.",
    "no_text_or_circles": "Scan the full raster for zero words, titles, labels, numerals, brands and empty numbered circles; retain only meaningful pictures, branches and action marks.",
    "whole_page_template": "Compare the full Dog/Window Q&A page family: header, number disks, Q/Chinese/A/Chinese reading order, broad soft rows and overall density. Matching pastel colors is insufficient.",
    "four_text_fields": "For every assigned question, check every English question/answer and Chinese question/answer against the manifest in the actual raster. No blank Q&A backgrounds or omitted fields.",
    "type_readability": "Read at full size and compare at 350 px page width: prominent legible handwritten English, quieter readable Chinese; no thin/tiny English, heavy dense Chinese, clipped or cramped wrapping.",
    "art_integration": "Check relevant illustrations flow into each Q&A row with usable size and text clearance; reject pasted opaque rectangles, crop fragments, tiny isolated thumbnails or disconnected blank space.",
    "framing": "Compare whole-scene subject scale and action composition with approved video framing; reject enlarged map crops, narrow picture strips and straight crop edges.",
    "answer_details": "Check every main detail of this question's answer has a meaningful visual cue and all named physical parts are individually recognizable.",
    "no_text": "Scan the whole video still for zero readable lettering, labels, numbers, brands or subtitles.",
    "subtitle_space": "Inspect the entire bottom 25 percent: uninterrupted quiet warm paper, with no feet, arrows, scenery, dark marks or printed box.",
    "home_softness": "Describe how this object conveys soft, comfortable, cute home treatment through appropriate contours, materials, palette and details; retain function and avoid unrelated curtains, faces or props.",
}

def visual_criteria(kind, home=False):
    keys = CHECKS[kind] + (["home_softness"] if home else [])
    return {key: CRITERIA[key] for key in keys}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def references(kind, home=False):
    refs = {
        "cover": [("key-cup-style/key-reference.png", "Key: drawing style"), ("key-cup-style/cup-reference.png", "Cup: drawing style"), ("key-cup-style/approved-cat-cover.png", "Cat: page rhythm"), ("approved-dog/cover.png", "Dog: page rhythm"), ("approved-carrot/cover-size-reference.png", "Carrot: subject scale only")],
        "practice": [("approved-dog/picture-practice.png", "Dog: connected practice"), ("approved-lion/picture-practice.png", "Lion: connected practice"), ("approved-carrot/practice-size-reference.png", "Carrot: subject scale only")],
        "qa": [("approved-dog/qa-01-04.png", "Dog: Q&A 1-4"), ("approved-dog/qa-05-08.png", "Dog: Q&A 5-8"), ("approved-rabbit/qa-01-03.png", "Rabbit: three-row layout"), ("approved-rabbit/qa-06-08.png", "Rabbit: three-row layout")],
        "video": [("approved-dog/video-single-subject.png", "Dog: subject framing"), ("approved-dog/video-multiple-actions.png", "Dog: action framing")],
    }[kind]
    if kind != "cover":
        refs = [("key-cup-style/key-reference.png", "Key: drawing style"), ("key-cup-style/cup-reference.png", "Cup: drawing style"), *refs]
    if home and kind != "video":
        names = {"cover": ["cover.png"], "practice": ["picture-practice.png"], "qa": ["qa-01-04.png", "qa-05-08.png"]}[kind]
        refs += [("approved-window/" + name, "Window: home " + name) for name in names]
    return [(ASSETS / rel, label) for rel, label in refs]

def local_references(folder, kind, home=False):
    result = []
    for source, label in references(kind, home):
        if not source.is_file():
            raise ValueError(f"Missing approved reference: {source}")
        target = folder / "review" / "references" / source.relative_to(ASSETS)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or digest(source) != digest(target):
            shutil.copy2(source, target)
        result.append((target, label))
    return result

def continuity_references(folder, candidate, kind):
    refs = []
    cover = folder / "01-cover.png"
    if kind != "cover" and cover.is_file(): refs.append((cover, "Current topic cover: subject continuity"))
    if kind in ("qa", "video"):
        from generation_evidence import record_path, local
        evidence = record_path(folder, candidate)
        if evidence.is_file():
            data = json.loads(evidence.read_text(encoding="utf-8"))
            sample = data.get("spec", {}).get("sample")
            if isinstance(sample, str) and sample != "self":
                refs.append((local(folder, sample), "Current topic inspected sample: layout/style continuity"))
    return refs

def comparison(items, target):
    thumbs = []
    for path, label in items:
        with Image.open(path) as source:
            im = ImageOps.exif_transpose(source).convert("RGB")
            thumbs.append((im.resize((350, round(im.height * 350 / im.width)), Image.Resampling.LANCZOS), label))
    sheet = Image.new("RGB", (16 + len(items) * 366, 80 + max(im.height for im, _ in thumbs)), "#eeeae2")
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 8), "VISUAL INSPECTION REQUIRED - each image is 350 px wide", fill="#342720")
    for i, (im, label) in enumerate(thumbs):
        x = 16 + i * 366
        draw.text((x, 36), label, fill="#342720")
        sheet.paste(im, (x, 64))
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, quality=93)

def expected_content(folder, candidate, kind):
    manifest = folder / "manifest.json"
    if not manifest.is_file():
        return {"warning": "No manifest.json: no frozen source for semantic/text inspection."}
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    groups = data.get("groups", [])
    errors, _, _ = check_manifest(manifest)
    if errors:
        return {"warning": "Invalid manifest: " + "; ".join(errors)}
    items = questions(data)
    if kind == "qa":
        match = re.search(r"-qa-(\d+)-(\d+)\.png$", candidate.name)
        if not match:
            return {"warning": "Use NN-qa-FIRST-LAST.png to associate assigned Q&A."}
        first, last = map(int, match.groups())
        items = [q for q in items if first <= q["id"] <= last]
        if first < 1 or last < first or [q["id"] for q in items] != list(range(first, last + 1)):
            return {"warning": "Q&A filename range does not match the manifest exactly."}
    elif kind == "video":
        items = [q for q in items if str(q["id"]) == candidate.stem.lstrip("0")]
    if not items:
        return {"warning": "No matching manifest groups for this image."}
    if kind in ("qa", "video"):
        group_ids = {q["group_id"] for q in items}
        groups = [g for g in groups if g["id"] in group_ids]
    groups = [{key: value for key, value in g.items() if key != "qa"} for g in groups]
    return {"topic_en": data.get("topic_en"), "topic_zh": data.get("topic_zh"), "groups": groups, "qa_items": items, "content_plan": data.get("content_plan")}

def receipt_path(folder, candidate):
    rel = candidate.resolve().relative_to(folder.resolve())
    return folder / "review" / (rel.with_suffix("").as_posix().replace("/", "--") + ".json")

def connector_sources(folder, candidate, kind):
    if kind not in ("cover", "practice"): return {}
    from connector_checks import record_path, local
    record=record_path(folder,candidate)
    if not record.is_file(): return {}
    data=json.loads(record.read_text(encoding="utf-8"))
    paths=[record,local(folder,data["base"]),local(folder,data["plan"])]
    return {p.relative_to(folder).as_posix():digest(p) for p in paths}

def prepare(folder, candidate, kind, home=False):
    folder, candidate = folder.resolve(), candidate.resolve()
    declared_home = is_home_topic(folder)
    if home and not declared_home:
        raise ValueError("--home disagrees with manifest visual_family; update the content plan first")
    home = declared_home
    rel = candidate.relative_to(folder)
    if not candidate.is_file() or candidate.suffix.lower() != ".png":
        raise ValueError("Candidate must be a saved PNG inside the topic folder.")
    with Image.open(candidate) as im:
        size = list(im.size)
        im.verify()
    refs = local_references(folder, kind, home)
    refs += continuity_references(folder, candidate, kind)
    receipt = receipt_path(folder, candidate)
    output = receipt.with_name(receipt.stem + "-comparison.jpg")
    sources = {p.relative_to(folder).as_posix(): digest(p) for p, _ in [(candidate, ""), *refs]}
    manifest = folder / "manifest.json"
    if manifest.is_file():
        sources["manifest.json"] = digest(manifest)
    sources.update(connector_sources(folder, candidate, kind))
    old = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
    comparison([*refs, (candidate, "CURRENT: " + rel.as_posix())], output)
    criteria = visual_criteria(kind, home)
    content = expected_content(folder, candidate, kind)
    same = (old.get("sources_sha256") == sources and old.get("kind") == kind
            and old.get("comparison_sha256") == digest(output) and old.get("visual_criteria") == criteria
            and old.get("expected_content") == content)
    from connector_checks import check as check_connectors
    connector_errors = check_connectors(folder, candidate, kind)
    result = {"candidate": rel.as_posix(), "kind": kind, "home_series": home,
              "dimensions": size, "structure_status": "pass" if size == [1086, 1448] and not connector_errors else "fail", "connector_errors": connector_errors,
              "comparison": output.relative_to(folder).as_posix(), "comparison_sha256": digest(output),
              "sources_sha256": sources, "expected_content": content,
              "required_visual_checks": list(criteria), "visual_criteria": criteria,
              "visual_status": old.get("visual_status", "pending") if same else "pending",
              "findings": old.get("findings", {}) if same else {},
              "reviewed_at": old.get("reviewed_at") if same else None,
              "note": "Generated comparisons and file/size checks never certify visual or text accuracy."}
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result, receipt

def record_findings(folder, receipt, findings_path):
    data = json.loads(receipt.read_text(encoding="utf-8"))
    if data.get("expected_content") != expected_content(folder, folder / data["candidate"], data["kind"]):
        raise ValueError("Question mapping changed: rebuild comparison and inspect the current question IDs.")
    if data.get("visual_criteria") != visual_criteria(data["kind"], data["home_series"]):
        raise ValueError("Inspection criteria changed: rebuild comparison and inspect against the current standards.")
    for rel, expected in data["sources_sha256"].items():
        source = folder / rel
        if not source.is_file() or digest(source) != expected:
            raise ValueError("Source changed: rebuild comparison and inspect the new image before recording findings.")
    cmp = folder / data["comparison"]
    if not cmp.is_file() or digest(cmp) != data["comparison_sha256"]:
        raise ValueError("Comparison changed or missing: rebuild before recording findings.")
    findings = json.loads(findings_path.read_text(encoding="utf-8-sig"))
    for check in data["required_visual_checks"]:
        item = findings.get(check, {})
        if item.get("status") not in ("pass", "fail") or not isinstance(item.get("observation"), str) or not item["observation"].strip():
            raise ValueError(f"{check}: supply status pass/fail and a concrete observation after inspection.")
    passed = all(findings[c]["status"] == "pass" for c in data["required_visual_checks"])
    if passed:
        from connector_checks import check as check_connectors
        failures = check_connectors(folder, folder / data["candidate"], data["kind"])
        if failures: raise ValueError("Fix actual connectors before recording a pass: " + "; ".join(failures))
    if passed and (data["structure_status"] != "pass" or data["expected_content"].get("warning")):
        raise ValueError("Fix dimensions or missing content association before recording a pass.")
    data["findings"] = {c: findings[c] for c in data["required_visual_checks"]}
    data["visual_status"] = "pass" if passed else "fail"
    data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("candidate", type=Path, help="PNG path relative to topic folder")
    parser.add_argument("--kind", required=True, choices=CHECKS)
    parser.add_argument("--home", action="store_true", help="Include approved Window references")
    parser.add_argument("--record", type=Path, help="JSON findings after inspecting the comparison and full-size PNG")
    args = parser.parse_args()
    folder = args.topic_folder.resolve()
    try:
        args.home = args.home or is_home_topic(folder)
        if args.record:
            receipt = receipt_path(folder, folder / args.candidate)
            old = json.loads(receipt.read_text(encoding="utf-8"))
            if old["kind"] != args.kind or old["home_series"] != args.home:
                raise ValueError("Review kind/home mode differs: prepare a new comparison first.")
            data = record_findings(folder, receipt, args.record)
        else:
            data, receipt = prepare(folder, folder / args.candidate, args.kind, args.home)
        print(f"COMPARISON: {folder / data['comparison']}")
        print(f"RECORD: {receipt}")
        print(f"STRUCTURE: {data['structure_status']}; VISUAL: {data['visual_status']} (recorded inspection, not automated judgment)")
        return 0 if data["structure_status"] == "pass" and data["visual_status"] != "fail" else 1
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
