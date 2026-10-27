#!/usr/bin/env python3
"""Bind observed generation/composition records to images; never authenticate a provider.

Register: generation_evidence.py TOPIC PNG --kind KIND --spec JSON
Check:    generation_evidence.py TOPIC PNG --kind KIND --check
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from review_image import ASSETS, digest, is_home_topic, receipt_path, references

KINDS = ("cover", "practice", "qa", "art")

def local(folder, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError("Evidence paths must be relative to the topic folder")
    path = (folder / rel).resolve(); path.relative_to(folder.resolve())
    if not path.is_file(): raise ValueError(f"Missing evidence file: {rel}")
    return path

def record_path(folder, candidate):
    rel = candidate.resolve().relative_to(folder.resolve()).with_suffix("").as_posix().replace("/", "--")
    return folder / "production/records" / (rel + ".json")

def timestamp(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None: raise ValueError("Evidence timestamps must include timezone")
    return value

def collect(folder, candidate, kind, spec, seen=None):
    seen = set() if seen is None else set(seen)
    rel = candidate.relative_to(folder).as_posix()
    if rel in seen: raise ValueError("Evidence parent cycle")
    seen.add(rel)
    if spec.get("mode") not in ("generated", "composed"):
        raise ValueError("Evidence mode must be generated or composed; missing evidence remains unverified")
    if not isinstance(spec.get("method"), str) or not spec["method"].strip():
        raise ValueError("Record the actual production method")
    sources = {rel: digest(candidate), "manifest.json": digest(folder / "manifest.json")}
    reference_hashes = []
    artifact_hashes = []
    declarations = []
    if spec["mode"] == "generated":
        event_path = local(folder, spec.get("event_file"))
        event = json.loads(event_path.read_text(encoding="utf-8-sig"))
        sources[event_path.relative_to(folder).as_posix()] = digest(event_path)
        if event.get("record_source") not in ("observed_tool_call", "provider_export"):
            raise ValueError("No captured/observed tool event; execution is unverified")
        if event.get("record_source") == "provider_export" or event.get("raw_event_file"):
            raw = local(folder, event.get("raw_event_file"))
            if event.get("raw_event_sha256") != digest(raw): raise ValueError("Missing or changed raw provider export")
            sources[raw.relative_to(folder).as_posix()] = digest(raw)
        if not isinstance(event.get("tool"), str) or not event["tool"].strip():
            raise ValueError("Tool event needs the actual tool name")
        request, response = event.get("request", {}), event.get("response", {})
        prompt = request.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Tool event must contain the actual full prompt")
        if response.get("status") != "succeeded": raise ValueError("Tool response is not successful")
        timestamp(response.get("completed_at", ""))
        refs = request.get("reference_images")
        if not isinstance(refs, list) or not refs: raise ValueError("Actual reference-image inputs must be recorded")
        for ref in refs:
            path = local(folder, ref.get("path"))
            value = digest(path)
            if ref.get("sha256") != value: raise ValueError("Reference input changed or lacks its captured SHA-256")
            if ref.get("role") not in ("style", "layout", "subject", "scale", "home"):
                raise ValueError("Every reference needs its actual role")
            sources[path.relative_to(folder).as_posix()] = value
            reference_hashes.append(value)
            declarations.append((value, ref["role"]))
        outputs = response.get("outputs", [])
        if not any(o.get("sha256") == digest(candidate) for o in outputs if isinstance(o, dict)):
            raise ValueError("Candidate bytes are not a recorded tool output; record resize/typesetting as a composed step")
        # QA text belongs in the actual complete-page prompt, never an empty sheet.
        if kind == "qa":
            from review_image import expected_content
            content = expected_content(folder, candidate, kind)
            if content.get("warning"): raise ValueError(content["warning"])
            for q in content["qa_items"]:
                for field in ("question_en", "answer_en", "question_zh", "answer_zh"):
                    if q[field] not in prompt: raise ValueError(f"Complete-page prompt omits question {q['id']} {field}")
        completed_at = response["completed_at"]
    else:
        recipe_path = local(folder, spec.get("recipe_file"))
        recipe = json.loads(recipe_path.read_text(encoding="utf-8-sig"))
        if not isinstance(recipe.get("operation"), str) or not recipe["operation"].strip():
            raise ValueError("Composition recipe must name the actual operation")
        timestamp(recipe.get("completed_at", ""))
        inputs = recipe.get("input_files", [])
        if not isinstance(inputs, list) or not inputs: raise ValueError("Composition recipe must bind its actual inputs")
        for item in inputs:
            path = local(folder, item.get("path")); value = digest(path)
            if item.get("sha256") != value: raise ValueError("Composition input changed")
            sources[path.relative_to(folder).as_posix()] = value
            artifact_hashes.append(value)
        if recipe.get("output_sha256") != digest(candidate): raise ValueError("Composition output differs from candidate")
        sources[recipe_path.relative_to(folder).as_posix()] = digest(recipe_path)
        for ref in recipe.get("layout_references", []):
            path = local(folder, ref.get("path")); value = digest(path)
            if ref.get("sha256") != value: raise ValueError("Composition layout reference changed")
            sources[path.relative_to(folder).as_posix()] = value
            reference_hashes.append(value)
            declarations.append((value, ref.get("role")))
        parents = spec.get("parents", [])
        if not isinstance(parents, list) or not parents: raise ValueError("Composed images need their generated/composed parent artifacts")
        for parent in parents:
            path = local(folder, parent)
            if path.relative_to(folder).as_posix() not in sources: raise ValueError("Parent missing from composition recipe inputs")
            parent_record = record_path(folder, path)
            errors = check(folder, path, "art", seen, enforce_kind=False)
            if errors: raise ValueError("Unverified parent: " + "; ".join(errors))
            sources[parent_record.relative_to(folder).as_posix()] = digest(parent_record)
            parent_data = json.loads(parent_record.read_text(encoding="utf-8"))
            sources.update(parent_data["sources_sha256"])
            reference_hashes += parent_data.get("reference_hashes", [])
        completed_at = recipe["completed_at"]
    from reference_roles import resolve
    coverage, bindings = resolve(folder, candidate, kind, spec, set(reference_hashes + artifact_hashes), completed_at, seen, declarations)
    sources.update(bindings)
    return sources, sorted(set(reference_hashes)), completed_at, coverage

def sample_binding(folder, candidate, kind, spec, completed_at):
    if kind not in ("qa",): return None
    sample = spec.get("sample")
    if sample == "self": return {"role": "sample"}
    path = local(folder, sample)
    if path == candidate: raise ValueError("Use sample=self for the representative sample")
    from check_visual_reviews import check_image
    errors = check_image(folder, path, kind)
    if errors: raise ValueError("Representative sample has not passed current visual inspection")
    receipt = receipt_path(folder, path)
    data = json.loads(receipt.read_text(encoding="utf-8"))
    if timestamp(data["reviewed_at"]) > timestamp(completed_at):
        raise ValueError("This image was completed before the sample review; do not claim sample-first production")
    sample_record = record_path(folder, path)
    source = json.loads(sample_record.read_text(encoding="utf-8"))
    if source.get("kind") != kind or source.get("spec", {}).get("sample") != "self" or source.get("method") != spec["method"]:
        raise ValueError("Sample method differs; a method change needs a new representative sample")
    errors = check(folder, path, kind)
    if errors: raise ValueError("Representative sample generation evidence is no longer valid")
    return {"role": "follows_sample", "candidate": path.relative_to(folder).as_posix(),
            "candidate_sha256": digest(path), "review_sha256": digest(receipt),
            "evidence_sha256": digest(sample_record)}

def register(folder, candidate, kind, spec):
    folder, candidate = folder.resolve(), candidate.resolve()
    sources, ref_hashes, completed_at, coverage = collect(folder, candidate, kind, spec)
    sample = sample_binding(folder, candidate, kind, spec, completed_at)
    record = {"schema_version": 1, "candidate": candidate.relative_to(folder).as_posix(), "kind": kind,
              "method": spec["method"], "spec": spec, "sources_sha256": sources,
              "reference_hashes": ref_hashes, "reference_coverage": coverage, "sample": sample, "completed_at": completed_at,
              "recorded_at": datetime.now(timezone.utc).isoformat(), "evidence_status": "linked_record",
              "execution_authenticity": "not_independently_verified",
              "note": "Local linkage checks do not authenticate provider execution or certify visual quality."}
    path = record_path(folder, candidate); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

def check(folder, candidate, kind, seen=None, enforce_kind=True):
    folder, candidate = folder.resolve(), candidate.resolve()
    try:
        path = record_path(folder, candidate)
        data = json.loads(path.read_text(encoding="utf-8"))
        if enforce_kind and data.get("kind") != kind: raise ValueError("Evidence format differs from candidate")
        if data.get("candidate") != candidate.relative_to(folder).as_posix(): raise ValueError("Evidence belongs to another candidate")
        if data.get("evidence_status") != "linked_record" or data.get("execution_authenticity") != "not_independently_verified":
            raise ValueError("Unverified/mislabelled evidence; no independent execution authentication is implemented")
        sources, refs, completed, coverage = collect(folder, candidate, data["kind"], data["spec"], seen)
        if sources != data.get("sources_sha256") or refs != data.get("reference_hashes") or completed != data.get("completed_at"):
            raise ValueError("Generation inputs, recipe, parents or candidate changed after evidence capture")
        if coverage != data.get("reference_coverage"):
            raise ValueError("Reference duties, catalog or inherited reference approvals changed")
        if sample_binding(folder, candidate, data["kind"], data["spec"], completed) != data.get("sample"):
            raise ValueError("Sample, sample inspection or sample evidence changed")
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
        return [f"{candidate.name}: generation evidence missing/invalid: {exc}"]
    return []

def check_samples(folder, images):
    errors = []
    for kind in ("qa",):
        paths = [path for path, k in images if k == kind]
        if not paths: continue
        try:
            data = [json.loads(record_path(folder, path).read_text(encoding="utf-8")) for path in paths]
            samples = [d["candidate"] for d in data if d.get("sample", {}).get("role") == "sample"]
            if len(samples) != 1: raise ValueError(f"{kind} needs exactly one representative sample, not one self-approved sample per page")
            if any(d.get("sample", {}).get("role") == "follows_sample" and d["sample"]["candidate"] != samples[0] for d in data):
                raise ValueError("Pages follow different representative samples")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(f"{kind} sample evidence: {exc}")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path); parser.add_argument("candidate")
    parser.add_argument("--kind", required=True, choices=KINDS)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--spec", type=Path); group.add_argument("--check", action="store_true")
    args = parser.parse_args(); folder = args.topic_folder.resolve()
    try:
        candidate = local(folder, args.candidate)
        if args.spec:
            spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
            print("RECORDED:", register(folder, candidate, args.kind, spec))
        errors = check(folder, candidate, args.kind)
        for error in errors: print("ERROR:", error)
        print("Evidence linkage:", "FAIL/UNVERIFIED" if errors else "PASS; remote execution authenticity remains independently unverified")
        return 1 if errors else 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print("UNVERIFIED:", exc); return 1

if __name__ == "__main__":
    raise SystemExit(main())
