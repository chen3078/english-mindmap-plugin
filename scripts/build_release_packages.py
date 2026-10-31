"""Build both versioned skill archives and their independent plugin packages."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FULL = ROOT / "skills/xhs-english-mindmap-series"
LITE_PLUGIN = ROOT / "plugins/english-mindmap-lite"
LITE = LITE_PLUGIN / "skills/english-mindmap"


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and not any(part in {"__pycache__", ".git", ".venv", ".validation"}
                                      for part in p.relative_to(root).parts) and p.suffix != ".pyc"}


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(path, payload):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel, data in sorted(payload.items()):
            info = zipfile.ZipInfo(rel, (2026, 11, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for skill in (FULL, LITE):
        payload = files(skill)
        payload.pop("bundle-manifest.json", None)
        save(skill / "bundle-manifest.json", {"name": skill.name, "version": "2026.11.01.1",
             "files_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in payload.items()}})
    full_src = out / "xhs-english-mindmap-series-portable-v2026.11.01.1-centered-layout.zip"
    lite_src = out / "English-mindmap-2026.11.01.zip"
    for skill, target in ((FULL, full_src), (LITE, lite_src)):
        archive(target, {skill.name + "/" + k: v for k, v in files(skill).items()})
    for plugin, src, old in ((ROOT, full_src, "xhs-english-mindmap-series-portable-v2026.10.26.3-connector-quality.zip"),
                             (LITE_PLUGIN, lite_src, "English-mindmap-2026.10.27.zip")):
        release = json.loads((plugin / "release.json").read_text(encoding="utf-8"))
        release.update(plugin_version="1.0.1", skill_version="2026.11.01.1", layout_policy=1,
                       source_archive=src.name, source_archive_sha256=digest(src), derived_from_archive=old)
        if plugin == LITE_PLUGIN:
            release.update(release_tag="lite-v1.0.1", full_edition_unchanged=False,
                           full_edition_scope_unchanged=True, source_skill_bytes_unchanged=True)
        save(plugin / "release.json", release)
    payload = files(LITE_PLUGIN)
    payload.pop("plugin-bundle-manifest.json", None)
    save(LITE_PLUGIN / "plugin-bundle-manifest.json", {"plugin_version": "1.0.1",
         "files_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in payload.items()}})
    for script in (ROOT / "scripts/check_plugin.py", LITE_PLUGIN / "scripts/check_plugin.py"):
        subprocess.run([sys.executable, "-X", "utf8", str(script)], check=True)
    archive(out / "English-mindmap-2026.11.01-plugin-portable.zip",
            {"english-mindmap-lite/" + k: v for k, v in files(LITE_PLUGIN).items()})
    # A full-edition standalone package has only its own marketplace entry.
    payload = {"skills/xhs-english-mindmap-series/" + k: v for k, v in files(FULL).items()}
    payload.update({"skills/english-mindmap-setup/" + k: v
                    for k, v in files(ROOT / "skills/english-mindmap-setup").items()})
    for rel in ("plugin.json", ".codex-plugin/plugin.json", "release.json", "README.md",
                "INSTALL.zh-CN.md", "CHANGELOG.md", "scripts/check_plugin.py"):
        payload[rel] = (ROOT / rel).read_bytes()
    market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    market["plugins"] = [p for p in market["plugins"] if p["name"] == "english-mindmap"]
    payload[".agents/plugins/marketplace.json"] = (json.dumps(market, ensure_ascii=False, indent=2) + "\n").encode()
    payload["README.md"] = payload["README.md"].replace(
        b"](plugins/english-mindmap-lite/", b"](https://github.com/chen3078/english-mindmap-plugin/blob/main/plugins/english-mindmap-lite/")
    archive(out / "english-mindmap-plugin-v1.0.1.zip", {"english-mindmap-plugin/" + k: v for k, v in payload.items()})
    for src, name in ((ROOT / "INSTALL.zh-CN.md", "Full-Migration-zh-CN.md"),
                      (LITE_PLUGIN / "INSTALL.zh-CN.md", "Lite-Migration-zh-CN.md"),
                      (LITE / "references/layout-balance.md", "Layout-Checks-zh-CN.md")):
        doc = src.read_text(encoding="utf-8")
        if name == "Lite-Migration-zh-CN.md":
            doc = doc.replace("](DELIVERY.zh-CN.md)", "](https://github.com/chen3078/english-mindmap-plugin/blob/main/plugins/english-mindmap-lite/DELIVERY.zh-CN.md)")
        # The standalone checklist's two introductory references remain prose, not broken local links.
        (out / name).write_text(doc, encoding="utf-8", newline="\n")
    targets = [p for p in sorted(out.iterdir()) if p.is_file() and p.name != "SHA256SUMS.txt"]
    (out / "SHA256SUMS.txt").write_text("".join(digest(p) + "  " + p.name + "\n" for p in targets), encoding="utf-8", newline="\n")
    for p in targets:
        print(p.name, p.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
