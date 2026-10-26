#!/usr/bin/env python3
"""Export exact English Q&A from a validated topic manifest.

Usage: python export_english_qa.py manifest.json qa-en-only.txt [--force]
No third-party packages are required.
"""

import json
import sys
from pathlib import Path

from check_manifest import check as check_manifest
from manifest_model import load, questions


def render(manifest: Path) -> str:
    data = load(manifest)
    blocks = []
    for qa in questions(data):
        blocks.append(f'{qa["id"]}. Q: {qa["question_en"]}\n   A: {qa["answer_en"]}')
    return "\n\n".join(blocks) + "\n"


def main() -> int:
    if len(sys.argv) not in (3, 4) or (len(sys.argv) == 4 and sys.argv[3] != "--force"):
        print("Usage: python export_english_qa.py manifest.json qa-en-only.txt [--force]", file=sys.stderr)
        return 2
    manifest = Path(sys.argv[1])
    output = Path(sys.argv[2])
    errors, warnings, count = check_manifest(manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    count = len(questions(load(manifest)))
    content = render(manifest)
    if output.exists() and output.read_text(encoding="utf-8-sig") == content:
        print(f"PASS: {count} English Q&A pairs already match {output}")
        return 0
    if output.exists() and "--force" not in sys.argv:
        print(f"ERROR: {output} exists with different content; use --force only for an approved update", file=sys.stderr)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"PASS: wrote {count} English Q&A pairs to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
