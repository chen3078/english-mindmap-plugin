# Production decisions for a new topic

Read this before selecting a production method. This file is the single source for method selection and execution order. Format references define the visual target; they do not independently prescribe a different production method. Follow explicit user choices for scope, supplied facts, approved artwork and requested review points.

## What transfers to the next topic

Keep the Key/Cup ink, pencil/watercolor texture and paper; Cat/Dog whole-page rhythm; Carrot compact left-subject scale; and Dog Q&A page family. For home objects, also retain the approved Window softness and comfortable, cute object treatment. Keep each reference in its assigned role in [visual-system.md](visual-system.md).

Adapt the subject design, facts, branch count, study shapes, action scenes and page splits to the actual topic. Before generating art, describe one subject identity (silhouette, material, palette and recurring motifs) in `prompt-notes.md`; use the accepted current-topic art to keep that identity consistent across formats. Reference characters and decorations are not content for an unrelated topic.

## Execution order

1. Read the applicable references and open the actual reference PNGs. Declare the series explicitly in the manifest. Check that the available image tool can accept actual image references. Follow [generation-evidence.md](generation-evidence.md) to capture the actual prompt, input images and returned output, with tool/model identifiers when exposed. Merely naming a path in prompt text is not supplying an image. If reference input or the actual request/response evidence is unavailable, report the limitation and leave the evidence unverified.
2. Prepare and review the content manifest under [content-planning.md](content-planning.md). Consider the complete knowledge path, bind selected dimensions and process steps to real questions, explain omissions, and pass check_manifest.py before rendering. Manufactured objects need how-made coverage; materials/use/cleaning are separate. Present the actual bilingual questions for the existing content-review decision. Plan the complete Q&A page split before rendering. Write the subject and full-page visual plan.
3. Make a complete cover and compare it at 300–400 px width with the applicable approved covers. Follow [branch-topology.md](branch-topology.md) for new map connector layers. A specific image selected by the user remains their exact selection; that exception does not turn unchecked connectors into a pass.
4. For Q&A in scope, select one of the methods below and make one complete sample using the frozen real text. For video stills in scope, make one representative still. When the user requests only the cover, stop at the cover; do not make later-format samples.
5. Inspect the actual sample PNGs at full size and beside the applicable references at the same 300–400 px width. Record observed results and specific corrections. A failed comparison blocks batch production of that format. Change the failing design before trying again; do not resubmit the same failed composition as a new solution.
6. Derive practice artwork from the accepted cover. After the relevant samples pass, make remaining pages/stills with the same subject identity and accepted production method. Capture generation/composition evidence, parent edits and the inspected sample dependency for each artifact. After each saved or edited finished PNG, run the per-image workflow in [image-review.md](image-review.md) before advancing. Preserve user-requested sample approval. Rebuild the final gallery/binding after the last evidence and inspection changes before release.

## Q&A method selection

Use a previously accepted method for the current topic when one exists. Otherwise, prefer **complete-page generation** when the available image tool supports actual reference images and bilingual lettering: it is the successful approved Window approach. **Separate art plus exact-text typesetting** is the fallback when the complete-page sample has unresolved text defects, the tool cannot render bilingual text adequately, or the user requests editable text. The fallback must still match the approved full-page appearance; using the bundled HTML helper does not itself establish a match.

| Method | Required production step | Required sample result |
| --- | --- | --- |
| Complete-page generation | Supply the approved Dog Q&A whole page, applicable Window Q&A reference, current-topic subject reference, and exact four text fields for every assigned question. Generate a complete text-bearing page. | All English and Chinese fields visibly match the manifest; whole-page type, integrated art and density match the reference. |
| Separate art plus exact-text typesetting | Generate isolated per-question illustrations, then compose them with all four text fields into a complete page. Do not generate a full-page blank Q&A sheet. | Exact text and the same full-page visual standard; reject pasted art, thin/small type, rigid cards or unreadable Chinese. |

For either method, compare the complete sample with Dog and, for home objects, Window; add Rabbit for a three-row layout. Check header, English size/weight, Chinese readability, row spacing, illustration integration and page density. Verify every question, answer and translation against the manifest. Only then make later pages using the successful sample as an additional reference.

Record `qa_method`, the selection reason, sample filename, actual reference files, page ranges, text-check result and observed visual findings in `prompt-notes.md`. If a method changes before batch work, make and check a new complete sample. If it changes after a user-selected visual sample, present the new sample for that same visual decision before batch work. Do not imply that the old sample approves the new method.

## Meaning of a pass

Keep three statuses distinct: structural check passed; visual comparison passed; user approved. Record only statuses actually observed. An unchecked or failed page cannot be called complete because its files exist. If the tool, reference access, text accuracy or visual match remains unresolved, report the specific blocker and retain an unapproved status.

The goal is consistent accepted output after comparison and correction. A new topic has not been proven reproducible merely because this workflow was written; that requires a real new-topic trial in a copied skill folder.
