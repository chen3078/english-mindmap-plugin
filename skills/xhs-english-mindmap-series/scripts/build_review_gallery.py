#!/usr/bin/env python3
"""Build a portable 350 px comparison gallery for all saved topic images.

Usage: python build_review_gallery.py TOPIC_FOLDER [--home]
Requires Pillow. Producing a gallery never approves its contents.
"""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import quote
from review_image import comparison, is_home_topic, local_references, prepare, continuity_references
from gallery_binding import write_binding
from check_manifest import check as check_manifest
from generation_evidence import record_path as generation_record_path, check as check_generation

def card(folder, path, label):
    rel = quote(path.relative_to(folder).as_posix())
    return (f'<figure><a href="{rel}"><img src="{rel}" alt="{html.escape(label, quote=True)}"></a>'
            f'<figcaption>{html.escape(label)}</figcaption></figure>')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("--home", action="store_true", help="Include approved Window references for home objects")
    args = parser.parse_args()
    folder = args.topic_folder.resolve()
    if not folder.is_dir():
        parser.error("Topic folder does not exist")
    manifest_errors, _, _ = check_manifest(folder / "manifest.json")
    if manifest_errors:
        parser.error("manifest invalid: " + "; ".join(manifest_errors))
    args.home = args.home or is_home_topic(folder)
    sections, failures = [], []
    qa_pages = sorted(folder.glob("[0-9][0-9]-qa-[0-9][0-9]-[0-9][0-9].png"))
    groups = [("cover", [folder / "01-cover.png"]), ("practice", [folder / "02-picture-practice.png"]),
              ("qa", qa_pages), ("video", sorted((folder / "video").glob("[0-9][0-9].png")))]
    count = 0
    try:
        for kind, paths in groups:
            paths = [p for p in paths if p.is_file()]
            if not paths:
                continue
            refs = local_references(folder, kind, args.home)
            for path in paths:
                result, receipt = prepare(folder, path, kind, args.home)
                rel = path.relative_to(folder).as_posix()
                count += 1
                if result["structure_status"] != "pass" or result["visual_status"] == "fail":
                    failures.append(rel)
                notes = html.escape(json.dumps(result["expected_content"], ensure_ascii=False, indent=2))
                criteria = html.escape(json.dumps(result["visual_criteria"], ensure_ascii=False, indent=2))
                receipt_link = quote(receipt.relative_to(folder).as_posix())
                cmp_link = quote(result["comparison"])
                generation = generation_record_path(folder, path)
                evidence_link = (' · <a href="' + quote(generation.relative_to(folder).as_posix()) + '">Generation evidence (execution not independently verified)</a>') if generation.is_file() else ' · Generation evidence: missing/unverified'
                continuity = continuity_references(folder, path, kind)
                evidence_errors = check_generation(folder, path, kind)
                coverage = json.loads(generation.read_text(encoding="utf-8")).get("reference_coverage", {}) if generation.is_file() else {}
                connector_notes = html.escape(json.dumps(result.get("connector_errors", []), ensure_ascii=False, indent=2))
                coverage_notes = html.escape(json.dumps({"linkage": "invalid/unverified" if evidence_errors else "current local linkage", "errors": evidence_errors, "duties": coverage}, ensure_ascii=False, indent=2))
                sections.append(f'<section><h2>{html.escape(rel)}</h2><p>Structure: {result["structure_status"]}; '
                                f'visual inspection: {result["visual_status"]}. '
                                f'<a href="{cmp_link}">Comparison JPG</a> · <a href="{receipt_link}">Inspection record</a>{evidence_link}</p>'
                                '<div class="strip">' + ''.join(card(folder, p, label) for p, label in [*refs, *continuity])
                                + card(folder, path, "CURRENT: " + rel) + '</div>'
                                f'<details><summary>Connector geometry / final raster errors (empty means no detected error, not aesthetic approval)</summary><pre>{connector_notes}</pre></details>'
                                f'<details><summary>Reference duties and actual inheritance</summary><pre>{coverage_notes}</pre></details>'
                                f'<details><summary>Visual standards to inspect individually</summary><pre>{criteria}</pre></details>'
                                f'<details><summary>Frozen content to verify against the raster</summary><pre>{notes}</pre></details></section>')
        if not count:
            raise ValueError("No saved topic images found; no review gallery was generated.")
        qa_inputs = []
        if qa_pages:
            qa_items = [*local_references(folder, "qa", args.home), *[(p, "CURRENT: " + p.name) for p in qa_pages]]
            comparison(qa_items, folder / "qa-review-comparison.jpg")
            qa_inputs = [p.relative_to(folder).as_posix() for p, _ in qa_items]
        markup = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Image review</title>
<style>*{box-sizing:border-box}body{margin:0;padding:24px;background:#eeeae2;color:#342720;font:16px system-ui,sans-serif}
section{margin:32px 0;padding:16px;background:#fffdf8}p{line-height:1.5}.strip{display:flex;gap:16px;overflow-x:auto;align-items:flex-start;padding:8px 0}
figure{margin:0;flex:0 0 350px;width:350px}img{display:block;width:350px;height:auto}figcaption{padding:6px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#804236}</style></head><body>
<h1>Whole-page reference comparison</h1><p>Every image is 350 px wide. Scroll horizontally; open a PNG for full-size text inspection.
Only explicit inspection findings can mark a visual pass. File changes invalidate earlier findings. References control their stated roles, not subject content.</p>
''' + '\n'.join(sections) + '</body></html>'
        (folder / "review-gallery.html").write_text(markup, encoding="utf-8")
        write_binding(folder, args.home, qa_inputs)
        print(f"CREATED: {folder / 'review-gallery.html'}")
        print(f"Prepared {count} image comparison(s); uninspected images remain PENDING.")
        if failures:
            print(f"FAILED checks: {', '.join(failures)}")
        return 1 if failures else 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
