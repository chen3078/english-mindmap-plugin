# Reference comparisons and inspection after every image

Run this workflow after **each saved final candidate**, including every later Q&A page, and after every edit. A first sample pass never approves the later images. Internal illustration layers are not finished pages; check the complete exported PNG after composition.

## Reference selection

Use the approved files listed in [visual-system.md](visual-system.md). Key/Cup control drawing style, Cat/Dog cover composition, Carrot subject scale only, Window home-object treatment, and Dog/Rabbit Q&A layout. Compare practice and Q&A art with the **current topic cover** for subject continuity.

The existing 16 PNGs cover these roles. Add a reference only when the user has accepted that exact finished image and it fills an identified gap (for example, a long-answer Q&A layout or a different object silhouette). Record its role and approval provenance in the visual reference table, bundle its file, and update the script's `references()` list if it belongs in routine comparisons. Do not automatically promote a newly generated or self-reviewed image to an approved cross-topic template. More references with conflicting roles can reduce consistency.

## Per-image command

Requires Python and Pillow (`python -m pip install Pillow`). Resolve scripts relative to the installed skill directory; the example commands below run from that directory. Save the PNG inside its topic folder first. Keep the image generator's active cache copy under the existing retention rule.

```text
python -X utf8 scripts/review_image.py <topic-folder> 01-cover.png --kind cover --home
python -X utf8 scripts/review_image.py <topic-folder> 02-picture-practice.png --kind practice --home
python -X utf8 scripts/review_image.py <topic-folder> 03-qa-01-04.png --kind qa --home
```

Every new topic must declare `visual_family: home` or `general`. Home mode adds applicable Window references; `--home` cannot override a `general` manifest. Name-based fallback is reserved for explicitly documented legacy manifests. The tool verifies PNG decoding and 1086 × 1448 dimensions, copies applicable references into `review/references/`, and creates a 350 px per-image comparison JPG plus a JSON inspection record. Paths in records and HTML are relative to the topic folder. A comparison does not need the original computer's skill path to remain viewable.

## Inspect, correct, and record

1. Open the comparison JPG and the candidate PNG. Use the full PNG for lettering and fine details. Compare whole pages at equal 350 px widths; a contact sheet scaled to fit a narrow chat preview is not a phone-size legibility check. Use the gallery's fixed-width horizontal strip or open the PNGs individually at the same width.
2. Read the expected manifest content in the JSON record or gallery. Inspect all applicable criteria below. For Q&A, read **every character of all four fields of each assigned question**, not just the first row. For practice, trace every connector by group, verify cover continuity, and scan for all readable text and empty circles.
3. Read the concrete `visual_criteria` in the image's record, then write a findings JSON object keyed by all `required_visual_checks`. Home-series records include a separate `home_softness` criterion; cover scale, heading/picture relationships and study variety, and Q&A whole-page match and art integration, are checked separately. Every value must contain `status` (`pass` or `fail`) and a concrete `observation`. Include group-by-group line destinations or question-by-question text findings where relevant. File existence and a generic “looks good” are not observations. Record the inspection with the same command plus `--record <findings.json>`. The script records an explicit inspection; it cannot verify that the observer looked carefully and it never records user approval.
4. If any criterion fails, write the actual failure and concrete layout/art/text change into the next generation/composition brief, export a new PNG, and run the preparation command again. Earlier findings reset to `pending` when the PNG, manifest, references, generated comparison or criteria change. Attempting to record against stale inputs or outdated criteria is rejected. Inspect the new raster before supplying new findings. Remove rejected candidate copies under the retention rule; keep useful written failure findings in `prompt-notes.md`.
5. Only an image with correct dimensions, complete frozen content association, and observed passes for all its criteria may advance. If inspection remains incomplete or a tool cannot show the image, keep it pending and report that limitation. User approval is a separate decision when requested.

| Kind | Required observations |
| --- | --- |
| Cover | Subject identity and scale; shared hand-drawn texture; page rhythm without detached headings/icon columns; exact learning text; literal pictures; one correctly attached connector per group |
| Practice | Same topic artwork and order as cover; shared texture and rhythm; zero text/numbers/empty circles; complete picture cues; every connector reaches its own cluster |
| Q&A | Same subject; shared drawing style; whole-page header/rows/density; exact four fields for every assigned question; phone-readable English/Chinese; all answer details pictured |

## Complete-topic gallery

```text
python -X utf8 scripts/build_review_gallery.py <topic-folder> --home
```

This rebuilds per-image comparisons and review records for every saved topic image, a portable `review-gallery.html`, and `qa-review-comparison.jpg` containing all final Q&A pages. Every page in the HTML stays 350 px wide, including on a narrow screen; scroll horizontally. The gallery shows pending/pass/fail **recorded inspections** and links to the actual findings and frozen content. Generating it never creates a visual pass. Rebuild it after the last revision before delivery.

The builder also writes `review/gallery-binding.json`: current candidate list, manifest/reference/input/output hashes, local HTML links, per-image records and every aggregate Q&A comparison input. Rebuild after final findings and [generation evidence](generation-evidence.md) registration. Replacing a JPG, changing a page, adding/removing a final image, changing a linked record or breaking a link blocks release even if filenames and modification times look valid.

Before release, run `python -X utf8 scripts/check_release.py <topic-folder>` (default full) or explicitly select a requested subset with `--scope`. This checks output completeness as well as the inspection records. `check_visual_reviews.py` remains a record-only diagnostic; with `--candidate <relative-PNG> --kind <kind>` it checks one existing image's record, not whether all requested outputs exist. Both checks reject pending, failed, missing, stale or incomplete records and home-mode omissions. A passing record check verifies evidence completeness and freshness, not the honesty or accuracy of an observer's aesthetic judgment.

## Connector neatness is a separate required finding

For every cover and practice page, follow [branch-topology.md](branch-topology.md). A current renderer binding and successful final-raster replay are required before a passing review can be recorded. Compare actual curves with the approved Dog/Window page, record `connector_neatness` separately from count/endpoints, and reject irregular spacing, tangles, large loops, detached ends and intrusion into content. Program rejection limits cannot certify aesthetics or the truth of declared subject/text boxes; inspect those against the actual page. A later base, plan or record change invalidates the earlier inspection.
