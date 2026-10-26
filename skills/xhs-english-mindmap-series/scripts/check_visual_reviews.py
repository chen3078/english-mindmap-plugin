#!/usr/bin/env python3
"""Reject missing, pending, failed or stale recorded visual inspections.

This validates inspection evidence, not aesthetic truth or user approval.
"""
import argparse
import json
from pathlib import Path
from review_image import ASSETS, digest, expected_content, is_home_topic, receipt_path, references, visual_criteria, continuity_references, connector_sources

def check_image(folder, candidate, kind):
    folder, candidate = folder.resolve(), candidate.resolve()
    name = candidate.relative_to(folder).as_posix()
    from connector_checks import check as check_connectors
    errors = check_connectors(folder, candidate, kind)
    try:
        data = json.loads(receipt_path(folder, candidate).read_text(encoding="utf-8"))
        home = bool(data.get("home_series"))
        criteria = visual_criteria(kind, home)
        if is_home_topic(folder) and not home:
            errors.append("home-series standards were omitted")
        if data.get("candidate") != name or data.get("kind") != kind:
            errors.append("inspection belongs to a different image/format")
        if data.get("visual_status") != "pass" or not data.get("reviewed_at"):
            errors.append("visual inspection is pending or failed")
        if data.get("visual_criteria") != criteria or data.get("required_visual_checks") != list(criteria):
            errors.append("inspection criteria are outdated or incomplete")
        if data.get("structure_status") != "pass" or data.get("dimensions") != [1086, 1448]:
            errors.append("recorded dimensions did not pass")
        if data.get("expected_content", {}).get("warning"):
            errors.append("frozen content association is unresolved")
        if data.get("expected_content") != expected_content(folder, candidate, kind):
            errors.append("review content association is outdated; rebuild and inspect the correct question IDs")
        for key in criteria:
            finding = data.get("findings", {}).get(key, {})
            if finding.get("status") != "pass" or not isinstance(finding.get("observation"), str) or not finding["observation"].strip():
                errors.append(f"missing passing observation for {key}")
        expected = {name: digest(candidate), "manifest.json": digest(folder / "manifest.json")}
        for source, _ in references(kind, home):
            rel = (Path("review/references") / source.relative_to(ASSETS)).as_posix()
            expected[rel] = digest(source)
        for source, _ in continuity_references(folder, candidate, kind):
            expected[source.relative_to(folder).as_posix()] = digest(source)
        expected.update(connector_sources(folder,candidate,kind))
        if data.get("sources_sha256") != expected:
            errors.append("image, manifest or approved reference changed after inspection")
        for rel, value in expected.items():
            path = folder / rel
            if not path.is_file() or digest(path) != value:
                errors.append(f"missing or changed review source: {rel}")
        comparison = (folder / data["comparison"]).resolve()
        comparison.relative_to(folder)
        if not comparison.is_file() or digest(comparison) != data.get("comparison_sha256"):
            errors.append("comparison is missing or changed")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"missing or invalid inspection record: {exc}")
    return [f"{name}: {error}" for error in errors]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--kind", choices=("cover", "practice", "qa", "video"))
    args = parser.parse_args()
    folder = args.topic_folder.resolve()
    if bool(args.candidate) != bool(args.kind):
        parser.error("--candidate and --kind must be used together")
    if args.candidate:
        images = [(folder / args.candidate, args.kind)]
    else:
        images = [(folder / "01-cover.png", "cover"), (folder / "02-picture-practice.png", "practice")]
        images += [(p, "qa") for p in sorted(folder.glob("*-qa-*.png"))]
        images += [(p, "video") for p in sorted((folder / "video").glob("*.png"))]
        images = [(p, kind) for p, kind in images if p.is_file()]
    errors = [error for path, kind in images for error in check_image(folder, path, kind)]
    if not images:
        errors.append("No topic images found")
    for error in errors:
        print("ERROR:", error)
    if errors:
        return 1
    print(f"REVIEW RECORDS PASS: {len(images)} current, complete recorded inspections. Aesthetic truth and user approval are not machine-certified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
