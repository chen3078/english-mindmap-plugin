# One manifest, independent map groups and questions

New topics use the top-level fields `topic_en`, `topic_zh`, `category`, `audience`, `brand`, `visual_family`, `content_plan`, `groups`, and `qa_items`. `visual_family` is required: set it to `home` for a home-series topic (including any new object outside the original list), or `general` for a different family. It is not inferred from a new object's name, and `--home` cannot override a contradictory manifest. A missing/invalid family blocks content validation and production.

An existing approved manifest lacking this field can explicitly use `manifest_mode: legacy` plus a nonempty `legacy_manifest_reason`; only that compatibility mode permits historical name-based family fallback. Do not apply it to new topics or silently modify historical outputs. Historical heading exceptions are a separate policy below.

## Two ID spaces

- `groups` is the ordered map branch list. Each group has `id` (1…G), `heading_en`, `keywords_en`, `illustration`, and, where applicable, `dimension` (`location` or `needs`). Branch plans and cover/practice checks use these group IDs.
- `qa_items` is the ordered complete question list. Each item has `id` (1…Q), `group_id` (an existing map branch), `question_en`, `answer_en`, `question_zh`, `answer_zh`, and optionally a question-specific `illustration` and `source_urls`. Every group must link to at least one question. Q can differ from G.
- For a question containing only part of a group's facts, supply a question-specific illustration brief rather than blindly reusing the whole branch brief. Exact Q&A wording determines what its picture must show.
- Q&A filenames, page ranges, `qa-art/NN.png`, video filenames and English text use **question IDs**. A nine-branch/thirteen-question topic needs thirteen English Q&A pairs and thirteen video stills; page ranges must cover questions 1–13, not branches 1–9.

`manifest_model.questions()` is the common reader for every question-based tool. If `qa_items` exists, it is authoritative, even when older `group.qa` values remain. An empty/invalid `qa_items` is an error, never a reason to fall back silently. For historical one-question-per-group files without `qa_items`, the reader derives IDs from `group.qa` without rewriting the approved content. Do not create two separately maintained question lists in a new topic.

The bundled `assets/test-themes/cup-multi-qa.json` demonstrates 9 groups and 13 questions. Its content is an example, not a fixed questionnaire for other objects.

## Machine-checkable heading rules

New topics default to `heading_policy: current` (or omit that field):

- First `heading_en` is exactly `What`.
- Set `dimension: location` for a place/location branch; its heading is exactly `Where`. Familiar longer variants such as `Where Dogs Live`, `Habitat` and `Location` are also rejected.
- For a plant's sunlight/water/soil requirements branch, set `dimension: needs`; its heading is exactly `Needs`. Recognized expanded variants such as `What helps it grow` are rejected.
- Map headings are section labels, not full questions. Keep full natural questions in `qa_items`.

The checker validates explicit dimensions and recognized heading patterns. Semantic review must still identify which dimension the facts actually describe; a script cannot classify every possible paraphrase.

For an **existing approved topic only**, an explicit `heading_policy: legacy` plus nonempty `legacy_heading_reason` permits historical heading wording. This preserves historical images; do not apply that exception to new topics to suppress an error. No checker silently edits existing content.

Run `python -X utf8 scripts/check_manifest.py <manifest.json>`. It reports both the branch count and question count. Correct content errors before exporting, paging, producing video stills or preparing inspections.

## Content completeness before rendering

Every new topic requires `content_plan` under [content-planning.md](content-planning.md): version, category profile, full/focused scope, and all nine considered dimensions with statuses. Included dimensions bind actual question IDs; omitted/not-applicable dimensions explain the topic-specific reason. Included processes bind at least two ordered excerpts from the English answers. Full manufactured-object topics need material/part coverage and a separate how-made question. Full food topics need a source or process path, with manual review of process omissions. The full mirror fixture and other category examples are linked in the planning guide. Existing explicit legacy manifests without a plan remain readable but report that they have not met the new content standard. Do not silently change past approved content.
