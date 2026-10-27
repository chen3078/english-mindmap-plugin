#!/usr/bin/env python3
"""Validate map groups, independent Q&A IDs, and new-topic heading rules."""
import re
import sys
from pathlib import Path
from manifest_model import QA_FIELDS, load, questions

def check(path):
    errors, warnings = [], []
    try:
        data = load(path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"Cannot read JSON: {exc}"], warnings, 0
    if not isinstance(data, dict):
        return ["The manifest root must be a JSON object"], warnings, 0
    for key in ("topic_en", "topic_zh", "category", "audience", "brand"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be a nonempty string")
    if data.get("audience") not in ("children", "adult_beginner"):
        errors.append("audience must be children or adult_beginner")
    if data.get("brand") != "新陈代谢（英语版）":
        errors.append("brand differs from the approved fixed signature")
    mode = data.get("manifest_mode", "current")
    if mode not in ("current", "legacy"):
        errors.append("manifest_mode must be current or legacy")
    if mode == "legacy":
        if not isinstance(data.get("legacy_manifest_reason"), str) or not data["legacy_manifest_reason"].strip():
            errors.append("legacy manifest mode requires legacy_manifest_reason for existing approved content")
        warnings.append("Explicit legacy manifest: do not apply this exception to new topics")
    elif "visual_family" not in data:
        errors.append("New topics require explicit visual_family: home or general; do not infer the series from the object name")
    if "visual_family" in data and data["visual_family"] not in ("home", "general"):
        errors.append("visual_family must be home or general")
    policy = data.get("heading_policy", "current")
    if policy not in ("current", "legacy"):
        errors.append("heading_policy must be current or legacy")
    legacy = policy == "legacy"
    if legacy:
        if not isinstance(data.get("legacy_heading_reason"), str) or not data["legacy_heading_reason"].strip():
            errors.append("legacy heading policy requires legacy_heading_reason for an existing approved topic")
        warnings.append("Legacy heading exception: do not use it to bypass current rules for a new topic")
    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        return errors + ["groups must be a nonempty array"], warnings, 0
    if not 6 <= len(groups) <= 9:
        warnings.append(f"{len(groups)} groups: keep this count only if the topic warrants it")
    headings = set()
    for index, group in enumerate(groups, 1):
        prefix = f"group {index}"
        if not isinstance(group, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if type(group.get("id")) is not int or group["id"] != index:
            errors.append(f"{prefix} id must be {index}")
        for key in ("heading_en", "illustration"):
            if not isinstance(group.get(key), str) or not group[key].strip():
                errors.append(f"{prefix} {key} must be a nonempty string")
        heading = group.get("heading_en", "")
        if isinstance(heading, str):
            folded = heading.strip().casefold()
            if folded in headings:
                errors.append(f"{prefix} repeats a heading: {heading}")
            headings.add(folded)
            if re.search(r"[\u3400-\u9fff]", heading):
                errors.append(f"{prefix} heading_en contains Chinese")
            if not legacy:
                if index == 1 and heading != "What":
                    errors.append("First heading_en must be exactly What")
                dimension = str(group.get("dimension", "")).casefold()
                location = dimension == "location" or bool(re.match(r"^(where\b|locations?\b|habitats?\b|places?\b)", folded))
                if location and heading != "Where":
                    errors.append(f"{prefix} location heading must be exactly Where")
                plant = "plant" in str(data.get("category", "")).casefold()
                needs = dimension == "needs" or bool(re.match(r"^(needs?\b|growth requirements?\b|what helps .+ grow\b)", folded))
                if plant and needs and heading != "Needs":
                    errors.append(f"{prefix} growth-requirements heading must be exactly Needs")
                if heading.endswith(("?", "？")):
                    errors.append(f"{prefix} map heading must be a section label, not a question")
        keywords = group.get("keywords_en")
        if not isinstance(keywords, list) or not keywords or any(not isinstance(k, str) or not k.strip() for k in keywords):
            errors.append(f"{prefix} keywords_en must contain nonempty strings")
        elif len({k.strip().casefold() for k in keywords}) != len(keywords) or any(re.search(r"[\u3400-\u9fff]", k) for k in keywords):
            errors.append(f"{prefix} keywords_en has duplicates or Chinese")
    if "qa_items" in data:
        items = data["qa_items"]
        if not isinstance(items, list) or not items:
            errors.append("qa_items must be a nonempty array; it cannot silently fall back to group.qa")
            items = []
    else:
        items = [{"id": i, "group_id": i, **(g.get("qa") if isinstance(g, dict) and isinstance(g.get("qa"), dict) else {})} for i, g in enumerate(groups, 1)]
    seen = {"question_en": set(), "answer_en": set()}
    covered = set()
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            errors.append(f"question {index} must be an object")
            continue
        if type(item.get("id")) is not int or item["id"] != index:
            errors.append(f"question {index} id must be {index}")
        group_id = item.get("group_id")
        if type(group_id) is not int or not 1 <= group_id <= len(groups):
            errors.append(f"question {index} group_id must reference an existing group")
        else:
            covered.add(group_id)
        for field in QA_FIELDS:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"question {index} missing {field}")
                continue
            if field in seen:
                folded = value.strip().casefold()
                if folded in seen[field]:
                    errors.append(f"question {index} repeats {field}")
                seen[field].add(folded)
            if field.startswith("question") and not value.strip().endswith(("?", "？")):
                warnings.append(f"question {index} {field} may lack a question mark")
        if re.search(r"\d", str(item.get("answer_en", ""))) and not item.get("source_urls"):
            warnings.append(f"question {index} numeric claim needs source review")
    if set(range(1, len(groups) + 1)) != covered:
        errors.append("Every map group must have at least one linked question")
    from content_coverage import check_content
    content_errors, content_warnings = check_content(data, items)
    errors.extend(content_errors); warnings.extend(content_warnings)
    return errors, warnings, len(groups)

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_manifest.py manifest.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]); errors, warnings, count = check(path)
    for message in errors: print("ERROR:", message)
    for message in warnings: print("WARNING:", message)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); return 1
    print(f"PASS: {count} map groups; {len(questions(load(path)))} ordered questions; {len(warnings)} warning(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
