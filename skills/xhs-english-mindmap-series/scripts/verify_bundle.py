#!/usr/bin/env python3
"""Verify the unpacked skill's inventory, references, syntax and image dependencies."""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    errors = []
    if sys.version_info < (3, 10):
        errors.append("Python 3.10 or newer is required")
    try:
        release = json.loads((root / "release.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
        if manifest["version"] != release["version"]:
            errors.append("Release and inventory versions differ")
        inventory = manifest["files_sha256"]
        actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc" and p.name != "bundle-manifest.json"}
        if actual != set(inventory):
            errors.append(f"File inventory differs: missing={sorted(set(inventory)-actual)}, extra={sorted(actual-set(inventory))}")
        for rel, expected in inventory.items():
            path = (root / rel).resolve()
            path.relative_to(root)
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append(f"Missing or modified file: {rel}")
        for path in (root / "scripts").glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8-sig"))
        for path in [root / "SKILL.md", root / "MIGRATION.md", *list((root / "references").glob("*.md"))]:
            for rel in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8-sig")):
                if not rel.startswith(("http:", "https:", "#")) and not (path.parent / rel.split("#")[0]).is_file():
                    errors.append(f"Broken documentation link: {path.name} -> {rel}")
        from PIL import Image
        for path in (root / "assets").rglob("*.png"):
            with Image.open(path) as im:
                im.verify()
        from reference_roles import catalog
        catalog()
        print(f"Version: {release['version']}; files checked: {len(inventory)}; reference PNGs: {len(list((root/'assets').rglob('*.png')))}")
    except (OSError, ValueError, KeyError, SyntaxError, ImportError) as exc:
        errors.append(str(exc))
    for error in errors:
        print("ERROR:", error)
    if errors:
        print("FAIL: install requirements and use a complete, unchanged release folder.")
        return 1
    print("BUNDLE PASS: integrity, references, Python syntax and PNG decoding. Image-generation access and new-topic visual quality still require a real trial.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
