#!/usr/bin/env python3
"""One release entry point. Default: full package; --scope selects a subset.

Checks deliverable completeness and current recorded inspections, not aesthetics.
"""
import argparse
import re
from pathlib import Path
from PIL import Image
from check_manifest import check as check_manifest
from check_visual_reviews import check_image
from export_english_qa import render
from manifest_model import load, questions
from gallery_binding import check_binding
from generation_evidence import check as check_generation, check_samples

WIDTH, HEIGHT = 1086, 1448
SCOPES = ("cover", "practice", "qa", "text", "video", "caption")

def size_of(path):
    with Image.open(path) as im:
        size = im.size
        if im.format != "PNG":
            raise ValueError("not a PNG image")
        im.verify()
    return size

def scope_set(value):
    if value == "full":
        return set(SCOPES)
    items = value.split(",")
    selected = {item.strip() for item in items}
    if not selected or "" in selected or not selected <= set(SCOPES):
        raise ValueError("scope must be full or a comma-separated subset of " + ",".join(SCOPES))
    if "video" in selected:
        selected.add("text")  # Exact English is a required video dependency.
    return selected

def check(folder, scope="full"):
    folder = Path(folder).resolve()
    errors, warnings = [], []
    try:
        selected = scope_set(scope)
    except ValueError as exc:
        return [str(exc)], warnings, 0
    manifest = folder / "manifest.json"
    manifest_errors, warnings, _ = check_manifest(manifest)
    if manifest_errors:
        return manifest_errors, warnings, 0
    items = questions(load(manifest)); count = len(items)
    def require(name):
        path = folder / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty {name}")
            return False
        return True
    images = []
    if "cover" in selected:
        images.append((folder / "01-cover.png", "cover"))
    if "practice" in selected:
        images.append((folder / "02-picture-practice.png", "practice"))
    qa_pages = []
    if "qa" in selected:
        qa_pages = sorted(folder.glob("*-qa-*.png"))
        if not qa_pages:
            errors.append("missing bilingual Q&A image(s)")
        covered = []
        for path in qa_pages:
            match = re.fullmatch(r"\d+-qa-(\d+)-(\d+)\.png", path.name)
            if not match:
                errors.append(f"{path.name}: expected NN-qa-FIRST-LAST.png")
                continue
            first, last = map(int, match.groups())
            if first > last:
                errors.append(f"{path.name}: reversed question range")
            covered.extend(range(first, last + 1))
        if covered != list(range(1, count + 1)):
            errors.append(f"Q&A ranges cover {covered}; expected question IDs 1–{count} exactly once in order")
        images += [(path, "qa") for path in qa_pages]
        if require("qa-review-comparison.jpg"):
            cmp = folder / "qa-review-comparison.jpg"
            try:
                with Image.open(cmp) as im:
                    if im.format != "JPEG":
                        raise ValueError("not a JPEG comparison")
                    im.verify()
                if qa_pages and cmp.stat().st_mtime_ns < max(p.stat().st_mtime_ns for p in qa_pages):
                    errors.append("qa-review-comparison.jpg is older than a final Q&A PNG")
            except (OSError, ValueError) as exc:
                errors.append(f"qa-review-comparison.jpg: {exc}")
    if "text" in selected and require("qa-en-only.txt"):
        try:
            if (folder / "qa-en-only.txt").read_text(encoding="utf-8-sig") != render(manifest):
                errors.append("qa-en-only.txt differs from the complete ordered question list")
        except (OSError, UnicodeError) as exc:
            errors.append(f"qa-en-only.txt: {exc}")
    if "video" in selected:
        actual = {p.name for p in (folder / "video").glob("*.png")}
        expected = {f"{i:02d}.png" for i in range(1, count + 1)}
        for name in sorted(expected - actual):
            errors.append(f"missing video/{name}")
        for name in sorted(actual - expected):
            errors.append(f"unexpected video/{name}")
        images += [(folder / "video" / name, "video") for name in sorted(expected & actual)]
    if "caption" in selected:
        require("caption.md")
    if selected & {"cover", "practice", "qa", "video"}:
        require("prompt-notes.md")
        require("review-gallery.html")
    for path, kind in images:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(folder).as_posix()}")
            continue
        try:
            if size_of(path) != (WIDTH, HEIGHT):
                errors.append(f"{path.name}: expected {WIDTH}x{HEIGHT}")
        except (OSError, ValueError) as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        errors.extend(check_image(folder, path, kind))
        errors.extend(check_generation(folder, path, kind))
    if selected & {"cover", "practice", "qa", "video"}:
        errors.extend(check_binding(folder, images, "qa" in selected))
        errors.extend(check_samples(folder, images))
    return errors, warnings, count

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("--scope", default="full", help="full (default), or e.g. cover / qa,text / video")
    args = parser.parse_args(argv)
    try:
        selected = scope_set(args.scope)
        errors, warnings, count = check(args.topic_folder, args.scope)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("ERROR:", exc)
        return 1
    print("CHECKED SCOPE:", ",".join(k for k in SCOPES if k in selected))
    print("Ordered questions:", count)
    for warning in warnings: print("WARNING:", warning)
    for error in errors: print("ERROR:", error)
    if errors:
        print(f"FAIL: {len(errors)} release-check error(s)")
        return 1
    print("RELEASE CHECK PASS for the scope above: complete outputs and current recorded inspections.")
    print("Actual visual quality and user approval are not machine-certified.")
    print("Generation records are locally linked; remote execution authenticity is NOT independently verified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
