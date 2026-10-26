"""Validate portable/compat manifests, marketplace and bundled skill."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    portable = load(ROOT / "plugin.json")
    compat = load(ROOT / ".codex-plugin/plugin.json")
    market = load(ROOT / ".agents/plugins/marketplace.json")
    assert all(portable[k] == compat[k] for k in ["name", "version", "description"]), "Manifest identity mismatch"
    assert compat["skills"] == "./skills/"
    assert market["plugins"][0]["name"] == portable["name"]
    assert (ROOT / market["plugins"][0]["source"]["path"]).resolve() == ROOT
    for manifest in [portable, compat]:
        path = (ROOT / manifest["extensions"]["com.openai"]["onboardingSkill"]).resolve()
        path.relative_to(ROOT)
        assert path.is_file()
    skill = ROOT / "skills/xhs-english-mindmap-series"
    release = load(ROOT / "release.json")
    assert release["skill_version"] == load(skill / "release.json")["version"] == "2026.10.26.3"
    assert release["plugin_version"] == portable["version"]
    for name in ["README.md", "INSTALL.zh-CN.md"]:
        assert "GITHUB_REPOSITORY" not in (ROOT / name).read_text(encoding="utf-8"), "Repository not finalized"
    result = subprocess.run([sys.executable, "-X", "utf8", str(skill / "scripts/verify_bundle.py")])
    if result.returncode:
        return result.returncode
    print("PLUGIN PACKAGE PASS: manifests, marketplace, setup and bundled skill.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
