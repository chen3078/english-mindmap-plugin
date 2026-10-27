#!/usr/bin/env python3
"""Build editable Dog-style bilingual Q&A HTML from a frozen topic manifest.

Usage: python build_qa_pages.py TOPIC_FOLDER [--art-dir DIR] [--page-sizes 3,2,3] [--overwrite]
Requires one related PNG per question in TOPIC_FOLDER/qa-art by default.
Generated HTML needs rendering and visual review before any PNG is accepted.
"""

import argparse
import html
import json
import shutil
from functools import lru_cache
from pathlib import Path

from check_manifest import check as check_manifest
from manifest_model import questions


SKILL = Path(__file__).resolve().parents[1]
CSS = SKILL / "assets" / "templates" / "qa-page.css"
FONTS = SKILL / "assets" / "fonts"


def is_long(group: dict) -> bool:
    qa = group
    return (
        # Dog's approved four-row pages top out around 34/66/24 characters
        # for English question / answer / Chinese answer. Keep longer animal
        # answers on roomier pages instead of reducing the reader-facing type.
        len(qa["question_en"]) > 40
        or len(qa["answer_en"]) > 75
        or len(qa["answer_zh"]) > 25
    )


def paginate(groups: list[dict], page_sizes: list[int] | None = None) -> list[list[dict]]:
    if page_sizes is not None:
        if not page_sizes or any(size < 1 for size in page_sizes) or sum(page_sizes) != len(groups):
            raise ValueError("page sizes must be positive and sum to the number of Q&A groups")
        sizes = tuple(page_sizes)
    else:
        sizes = None

    @lru_cache(None)
    def best(start: int) -> tuple[int, tuple[int, ...]]:
        if start == len(groups):
            return 0, ()
        choices = []
        for size in (4, 3, 2, 1):
            end = start + size
            if end > len(groups):
                continue
            tail_cost, tail_sizes = best(end)
            page_cost = 5 + (100 if size == 2 else 250 if size == 1 else 0)
            if size == 4 and any(is_long(group) for group in groups[start:end]):
                page_cost += 500
            choices.append((page_cost + tail_cost, (size,) + tail_sizes))
        if not choices:
            return 10**9, ()
        return min(choices, key=lambda choice: (choice[0], len(choice[1])))

    if sizes is None:
        sizes = best(0)[1]
    pages = []
    start = 0
    for size in sizes:
        pages.append(groups[start:start + size])
        start += size
    return pages


def row_html(group: dict, art_name: str, index: int) -> str:
    qa = group
    color = ("", "blue", "yellow", "blue")[index % 4]
    esc = html.escape
    return f"""<section class="row {color}">
      <div class="left">
        <div class="number">{group['id']}</div>
        <div class="en question"><span class="badge">Q:</span><span class="words">{esc(qa['question_en'])}</span></div>
        <div class="zh">问：{esc(qa['question_zh'])}</div>
        <div class="en answer"><span class="badge">A:</span><span class="words">{esc(qa['answer_en'])}</span></div>
        <div class="zh">答：{esc(qa['answer_zh'])}</div>
      </div>
      <div class="art-area"><img class="art" src="qa-art/{esc(art_name)}" alt=""></div>
    </section>"""


def page_html(topic: str, brand: str, groups: list[dict]) -> str:
    first, last = groups[0]["id"], groups[-1]["id"]
    rows = "\n".join(row_html(group, f"{group['id']:02d}.png", i) for i, group in enumerate(groups))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1086,initial-scale=1">
<link rel="stylesheet" href="qa-page.css"><title>{html.escape(topic)} Q&A {first}–{last}</title></head>
<body><main class="page">
<header class="header">{html.escape(topic.upper())} · <span class="q">Q</span>&amp;<span class="a">A</span>&nbsp;{first}–{last}</header>
<div class="rows" data-count="{len(groups)}" style="--rows:{len(groups)}">{rows}</div>
<div class="signature">{html.escape(brand)}</div>
</main></body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("--art-dir", type=Path)
    parser.add_argument("--page-sizes", help="comma-separated row counts, e.g. 3,2,3; use after visual review when automatic pagination crowds text")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    folder = args.topic_folder.resolve()
    manifest = folder / "manifest.json"
    errors, warnings, count = check_manifest(manifest)
    if errors:
        parser.error("manifest invalid: " + "; ".join(errors))
    for warning in warnings:
        print("WARNING:", warning)
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    qa_items = questions(data)
    count = len(qa_items)
    art_dir = (args.art_dir or folder / "qa-art").resolve()
    missing = [f"{i:02d}.png" for i in range(1, count + 1) if not (art_dir / f"{i:02d}.png").is_file()]
    if missing:
        parser.error("missing Q&A art in " + str(art_dir) + ": " + ", ".join(missing))
    try:
        requested_sizes = [int(part.strip()) for part in args.page_sizes.split(",")] if args.page_sizes else None
        pages = paginate(qa_items, requested_sizes)
    except ValueError as exc:
        parser.error(str(exc))
    targets = [folder / f"{i+3:02d}-qa-{groups[0]['id']:02d}-{groups[-1]['id']:02d}.html" for i, groups in enumerate(pages)]
    assets = [folder / "qa-page.css", folder / "qa-layout-assets" / "PatrickHand-Regular.ttf", folder / "qa-layout-assets" / "NotoSansSC-VF.ttf"]
    if not args.overwrite and any(path.exists() for path in targets + assets):
        parser.error("generated files already exist; pass --overwrite only when replacement is intended")
    (folder / "qa-art").mkdir(exist_ok=True)
    for i in range(1, count + 1):
        src = art_dir / f"{i:02d}.png"
        dst = folder / "qa-art" / src.name
        if src != dst:
            shutil.copy2(src, dst)
    (folder / "qa-layout-assets").mkdir(exist_ok=True)
    shutil.copy2(CSS, folder / "qa-page.css")
    for filename in ("PatrickHand-Regular.ttf", "NotoSansSC-VF.ttf"):
        shutil.copy2(FONTS / filename, folder / "qa-layout-assets" / filename)
    for target, groups in zip(targets, pages):
        target.write_text(page_html(data["topic_en"], data["brand"], groups), encoding="utf-8")
        print("CREATED:", target)
    print("NEXT: render every HTML at 1086x1448; compare English and Chinese apparent type size/weight plus art with approved Dog pages at phone size; reject smaller or thinner text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
