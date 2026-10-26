"""Resolve reference duties from approved bytes, never from self-declared labels."""
import json
from pathlib import Path
from review_image import ASSETS, digest, is_home_topic, receipt_path

CATALOG = ASSETS / "reference-roles.json"
BASE_REQUIRED = {
    "cover": {"illustration_style", "cover_layout", "subject_scale"},
    "practice": {"illustration_style", "practice_layout", "subject_scale", "subject_continuity"},
    "qa": {"illustration_style", "qa_layout", "subject_continuity"},
    "video": {"illustration_style", "video_framing", "subject_continuity"},
    "art": {"illustration_style"},
}

def catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = data["entries"]
    paths = set()
    for entry in entries:
        path = (ASSETS.parent / entry["path"]).resolve()
        path.relative_to(ASSETS.resolve())
        if entry["path"] in paths or not entry["roles"] or digest(path) != entry["sha256"]:
            raise ValueError("Reference role catalog is duplicate, empty or stale")
        if set(entry["roles"]) - set.union(*BASE_REQUIRED.values(), {"home_treatment"}):
            raise ValueError("Unknown reference duty")
        paths.add(entry["path"])
    if paths != {p.relative_to(ASSETS.parent).as_posix() for p in ASSETS.rglob("*.png")}:
        raise ValueError("Every bundled reference PNG needs an explicit scoped role")
    return entries

def resolve(folder, candidate, kind, spec, hashes, completed_at, seen, declarations=()):
    from generation_evidence import check, local, record_path, timestamp, sample_binding
    from check_visual_reviews import check_image
    required = set(BASE_REQUIRED[kind])
    if kind != "art" and is_home_topic(folder): required.add("home_treatment")
    origins = {}
    bindings = {}
    def grant(roles, origin):
        for role in roles: origins.setdefault(role, []).append(origin)
    entries = catalog()
    primary = {"style": {"illustration_style"}, "layout": {"cover_layout", "practice_layout", "qa_layout", "video_framing"}, "scale": {"subject_scale"}, "home": {"home_treatment"}, "subject": set()}
    by_hash = {entry["sha256"]: entry for entry in entries}
    for value, role in declarations:
        if value in by_hash and role is not None and not (set(by_hash[value]["roles"]) & primary.get(role, set())):
            raise ValueError("Reference primary role mismatch: " + by_hash[value]["path"] + " cannot supply " + str(role))
    for entry in entries:
        if entry["sha256"] in hashes:
            grant(entry["roles"], {"type": "bundled", "path": entry["path"], "sha256": entry["sha256"]})
    def inherit(path, source_kind, label):
        if path.resolve() == candidate.resolve(): raise ValueError("Reference cannot inherit from itself")
        errors = check_image(folder, path, source_kind)
        if errors: raise ValueError(label + " lacks a current passing visual inspection: " + "; ".join(errors))
        receipt = receipt_path(folder, path)
        review = json.loads(receipt.read_text(encoding="utf-8"))
        if timestamp(review["reviewed_at"]) > timestamp(completed_at):
            raise ValueError(label + " was inspected after this output was completed")
        errors = check(folder, path, source_kind, seen)
        if errors: raise ValueError(label + " lacks valid generation evidence: " + "; ".join(errors))
        evidence = record_path(folder, path)
        data = json.loads(evidence.read_text(encoding="utf-8"))
        origin = {"type": label, "path": path.relative_to(folder).as_posix(), "sha256": digest(path),
                  "review_sha256": digest(receipt), "evidence_sha256": digest(evidence)}
        roles = set(data["reference_coverage"]["covered"])
        if label == "current_topic_cover":
            # A cover does not establish the practice, Q&A or video page layout.
            roles &= {"illustration_style", "subject_scale", "home_treatment"}
        roles.add("subject_continuity")
        grant(roles, origin)
        for bound in [path, receipt, evidence]: bindings[bound.relative_to(folder).as_posix()] = digest(bound)
    cover = folder / "01-cover.png"
    if kind != "cover" and cover.is_file() and digest(cover) in hashes:
        inherit(cover, "cover", "current_topic_cover")
    sample = spec.get("sample")
    if kind in ("qa", "video") and sample != "self":
        path = local(folder, sample)
        if digest(path) not in hashes:
            raise ValueError("Later pages must actually use the inspected sample as an image input; sample metadata alone is insufficient")
        sample_binding(folder, candidate, kind, spec, completed_at)
        inherit(path, kind, "current_topic_sample")
    missing = sorted(required - origins.keys())
    if missing: raise ValueError("Missing reference duties for " + kind + ": " + ", ".join(missing))
    return {"policy_version": 1, "required": sorted(required), "covered": sorted(origins),
            "origins": origins, "catalog_sha256": digest(CATALOG)}, bindings


def main():
    import argparse
    from datetime import datetime, timezone
    from generation_evidence import local
    from check_manifest import check
    parser = argparse.ArgumentParser(description="Preflight planned actual image references; does not prove they were sent or approve aesthetics.")
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("--kind", choices=list(BASE_REQUIRED), required=True)
    parser.add_argument("--references", nargs="+", required=True, help="Topic-relative snapshots that will actually be supplied")
    parser.add_argument("--sample", help="self for first QA/video sample; inspected sample path for later pages")
    parser.add_argument("--method", default="whole_page")
    args = parser.parse_args()
    folder = args.topic_folder.resolve()
    try:
        errors = check(folder / "manifest.json")[0]
        if errors: raise ValueError("Invalid manifest: " + "; ".join(errors))
        hashes = {digest(local(folder, rel)) for rel in args.references}
        spec = {"sample": args.sample, "method": args.method}
        coverage, _ = resolve(folder, folder / "production/planned-output.png", args.kind, spec, hashes, datetime.now(timezone.utc).isoformat(), set())
        print(json.dumps(coverage, ensure_ascii=False, indent=2))
        print("REFERENCE PLAN PASS; actual call linkage and visual inspection are still required.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
        print("REFERENCE PLAN FAIL:", exc)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
