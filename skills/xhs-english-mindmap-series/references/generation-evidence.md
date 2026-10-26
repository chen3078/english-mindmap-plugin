# Capture image-generation evidence without inventing it

Use this for every new or edited finished image before release. The executing assistant maintains these files; the user does not need to fill them manually. Read [manifest-schema.md](manifest-schema.md) and declare the series before any image call.

## What the tools can verify

There are three separate facts: a record exists; its prompt/input/output files match the current image; a remote provider actually executed that request. This skill verifies the first two. It does **not** authenticate provider execution, assess whether an observer told the truth, or certify aesthetics. The stored field `execution_authenticity` is always `not_independently_verified`. Never change it to “verified” to make a release pass.

An absent event, missing references, mismatched output or incomplete chain is **unverified** and blocks release. A valid record becomes `linked_record`; that means local evidence linkage passed, with remote execution independently unverified. Actual visual inspection is still required.

## Immediately after a real image call

1. Preserve the actual full prompt and actual request/reference inputs from the call you made. Copy reference bytes to `production/inputs/` and use topic-relative snapshot paths in the normalized record. Keep original request path/identifier details in the raw export when available. A filename mentioned in prompt prose is not a reference-image input.
2. Preserve the returned image's bytes and tool response. Record the actual tool name, model when exposed (otherwise `null`), call identifier when exposed, success/failure and completion time. If the tool does not expose a provider timestamp, record the local observed completion time with `time_source: local_observation`; never present it as a provider timestamp.
3. Save a normalized event JSON under `production/events/`. Use `record_source: observed_tool_call` for parameters/results directly observed by the executing assistant, or `provider_export` only with the actual exported record. Provider exports additionally require `raw_event_file` and `raw_event_sha256`; raw exports are retained as evidence, not authenticated by this checker. Omit credentials from saved records.
4. If the request/response is unavailable, record that limitation in `prompt-notes.md` and leave the image's generation evidence unverified. Do not reconstruct an assumed prompt or invented call ID for an old image.

The following is a **schema example**, not evidence. Replace every bracketed value with actual observed data; placeholder values cannot pass validation:

```json
{
  "record_source": "observed_tool_call",
  "tool": "<actual tool name>",
  "model": null,
  "call_id": null,
  "request": {
    "prompt": "<the full actual prompt>",
    "reference_images": [
      {"path": "production/inputs/reference.png", "sha256": "<actual SHA-256>", "role": "layout"}
    ]
  },
  "response": {
    "status": "succeeded",
    "completed_at": "<actual timezone-aware ISO timestamp>",
    "time_source": "local_observation",
    "outputs": [{"sha256": "<actual returned image SHA-256>"}]
  }
}
```

Reference roles are `style`, `layout`, `subject`, `scale` and `home`. Keep their assigned roles from the visual system. Every required duty in [reference-roles.md](reference-roles.md) must be covered by actual approved inputs or valid inspected current-topic inheritance. A single size-only image never establishes drawing style or page layout. Primary role labels must match the scoped catalog; labels alone grant no duties. Q&A complete-page prompts must actually include all four text fields for every assigned question. A blank Q&A sheet is not an acceptable tool output to request.

## Register direct generated images

Save a spec JSON describing the actual method, then register it:

```json
{
  "mode": "generated",
  "method": "whole_page",
  "event_file": "production/events/qa-sample.json",
  "sample": "self"
}
```

```text
python -X utf8 scripts/generation_evidence.py <topic-folder> 03-qa-01-04.png --kind qa --spec <spec.json>
```

Kinds are `cover`, `practice`, `qa`, `video`, and internal `art`. `sample` applies to Q&A/video only. For cover/practice/art omit it. Methods describe what was actually used, such as `whole_page`, `independent_scene` or `isolated_art`.

The registered record lives in `production/records/`. It binds the event, full prompt, reference bytes, frozen manifest and returned-image hash. Copying identical returned bytes into a final filename is allowed. Resizing, changing text or drawing connector lines changes the bytes and needs a composition step rather than claiming the modified PNG was the direct tool output.

## Register composition and editing

For local exact-text typesetting, controlled connectors, resizing or another local edit:

- Register the actual generated parent artwork first (`--kind art` when internal).
- Save a recipe JSON naming the operation, completion time, `input_files` (each with relative `path` and `sha256`), and `output_sha256`. Bind actual HTML/CSS, branch plan, fonts or other files that determined the raster. Record renderer settings/commands in the recipe as applicable.
- `layout_references` may list the actual whole-page reference files consulted for composition, each with `path` and `sha256`. These are composition references, not a claim that they were uploaded to an image-generation service. Use them when isolated-art parents carry drawing style but the Q&A layout comes from Dog/Window.
- Register a spec with `mode: composed`, actual `method`, `recipe_file`, and `parents` (topic-relative artifact paths). Parent generation/composition records are checked recursively, including cycle rejection. Do not fabricate parent traces for historical art whose generation record was not retained.

```json
{
  "mode": "composed",
  "method": "exact_text_typesetting",
  "recipe_file": "production/recipes/qa-page-2.json",
  "parents": ["production/art/05.png", "production/art/06.png", "production/art/07.png"],
  "sample": "03-qa-01-04.png"
}
```

Keep only current/accepted artwork required by the active chain. Follow the owner's retention rule for rejected/superseded image bytes and cache copies; do not accumulate failed images as evidence. Written failure observations may remain in prompt notes.

## Sample-first evidence and later pages

1. Register exactly one representative Q&A sample and one representative video sample for formats in scope with `sample: self`. Make no claim that registration itself approves the sample.
2. Prepare its comparison, actually inspect the complete raster and record the findings under [image-review.md](image-review.md).
3. Actually supply the inspected sample as an image reference (or a bound composition input); metadata alone is insufficient. For later Q&A pages/video stills, set `sample` to that sample's relative path and keep the same actual `method`. The later image's observed completion time must follow the recorded sample review. A sample file, inspection record or evidence change invalidates dependent records.
4. Multiple self-labelled samples cannot substitute for the approved sample-first process. A method change needs a new representative sample and its inspection; preserve any user-requested visual approval step.

Timestamp and record checks test **internal consistency**, not independently proven historical execution order. Do not claim stronger verification than the available event source supports.

## Review, bind the gallery, then release

After capture/registration, prepare the per-image comparison and complete its actual visual inspection. After the final findings, rebuild:

```text
python -X utf8 scripts/build_review_gallery.py <topic-folder>
python -X utf8 scripts/check_release.py <topic-folder>
```

Use the explicit `--scope` for a requested subset. The gallery links to current evidence records and writes `review/gallery-binding.json`, which binds current images, references, per-image comparisons, inspection/evidence records, HTML links and the aggregate Q&A comparison. Any change requires rebuilding and, where relevant, reinspection. Release checks reject broken/escaping links, replaced comparisons, omitted current pages, missing series, stale evidence, changed parent art and missing sample links.

Do not fill synthetic or generic passing observations to get a release through. Regression tests use isolated synthetic fixtures to test program behavior only; they are never examples of actual visual approval.

## Cover/practice connector evidence

Before inspecting a newly made cover or practice map, render the actual final connector layer under [branch-topology.md](branch-topology.md). The renderer saves a mandatory binding under production/connectors; visual and release checks replay the bound base/plan against final pixels. Geometry, visible strokes and required whole-page neatness observations are separate checks. Register this local rendering as a composed operation with its actual base/plan inputs and verified parent artwork. Connector receipts alone do not authenticate generation or approve neatness.
