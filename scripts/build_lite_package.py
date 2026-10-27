"""Build the independent lite plugin ZIP and copy its original source skill ZIP.

Run after updating the checked-in plugin-bundle-manifest.json. Never rewrites the
source archive or the bundled skill to make a failed integrity check pass.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/english-mindmap-lite"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    release = json.loads((PLUGIN / "release.json").read_text(encoding="utf-8"))
    source = args.source_archive.resolve()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == release["source_archive_sha256"], "Wrong source ZIP"
    with zipfile.ZipFile(source) as z:
        expected = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
    skill = PLUGIN / "skills/english-mindmap"
    actual = {
        "english-mindmap/" + p.relative_to(skill).as_posix(): p.read_bytes()
        for p in skill.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    assert expected == actual, "Bundled skill differs from the user's original ZIP"
    subprocess.run([sys.executable, "-X", "utf8", str(PLUGIN / "scripts/check_plugin.py")], check=True)
    inventory = json.loads((PLUGIN / "plugin-bundle-manifest.json").read_text(encoding="utf-8"))
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    target = out / "English-mindmap-2026.10.27-plugin-portable.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel in sorted([*inventory["files_sha256"], "plugin-bundle-manifest.json"]):
            z.write(PLUGIN / rel, "english-mindmap-lite/" + rel)
    archive = out / source.name
    if archive != source:
        shutil.copyfile(source, archive)
    # GitHub sanitizes non-ASCII asset names; the guide content remains Chinese.
    tutorial = out / "English-mindmap-Migration-zh-CN.md"
    shutil.copyfile(PLUGIN / "INSTALL.zh-CN.md", tutorial)
    # Standalone downloaded tutorial links must work outside the extracted plugin.
    doc = tutorial.read_text(encoding="utf-8").replace(
        "](DELIVERY.zh-CN.md)",
        "](https://github.com/chen3078/english-mindmap-plugin/blob/main/plugins/english-mindmap-lite/DELIVERY.zh-CN.md)"
    )
    tutorial.write_text(doc, encoding="utf-8", newline="\n")
    with (out / "SHA256SUMS.txt").open("w", encoding="utf-8", newline="\n") as f:
        for p in (target, archive, tutorial):
            f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n")
    print("Built:", target)
    print("Source ZIP preserved:", archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
