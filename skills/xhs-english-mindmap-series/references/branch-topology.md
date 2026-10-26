# Exact branch topology for cover and picture-only maps

This workflow checks missing lines and irregular geometry as well as the recurring extra-line error. Read the mandatory evidence and neatness gate below before rendering. It is required for new or repaired mind maps, independent of topic and group count. Do not treat an image-generation prompt such as “exactly eight lines” as proof that eight lines were drawn.

If the owner explicitly selects one **exact generated image** as the desired visual result, preserve that file unchanged as the selected artwork. Do not silently replace it with a connector-reworked derivative. Audit any connector concern separately; if a correction would change the selected picture, present that version as a separate candidate and keep the owner's exact selection until they choose otherwise. This does not make an unverified branch count a structural pass.

1. Freeze the manifest. Let `N = len(groups)`; the IDs must be ordered and unique. Mark each destination **circle on the cover** and each destination **picture cluster on the practice map**. The practice map does not retain the circles.
2. Prepare each 1086 × 1448 illustrated page **without any coral curved connector lines**. On the practice base, remove text **and all blank heading/number circles** while keeping every illustration and meaningful action arrow. Inspect the actual bases at full size. Reject a base if an old connector or practice circle remains, or if text/illustration changes materially. Retain only the active base while rendering it; delete rejected and superseded bases instead of accumulating them in `revisions/`.
3. Make one JSON branch plan for the cover and another for the picture-only image. Each plan has `branches` in manifest order. Every branch has exactly one `group_id` and four cubic Bezier `points: [[x,y], ...]` from the subject toward its destination. Declare plan `kind` (`cover` or `practice`), the actual `subject_box`, optional cover-only `title_box`, and one `content_box: [left, top, right, bottom]` per branch protecting its text/illustration area. Use `circle_center: [x,y]` for a cover branch; use `target_center: [x,y]` near the relevant picture cluster for a practice branch. For a practice page derived from a numbered cover, also list the former circle locations in `forbidden_circles` so the renderer can reject a base that still has dark rings. Use only `N` branch objects. Never add spare decorative curves to the plan.
4. Render with `python scripts/render_connectors.py manifest.json line-free.png branch-plan.json output.png`. This needs Pillow (`python -m pip install Pillow` if unavailable). The renderer rejects a plan whose count or ordered IDs differ from the manifest, duplicate destinations, out-of-bounds points, or lines whose endpoint is not near its declared destination. With `forbidden_circles`, it also rejects old dark circle outlines in the practice base. The resulting branch layer itself contains exactly `N` paths.
5. Visually audit the **rendered raster**, separately for cover and practice. Place the final cover beside the accepted Dog cover, and the final practice page beside the accepted Dog and Lion practice pages, all at the same phone width. Trace both ends and the full arc of every line: upper branches rise from near the main subject, middle branches leave its side, and lower branches continue naturally from its lower edge or title. Adapt to the topic's actual group positions; do not copy Dog's coordinates. Reject a line that begins far from the subject/title, cuts through an unrelated picture or another branch, or makes a large outer loop merely to reach the last group. On the cover, follow each numbered circle's one connector back to the subject. On the practice page, follow each line to its corresponding picture cluster. Record each group ID, destination, and pass/fail in `prompt-notes.md`. Verify there are **zero blank circles, English hints, numbers or other readable characters** and no line ending at a former circle location or dangling in blank paper. Count every visible connector again without relying on the plan. Scan around the subject/title and below the last group for leftover connectors. A drawing-plan pass or correct endpoint count alone is not final approval.
6. Only after both maps pass, replace final topic images, update any approved style reference derived from them, run the normal text/size checks, and build the portable archive. If any image fails, keep the old release clearly unapproved and do not promote that image as an “approved” reference.

## Mandatory evidence and neatness gate · 2026.10.26.3

No new cover or practice page can pass merely because an observer writes “connectors: pass”. `render_connectors.py` calls the shared geometry/raster validator and writes `production/connectors/<candidate>.json`. The record binds the manifest, actual line-free base, actual plan, renderer and final PNG. Save inputs inside the topic folder, distinct from the final path. Treat the base as internal artwork, not a finished practice page.

For an authoring schema example see [connector plan example](../assets/test-themes/connectors-plan-example.json). It is a synthetic nine-group engineering example, **not** approved layout coordinates for another topic. Locate actual subject edges, group circles/clusters, text and pictures for the current page before writing the plan. Include all of each group's text and art inside its `content_box`, with the destination circle just beside that area. A practice target is beside the picture cluster, with no text or empty circle. A cover may start lower arcs at its existing title; practice must start at the subject because the title is removed.

### Program checks

- Exactly one ordered curve per actual group; distinct destinations in top-to-bottom order.
- Starts close to a declared subject/title edge; ends close to the declared circle/cluster and its own protected content area.
- Consistent visible coral stroke (3–5.5 pixels); white/invisible or tiny strokes fail.
- No crossing or overlap; no crowding away from a short shared departure; no giant side loop, excessive detour or vertical backtracking.
- Curves route through whitespace, outside declared text/illustration boxes and outside the body of the main subject/title after departure.
- Every branch must add visible pixels to the base; redrawing on top of existing same-color lines or low contrast can fail.
- At inspection and release, replay the renderer from the bound files and compare the **actual final raster pixels**. Missing binding, changed inputs, missing/erased lines or later edits fail. Cover and practice use separate plans and records.

The numeric tolerances are engineering rejection limits, **not** measurements proving the approved templates' beauty. Declared boxes and destinations must match the actual image; software cannot infer all semantic image regions. Old connectors/stray lines hidden inside a declared art region, wrong region declarations and semantically wrong destinations still need visual inspection. A replay does not certify all content in the base.

The renderer is a local composition step. Register generated base artwork and the actual composition recipe/parent chain under [generation-evidence.md](generation-evidence.md); include the base and plan in recipe inputs. A connector record does not substitute for generation evidence. Finish all text/art edits before rendering the final layer; after any later edit, render and inspect again.

### Mandatory template comparison

Use approved Dog/Window covers for the organized fan and whole-page rhythm, Dog/Lion/Window practice pages for connected picture clusters, and Carrot only for subject scale. Existing references are sufficient; a user need not supply a new template for every topic. Do not copy Dog's exact coordinates or branch count.

The inspector must separately record **connector_neatness** after seeing the actual final raster and the applicable whole-page references at 350-pixel width, then inspect endpoints at full resolution:

1. Trace every group back to the main subject and identify its true destination.
2. Check smooth natural curves, consistent weight/color, ordered departures and balanced gaps.
3. Reject tangles, crossings, merged paths, oversized loops, detached starts, dangling ends, crowding, text/art intrusion or lines wandering across unrelated whitespace.
4. Inspect the subject/title boundary and below the last group for extra strokes; distinguish meaningful action arrows from branches.
5. A correct curve count or a geometry PASS never overrides visibly untidy whole-page composition. Record a failure and revise the plan, render and inspect again.

`review_image.py` refuses a passing review when actual connector checks fail. `check_visual_reviews.py` independently reruns these checks; publication uses that same gate. Review records also bind the connector record, base and plan, so changing the layout invalidates previous inspection. No blanket exemption is applied just because an image was generated in one call or selected as a visual candidate.

Do not mistake checks of manifest structure, file dimensions, or archive validity for checks of visible branch count. If the line-free image was generated from a text-bearing cover, compare every heading/label against the frozen manifest after line removal and after final rendering.
