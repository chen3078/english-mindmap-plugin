"""Verify this plugin, its wrapper inventory, and the unchanged bundled skill."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def files(root):
    return {
        p.relative_to(root).as_posix(): p
        for p in root.rglob("*")
        if p.is_file()
        and not any(part in {"__pycache__", ".venv", ".git", ".validation"} for part in p.relative_to(root).parts)
        and p.suffix != ".pyc"
        and p.name != "plugin-bundle-manifest.json"
    }


def main():
    try:
        portable = load(ROOT / "plugin.json")
        compat = load(ROOT / ".codex-plugin/plugin.json")
        market = load(ROOT / ".agents/plugins/marketplace.json")
        release = load(ROOT / "release.json")
        skill = ROOT / "skills/english-mindmap"
        for key in ("name", "version", "description"):
            assert portable[key] == compat[key], f"Manifest identity mismatch: {key}"
        assert portable["name"] == "english-mindmap-lite"
        assert compat["skills"] == "./skills/"
        assert portable["extensions"]["com.openai"]["requires_local_executor"] is True
        assert portable["version"] == release["plugin_version"]
        assert release["skill_version"] == load(skill / "release.json")["version"] == "2026.10.27.1"
        assert load(skill / "release.json")["deliverables"] == ["cover", "practice", "qa"]
        assert len(list((skill / "assets").rglob("*.png"))) == release["reference_pngs"] == 16
        assert market["name"] == "english-mindmap-lite-local"
        assert len(market["plugins"]) == 1
        entry = market["plugins"][0]
        assert entry["name"] == portable["name"]
        assert (ROOT / entry["source"]["path"]).resolve() == ROOT
        for manifest in (portable, compat):
            rel = manifest["extensions"]["com.openai"]["onboardingSkill"]
            assert rel.startswith("./") and ".." not in Path(rel).parts
            path = (ROOT / rel).resolve()
            path.relative_to(ROOT)
            assert path.is_file(), "Missing onboarding skill"
        assert {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()} == {
            "english-mindmap", "english-mindmap-lite-setup"
        }
        for name in ("README.md", "INSTALL.zh-CN.md", "DELIVERY.zh-CN.md"):
            assert (ROOT / name).is_file(), f"Missing Chinese documentation: {name}"
        inventory = load(ROOT / "plugin-bundle-manifest.json")
        assert inventory["plugin_version"] == portable["version"]
        actual = files(ROOT)
        expected = inventory["files_sha256"]
        assert actual.keys() == expected.keys(), "Plugin inventory differs"
        for rel, path in actual.items():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected[rel], f"Modified plugin file: {rel}"
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        print("LITE PLUGIN FAIL:", exc)
        return 1
    result = subprocess.run([sys.executable, "-X", "utf8", str(skill / "scripts/verify_bundle.py")])
    if result.returncode:
        return result.returncode
    print(f"LITE PLUGIN PASS: {len(actual)} files, manifests, local marketplace, onboarding, unchanged skill, 16 references.")
    print("Image tools and actual new-topic quality require separate checks in the user's environment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
