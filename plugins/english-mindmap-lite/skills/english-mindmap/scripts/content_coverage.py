"""Check explicit content coverage; human review still validates relevance and facts."""
import re

DIMENSIONS = ("identity", "features", "composition", "types", "use", "acquisition_care", "origin", "process", "extension")
PROFILES = {
    "manufactured_object": {"manufacturing"},
    "food": {"processing", "cooking", "growth", "supply_chain"},
    "animal": {"growth", "life_cycle", "behavior"},
    "plant": {"growth", "life_cycle"},
    "transport": {"manufacturing", "operation", "supply_chain"},
    "other": {"manufacturing", "processing", "cooking", "growth", "life_cycle", "behavior", "operation", "supply_chain"},
}

def category_profile(category):
    category = str(category).strip().casefold().replace("-", "_").replace(" ", "_")
    if any(x in category for x in ("everyday_object", "home_object", "household", "manufactured", "furniture", "clothing", "appliance", "clothes")): return "manufactured_object"
    for word, profile in [("food", "food"), ("drink", "food"), ("animal", "animal"), ("plant", "plant"), ("transport", "transport"), ("vehicle", "transport")]:
        if word in category: return profile
    return None

def check_content(data, items):
    errors, warnings = [], []
    if data.get("manifest_mode") == "legacy":
        if data.get("content_plan") is None:
            return [], ["Historical content has no coverage plan: retained as legacy, not validated under the new content standard"]
    plan = data.get("content_plan")
    if not isinstance(plan, dict): return ["content_plan is required for new topics; consider sources, materials and processes before rendering"], warnings
    if plan.get("version") != 1: errors.append("content_plan.version must be 1")
    profile = plan.get("profile")
    if not isinstance(profile, str) or profile not in PROFILES:
        return errors + ["content_plan.profile is invalid"], warnings
    inferred = category_profile(data.get("category"))
    if inferred and inferred != profile:
        errors.append("content_plan.profile disagrees with category; do not relabel objects to skip manufacturing")
    if not inferred and not isinstance(plan.get("profile_reason"), str):
        errors.append("Unrecognized category needs content_plan.profile_reason")
    elif not inferred and not plan.get("profile_reason", "").strip():
        errors.append("Unrecognized category needs a nonempty profile_reason")
    scope = plan.get("scope", "full")
    if scope not in ("full", "focused"): errors.append("content_plan.scope must be full or focused")
    if scope == "focused" and (not isinstance(plan.get("user_scope_instruction"), str) or not plan["user_scope_instruction"].strip()):
        errors.append("Focused content requires the actual user_scope_instruction; page count is not a scope instruction")
    dims = plan.get("dimensions")
    if not isinstance(dims, dict): return errors + ["content_plan.dimensions must explicitly consider all nine dimensions"], warnings
    if set(dims) != set(DIMENSIONS):
        errors.append("content_plan.dimensions must consider exactly: " + ", ".join(DIMENSIONS))
    questions = {q["id"]: q for q in items if isinstance(q, dict) and type(q.get("id")) is int}
    assigned = set()
    included = set()
    for key in DIMENSIONS:
        entry = dims.get(key)
        if not isinstance(entry, dict):
            errors.append("content dimension missing/invalid: " + key); continue
        status = entry.get("status")
        if status not in ("included", "omitted", "not_applicable"):
            errors.append(key + ": status must be included, omitted or not_applicable"); continue
        ids = entry.get("question_ids", [])
        if not isinstance(ids, list) or any(type(i) is not int or i not in questions for i in ids):
            errors.append(key + ": question_ids must reference actual question IDs"); continue
        if len(ids) != len(set(ids)): errors.append(key + ": repeated question IDs")
        if status != "included":
            if ids: errors.append(key + ": an excluded dimension cannot bind questions")
            if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
                errors.append(key + ": omission/non-applicability needs a topic-specific reason")
            continue
        if not ids: errors.append(key + ": included dimension needs actual questions")
        included.add(key); assigned.update(ids)
        if key == "process":
            if entry.get("kind") not in PROFILES[profile]:
                errors.append("Process kind is inappropriate for this profile")
            steps = entry.get("steps")
            if not isinstance(steps, list) or len(steps) < 2:
                errors.append("Process needs at least two meaningful ordered steps tied to actual answers"); continue
            answers = " ".join(str(questions[i].get("answer_en", "")) for i in ids).casefold()
            cursor = 0
            for step in steps:
                if not isinstance(step, str) or not step.strip():
                    errors.append("Process steps must be nonempty answer excerpts"); continue
                pos = answers.find(step.strip().casefold(), cursor)
                if pos < 0: errors.append("Process step is absent or out of order in the linked English answer: " + step)
                else: cursor = pos + len(step.strip())
            for i in ids:
                question = str(questions[i].get("question_en", "")).casefold()
                if re.search(r"\bmade\s+(?:of|from|out of)\b", question) and not re.search(r"\b(how|steps|process)\b", question):
                    errors.append("A material/ingredient question cannot substitute for how it is made; add a separate process question")
    if "identity" not in included: errors.append("Full identity/definition coverage is required")
    if assigned != set(questions): errors.append("Every question must have an explicit learning dimension in content_plan")
    if scope == "full" and profile == "manufactured_object":
        if "composition" not in included: errors.append("Manufactured objects need material/part coverage")
        if "process" not in included: errors.append("Full manufactured-object topics require how it is made; cleaning/use/materials are not manufacturing")
    if scope == "full" and profile == "food" and not ({"origin", "process"} & included):
        errors.append("Food topics need an actual source/growth/making path, not only appearance and eating")
    if "process" in included and profile == "manufactured_object":
        if dims["process"].get("kind") != "manufacturing":
            errors.append("For manufactured objects the process dimension must explain manufacturing, not use or cleaning")
        process_ids = dims["process"].get("question_ids", [])
        valid_questions = [str(questions[i].get("question_en", "")).casefold() for i in process_ids if type(i) is int and i in questions] if isinstance(process_ids, list) else []
        if not any(re.search(r"\b(how|steps|process)\b", q) and re.search(r"\b(make|makes|making|made|manufactur\w*|produc\w*|assembl\w*|build|built|construct\w*)\b", q) for q in valid_questions):
            errors.append("Manufacturing needs a clear how-made question; use/cleaning questions cannot substitute")
    if "process" not in included:
        warnings.append("No process question selected: manually review the topic-specific omission reason")
    warnings.append("Content plan linkage does not certify factual accuracy, relevance, true process steps or genuine user scope")
    return errors, warnings
