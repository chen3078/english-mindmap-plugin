"""Shared content access: map groups and ordered questions have separate IDs."""
import json
from pathlib import Path

QA_FIELDS = ("question_en", "answer_en", "question_zh", "answer_zh")

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def questions(data):
    """qa_items is authoritative when present; legacy group.qa is read-only fallback."""
    groups = {g["id"]: g for g in data["groups"]}
    if "qa_items" in data:
        items = data["qa_items"]
    else:
        items = [{"id": g["id"], "group_id": g["id"], **g["qa"]} for g in data["groups"]]
    return [{**q, "illustration": q.get("illustration", groups[q["group_id"]].get("illustration", ""))} for q in items]
