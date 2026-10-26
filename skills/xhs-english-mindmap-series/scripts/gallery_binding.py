"""Bind generated gallery HTML/comparisons to their exact current local inputs."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def candidates(folder):
    result = {}
    for name, kind in (("01-cover.png", "cover"), ("02-picture-practice.png", "practice")):
        if (folder / name).is_file(): result[name] = kind
    for path in sorted(folder.glob("*-qa-*.png")):
        result[path.relative_to(folder).as_posix()] = "qa"
    for path in sorted((folder / "video").glob("*.png")):
        result[path.relative_to(folder).as_posix()] = "video"
    return result

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        self.links += [value for key, value in attrs if key in ("href", "src") and value]

def linked_files(folder):
    parser = Links(); parser.feed((folder / "review-gallery.html").read_text(encoding="utf-8"))
    files = set()
    for value in parser.links:
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path or url.path.startswith(("/", "\\")):
            raise ValueError(f"Gallery link must be a portable local file: {value}")
        path = (folder / unquote(url.path)).resolve()
        rel = path.relative_to(folder.resolve()).as_posix()
        if not path.is_file(): raise ValueError(f"Broken gallery link: {value}")
        files.add(rel)
    return sorted(files)

def write_binding(folder, home, qa_inputs):
    folder = folder.resolve()
    current = candidates(folder)
    outputs = ["review-gallery.html"] + (["qa-review-comparison.jpg"] if qa_inputs else [])
    links = linked_files(folder)
    sources = sorted(set(["manifest.json", *current, *links, *qa_inputs]))
    data = {"schema_version": 1, "home_series": home, "candidates": current,
            "qa_comparison_inputs": qa_inputs, "linked_files": links,
            "sources_sha256": {rel: sha(folder / rel) for rel in sources},
            "outputs_sha256": {rel: sha(folder / rel) for rel in outputs}}
    (folder / "review/gallery-binding.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def check_binding(folder, requested, require_qa=False):
    folder = folder.resolve(); errors = []
    try:
        data = json.loads((folder / "review/gallery-binding.json").read_text(encoding="utf-8"))
        if data.get("schema_version") != 1: errors.append("unknown gallery binding version")
        current = candidates(folder)
        if data.get("candidates") != current: errors.append("gallery image list is stale; rebuild gallery")
        for path, kind in requested:
            rel = path.relative_to(folder).as_posix()
            if data.get("candidates", {}).get(rel) != kind: errors.append(f"gallery omits {rel}")
        links = linked_files(folder)
        if links != data.get("linked_files"): errors.append("gallery links changed after build")
        from generation_evidence import record_path
        for path, _ in requested:
            evidence = record_path(folder, path)
            if evidence.is_file() and evidence.relative_to(folder).as_posix() not in links:
                errors.append("gallery omits current generation evidence; rebuild gallery")
        required_sources = {"manifest.json", *current, *links, *data.get("qa_comparison_inputs", [])}
        if set(data.get("sources_sha256", {})) != required_sources: errors.append("incomplete gallery input binding")
        for rel, expected in {**data["sources_sha256"], **data["outputs_sha256"]}.items():
            path = (folder / rel).resolve(); path.relative_to(folder)
            if not path.is_file() or sha(path) != expected: errors.append(f"gallery input/output changed: {rel}")
        if "review-gallery.html" not in data["outputs_sha256"]: errors.append("gallery HTML is not bound")
        if require_qa:
            from review_image import is_home_topic, references, ASSETS
            expected_inputs = [(Path("review/references") / p.relative_to(ASSETS)).as_posix() for p, _ in references("qa", is_home_topic(folder))]
            expected_inputs += [rel for rel, kind in current.items() if kind == "qa"]
            if data.get("qa_comparison_inputs") != expected_inputs: errors.append("Q&A comparison does not bind every current page/reference")
            if "qa-review-comparison.jpg" not in data["outputs_sha256"]: errors.append("Q&A comparison output is not bound")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        errors.append(f"missing, broken or invalid gallery binding: {exc}")
    return errors
