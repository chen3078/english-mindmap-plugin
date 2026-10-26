# Single-question video stills

Use this only when a request includes video images or English-only Q&A text. For video framing, the approved references are `../assets/approved-dog/video-single-subject.png` and `video-multiple-actions.png`. Use the Key/Cup images and the current topic's accepted cover to guide illustration style and subject continuity. The selected Cat cover applies to covers; Cat video stills are not approved references.

## Content and format

- Generate exactly one still for each ordered question in `qa_items` (legacy `group.qa` is a compatibility fallback). Save as `video/01.png`, `video/02.png`, etc. The count follows question IDs, not map branches: 9 branches and 13 questions require 13 stills. Do not merge or skip questions, and do not add a generic title image unless requested.
- Use the English answer to decide which details must be visible. A single-subject question may need one large scene; a multi-part answer may use a few separated vignettes. Do not force the same composition on every question.
- Match the accepted Dog stills' scale, paper, dark hand-drawn outlines, colored-pencil/watercolor fill, and generous whitespace. For another topic, copy the visual grammar, not the Dog subject.
- Compose and generate or edit **each numbered still separately** from that question and answer. A crop of the full mind map, an enlarged mini-icon, a narrow picture strip on a large blank card, a visible rectangular patch, or a leftover branch fragment is a failed still. Regenerate that scene at a proper 3:4 scale.
- 1086 × 1448 portrait (3:4). Put all meaningful art in approximately the top 72%; keep the entire bottom 25% as uninterrupted, low-contrast warm off-white paper. This space is for subtitles added later in the video editor, not a printed blank card or text box.
- No readable text anywhere in the picture: no title, Q&A, labels, numerals, signs, brand signature, watermark, or subtitles. The separate English-only text file supplies the exact words.
- Use arrows only for actual action or progression. Keep each scene legible at phone width; do not crowd a long answer into tiny icons.
- For a question that names several physical parts, show the whole subject plus a separate, enlarged visual study of **each named part**, as in the owner's rabbit body-parts reference. Do not rely on a single whole-object drawing or one generic cutaway to imply all parts. Keep every local study distinct and readable while preserving the bottom subtitle zone. Apply the same one-part-one-visual check to the cover branch and related Q&A illustration.

## Prompt pattern

Use a fresh prompt for each group, including its exact question and answer for semantic grounding. Supply the approved Dog still matching the composition type, the Key/Cup style references, and the accepted cover of the current topic when the image tool supports references. Mark all references as style or subject-continuity examples, not content to copy. State the required scene details, the common 3:4 dimensions and subtitle-safe zone, and the no-text constraint. Save actual prompt and reference filenames beside the output for later reproducibility.

## Verification

1. Compare each image against that question's English answer and its linked group's mind-map/QA illustrations. Every main answer detail must have a visual cue where possible; numerical facts may remain in the later subtitle rather than being represented as fake clocks or labels.
2. Inspect the whole composition beside the approved Dog stills at phone size. The scene must occupy a useful share of the upper page, show no visible crop boundary or irrelevant fragment, and keep the bottom quarter blank. No feet, arrows, scenery, or high-contrast marks should overlap the subtitle-safe zone.
3. Run `scripts/check_video_outputs.py` for file count, order, dimensions, and exact English text. This does not replace visual inspection.

A copied skill still needs image-generation access on the destination computer; model output can vary. The subtitle-safe zone is specified above and does not need a bundled example image.
