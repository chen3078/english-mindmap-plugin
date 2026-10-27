#!/usr/bin/env python3
"""Functional regressions for IDs, headings and release scope. No visual approval.

Synthetic files and mocked visual inspections are temporary test fixtures only.
"""
import copy
import json
import shutil
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import build_qa_pages
import check_release
from check_manifest import check
from manifest_model import load, questions
from review_image import expected_content

SKILL = Path(__file__).resolve().parents[1]

class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="xhs-functional-test-")
        self.folder = Path(self.tmp.name)
        self.data = load(SKILL / "assets/test-themes/cup-multi-qa.json")
        self.write_manifest()

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self):
        path = self.folder / "manifest.json"
        path.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_new_topics_require_explicit_content_plan(self):
        self.data.pop("content_plan")
        self.assertTrue(any("content_plan is required" in e for e in check(self.write_manifest())[0]))
        self.data.update(manifest_mode="legacy", legacy_manifest_reason="Retain an existing approved topic without inventing a historical content plan")
        errors, warnings, _ = check(self.write_manifest())
        self.assertFalse(errors)
        self.assertTrue(any("not validated under the new content standard" in w for w in warnings))

    def test_mirror_manufacturing_cannot_be_omitted(self):
        self.data = load(SKILL / "assets/test-themes/mirror-content.json")
        self.assertFalse(check(self.write_manifest())[0])
        self.data["groups"].pop(); self.data["qa_items"].pop()
        self.data["content_plan"]["dimensions"]["process"] = {"status": "omitted", "reason": "Seven groups already fit the page"}
        self.assertTrue(any("require how it is made" in e for e in check(self.write_manifest())[0]))
        self.data["content_plan"]["profile"] = "other"
        self.assertTrue(any("disagrees with category" in e for e in check(self.write_manifest())[0]))

    def test_materials_and_cleaning_are_not_manufacturing(self):
        self.data = load(SKILL / "assets/test-themes/mirror-content.json")
        self.data["qa_items"][7]["question_en"] = "What is a mirror made of?"
        self.assertTrue(any("material/ingredient" in e for e in check(self.write_manifest())[0]))
        self.data = load(SKILL / "assets/test-themes/mirror-content.json")
        entry = self.data["content_plan"]["dimensions"]["process"]
        entry.update(kind="operation", question_ids=[7], steps=["wipe it", "with a soft cloth"])
        self.assertTrue(any("manufacturing" in e for e in check(self.write_manifest())[0]))
        entry["kind"] = "manufacturing"
        self.assertTrue(any("how-made question" in e for e in check(self.write_manifest())[0]))

    def test_process_steps_bind_actual_answer_in_order(self):
        self.data["content_plan"]["dimensions"]["process"]["steps"] = ["invented packaging step", "heat the glass"]
        self.assertTrue(any("absent or out of order" in e for e in check(self.write_manifest())[0]))
        self.data = load(SKILL / "assets/test-themes/cup-multi-qa.json")
        self.data["content_plan"]["dimensions"]["process"]["steps"].reverse()
        self.assertTrue(any("absent or out of order" in e for e in check(self.write_manifest())[0]))

    def test_dimensions_reasons_and_question_links(self):
        self.data["content_plan"]["dimensions"]["origin"].pop("reason")
        self.assertTrue(any("topic-specific reason" in e for e in check(self.write_manifest())[0]))
        self.data = load(SKILL / "assets/test-themes/cup-multi-qa.json")
        self.data["content_plan"]["dimensions"]["use"]["question_ids"] = [99]
        self.assertTrue(check(self.write_manifest())[0])
        self.data["content_plan"]["dimensions"].pop("extension")
        self.assertTrue(check(self.write_manifest())[0])

    def test_user_focused_scope_is_explicit(self):
        self.data = load(SKILL / "assets/test-themes/mirror-content.json")
        self.data["groups"].pop(); self.data["qa_items"].pop()
        plan = self.data["content_plan"]; plan["scope"] = "focused"
        plan["dimensions"]["process"] = {"status": "omitted", "reason": "The user limited this lesson to recognizing and using mirrors"}
        self.assertTrue(check(self.write_manifest())[0])
        plan["user_scope_instruction"] = "Only cover what a mirror looks like and how I use and clean it; omit factory production."
        self.assertFalse(check(self.write_manifest())[0])

    def test_category_paths_are_not_identical_questionnaires(self):
        for name in ["dog.json", "bus.json", "milk-content.json", "tomato-content.json", "mirror-content.json"]:
            self.data = load(SKILL / "assets/test-themes" / name)
            self.assertFalse(check(self.write_manifest())[0], name)
        self.data = load(SKILL / "assets/test-themes/cup-multi-qa.json")
        self.data["qa_items"][11]["question_en"] = "How is a cup made from glass?"
        self.assertFalse(check(self.write_manifest())[0])
        self.data = load(SKILL / "assets/test-themes/milk-content.json")
        self.data["content_plan"]["dimensions"]["process"].update(kind="manufacturing")
        self.assertTrue(check(self.write_manifest())[0])


    def test_bad_ids_empty_and_dangling_qa(self):
        for mutate in (lambda d: d.update(qa_items=[]),
                       lambda d: d["qa_items"][0].update(id=2),
                       lambda d: d["qa_items"][0].update(group_id=99),
                       lambda d: d["qa_items"][0].pop("answer_zh"),
                       lambda d: d.update(qa_items=[q for q in d["qa_items"] if q["group_id"] != 9])):
            self.data = load(SKILL / "assets/test-themes/cup-multi-qa.json")
            mutate(self.data)
            self.assertTrue(check(self.write_manifest())[0])

    def test_legacy_one_question_per_group(self):
        self.data = load(SKILL / "assets/test-themes/dog.json")
        self.assertFalse(check(self.write_manifest())[0])
        self.assertEqual(len(questions(self.data)), len(self.data["groups"]))

    def test_layout_cli_renders_thirteen_questions(self):
        art = self.folder / "qa-art"
        art.mkdir()
        for i in range(1, 14):
            Image.new("RGB", (16, 16), "white").save(art / f"{i:02d}.png")
        args = ["build_qa_pages.py", str(self.folder), "--page-sizes", "4,3,3,3"]
        with patch.object(sys, "argv", args):
            self.assertEqual(build_qa_pages.main(), 0)
        pages = sorted(self.folder.glob("*-qa-*.html"))
        self.assertEqual(len(pages), 4)
        self.assertIn("11-13", pages[-1].name)
        self.assertIn("qa-art/13.png", pages[-1].read_text(encoding="utf-8"))

    def test_heading_rules_and_explicit_historical_exception(self):
        for heading in ("What it is", "Wrong First Heading", "What is it?"):
            self.data["groups"][0]["heading_en"] = heading
            self.assertTrue(check(self.write_manifest())[0])
        self.data["heading_policy"] = "legacy"
        self.assertTrue(check(self.write_manifest())[0])
        self.data["legacy_heading_reason"] = "Existing approved artwork retained for compatibility test"
        self.assertFalse(check(self.write_manifest())[0])

    def test_location_and_plant_needs(self):
        self.data["groups"][1].update(heading_en="Where Dogs Live", dimension="location")
        self.assertTrue(check(self.write_manifest())[0])
        self.data["groups"][1]["heading_en"] = "Where"
        self.assertFalse(check(self.write_manifest())[0])
        self.data = load(SKILL / "assets/test-themes/tomato-content.json")
        self.data["groups"][5].update(heading_en="What helps it grow", dimension="needs")
        self.assertTrue(check(self.write_manifest())[0])
        self.data["groups"][5]["heading_en"] = "Needs"
        self.assertFalse(check(self.write_manifest())[0])

    def make_outputs(self):
        for name in ("01-cover.png", "02-picture-practice.png", "03-qa-01-04.png", "04-qa-05-07.png", "05-qa-08-10.png", "06-qa-11-13.png"):
            Image.new("RGB", (1086, 1448), "white").save(self.folder / name)
        Image.new("RGB", (350, 467), "white").save(self.folder / "qa-review-comparison.jpg")
        for name in ("prompt-notes.md", "review-gallery.html"):
            (self.folder / name).write_text("Synthetic structural test fixture only", encoding="utf-8")

    @patch("check_release.check_samples", return_value=[])
    @patch("check_release.check_generation", return_value=[])
    @patch("check_release.check_binding", return_value=[])
    @patch("check_release.check_image", return_value=[])
    def test_full_missing_each_required_output(self, *mocks):
        self.make_outputs()
        self.assertFalse(check_release.check(self.folder)[0])
        for name in ("01-cover.png", "02-picture-practice.png", "prompt-notes.md", "review-gallery.html", "06-qa-11-13.png"):
            path = self.folder / name
            temporary = path.with_suffix(path.suffix + ".hold")
            path.rename(temporary)
            self.assertTrue(check_release.check(self.folder)[0], name)
            temporary.rename(path)



    def test_missing_visual_records_still_block(self):
        self.make_outputs()
        self.assertTrue(any("inspection" in e for e in check_release.check(self.folder, "cover")[0]))

    def test_new_series_required_and_explicit_legacy(self):
        self.data["topic_en"] = "Bookshelf"
        self.data.pop("visual_family")
        self.assertTrue(any("visual_family" in e for e in check(self.write_manifest())[0]))
        self.data["manifest_mode"] = "legacy"
        self.assertTrue(check(self.write_manifest())[0])
        self.data["legacy_manifest_reason"] = "Existing approved topic retained for compatibility test"
        self.assertFalse(check(self.write_manifest())[0])
        self.data["manifest_mode"] = "current"
        self.data["visual_family"] = "home"
        self.assertFalse(check(self.write_manifest())[0])

    def test_gallery_binding_changes_and_portability(self):
        import build_review_gallery
        from gallery_binding import check_binding
        for name in ["01-cover.png", "03-qa-01-04.png"]:
            Image.new("RGB", (1086, 1448), "white").save(self.folder / name)
        with patch.object(sys, "argv", ["build_review_gallery.py", str(self.folder)]):
            self.assertEqual(build_review_gallery.main(), 1)
        requested = [(self.folder / "01-cover.png", "cover"), (self.folder / "03-qa-01-04.png", "qa")]
        self.assertFalse(check_binding(self.folder, requested, True))
        for name in ["qa-review-comparison.jpg", "review-gallery.html", "03-qa-01-04.png"]:
            path = self.folder / name; original = path.read_bytes()
            if name.endswith(".jpg"): Image.new("RGB", (350, 467), "white").save(path)
            elif name.endswith(".html"): path.write_text('<img src="missing.png">', encoding="utf-8")
            else: Image.new("RGB", (1086, 1448), "blue").save(path)
            self.assertTrue(check_binding(self.folder, requested, True), name)
            path.write_bytes(original)
        moved = self.folder / "moved-topic"
        moved.mkdir()
        for path in list(self.folder.iterdir()):
            if path != moved: shutil.move(str(path), moved / path.name)
        self.assertFalse(check_binding(moved, [(moved / p.name, kind) for p, kind in requested], True))

    def connector_plan_fixture(self, kind="cover"):
        plan = {"kind": kind, "subject_box": [40,475,290,900], "width":4.3, "branches":[]}
        if kind=="cover": plan["title_box"]=[40,920,290,995]
        upper=0; lower=0
        for i,g in enumerate(self.data["groups"]):
            y=80+i*145
            if y<475:
                start=[100+upper*70,475]; upper+=1
                pts=[start,[start[0],y],[330,y],[385,y]]
            elif y<=900:
                start=[290,y];pts=[start,[320,y],[350,y],[385,y]]
            elif kind=="cover" and y<=995:
                start=[290,max(920,y)];pts=[start,[320,y],[350,y],[385,y]]
            else:
                start=[200-lower*70,995 if kind=="cover" else 900];lower+=1
                pts=[start,[start[0],y],[330,y],[385,y]]
            b={"group_id":g["id"],"points":pts,"content_box":[440,y-30,1055,min(1447,y+80)]}
            b["circle_center" if kind=="cover" else "target_center"]=[410,y]
            plan["branches"].append(b)
        return plan

    def connect_fixture(self, image, kind="cover"):
        from connector_checks import render, write_record
        base=self.folder/(image.stem+"-base.png")
        shutil.copy2(image,base)
        pf=self.write_json(image.stem+"-plan.json",self.connector_plan_fixture(kind))
        with Image.open(base) as im: output=render(self.data,im,load(pf))
        output.save(image)
        write_record(self.folder,image,base,pf)

    def event(self, image, reference=None, prompt="Actual prompt fixture", completed=None):
        from datetime import datetime, timezone
        from generation_evidence import digest
        reference = reference or SKILL / "assets/key-cup-style/cup-reference.png"
        inputs = self.folder / "production/inputs"; inputs.mkdir(parents=True, exist_ok=True)
        ref = inputs / reference.name
        if reference.resolve() != ref.resolve(): shutil.copy2(reference, ref)
        return {"record_source": "observed_tool_call", "tool": "synthetic-test-tool", "model": None,
                "request": {"prompt": prompt, "reference_images": [{"path": ref.relative_to(self.folder).as_posix(), "sha256": digest(ref), "role": "style"}]},
                "response": {"status": "succeeded", "completed_at": completed or datetime.now(timezone.utc).isoformat(),
                             "outputs": [{"sha256": digest(image)}]}}

    def full_event(self, image, kind, prompt="Actual complete prompt fixture"):
        refs = ["key-cup-style/cup-reference.png"]
        if kind == "cover": refs += ["approved-dog/cover.png", "approved-carrot/cover-size-reference.png", "approved-window/cover.png"]
        elif kind == "qa": refs += ["approved-dog/qa-01-04.png", "approved-window/qa-01-04.png"]
        elif kind == "practice": refs += ["approved-dog/picture-practice.png"]
        event = self.event(image, prompt=prompt)
        event["request"]["reference_images"] = []
        for i, name in enumerate(refs):
            # Preserve distinct reference snapshots even when source basenames match.
            source = SKILL / "assets" / name
            target = self.folder / "production/inputs" / (name.replace("/", "--"))
            shutil.copy2(source, target)
            from generation_evidence import digest
            event["request"]["reference_images"].append({"path": target.relative_to(self.folder).as_posix(), "sha256": digest(target), "role": "scale" if "carrot" in name else "style" if "key-cup-style" in name else "layout"})
        if kind in ("qa", "practice"):
            cover = self.accepted_cover()
            event["request"]["reference_images"].append({"path": cover.name, "sha256": digest(cover), "role": "subject"})
            from datetime import datetime, timezone
            event["response"]["completed_at"] = datetime.now(timezone.utc).isoformat()
        return event

    def accepted_cover(self):
        import generation_evidence as ge
        cover = self.folder / "01-cover.png"
        if not ge.record_path(self.folder, cover).exists():
            Image.new("RGB", (1086, 1448), "lightyellow").save(cover)
            self.connect_fixture(cover)
            self.write_json("production/accepted-cover.json", self.full_event(cover, "cover"))
            ge.register(self.folder, cover, "cover", {"mode": "generated", "method": "whole_page", "event_file": "production/accepted-cover.json"})
            self.inspect_fixture(cover, "cover")
        return cover

    def inspect_fixture(self, image, kind):
        import review_image as review
        data, receipt = review.prepare(self.folder, image, kind)
        findings = {key: {"status": "pass", "observation": "Synthetic inspection fixture only, never real visual approval."} for key in data["required_visual_checks"]}
        review.record_findings(self.folder, receipt, self.write_json("synthetic-findings.json", findings))
        return receipt

    def write_json(self, name, data):
        path = self.folder / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def test_generated_evidence_missing_prompt_refs_and_changed_output(self):
        import generation_evidence as ge
        image = self.folder / "01-cover.png"; Image.new("RGB", (1086, 1448), "white").save(image)
        self.assertTrue(ge.check(self.folder, image, "cover"))
        event = self.full_event(image, "cover"); self.write_json("production/call.json", event)
        spec = {"mode": "generated", "method": "whole_page", "event_file": "production/call.json"}
        ge.register(self.folder, image, "cover", spec)
        self.assertFalse(ge.check(self.folder, image, "cover"))
        for section, key, value in [("request", "prompt", ""), ("request", "reference_images", []), ("response", "outputs", [])]:
            changed = copy.deepcopy(event); changed[section][key] = value
            self.write_json("production/call.json", changed)
            self.assertTrue(ge.check(self.folder, image, "cover"))
        self.write_json("production/call.json", event)
        Image.new("RGB", (1086, 1448), "blue").save(image)
        self.assertTrue(ge.check(self.folder, image, "cover"))

    def test_composed_evidence_binds_recipe_and_parent(self):
        import generation_evidence as ge
        parent = self.folder / "art.png"; Image.new("RGB", (1086, 1448), "white").save(parent)
        self.write_json("production/art-call.json", self.event(parent))
        ge.register(self.folder, parent, "art", {"mode": "generated", "method": "isolated_art", "event_file": "production/art-call.json"})
        image = self.folder / "01-cover.png"; shutil.copy2(parent, image)
        recipe = {"operation": "synthetic composition fixture", "completed_at": "2026-10-25T12:00:00+00:00",
                  "input_files": [{"path": "art.png", "sha256": ge.digest(parent)}], "output_sha256": ge.digest(image)}
        full_refs = self.full_event(image, "cover")["request"]["reference_images"]
        recipe["layout_references"] = full_refs
        self.write_json("production/recipe.json", recipe)
        spec = {"mode": "composed", "method": "controlled_connectors", "recipe_file": "production/recipe.json", "parents": ["art.png"]}
        ge.register(self.folder, image, "cover", spec)
        self.assertFalse(ge.check(self.folder, image, "cover"))
        recipe["operation"] = "changed recipe"; self.write_json("production/recipe.json", recipe)
        self.assertTrue(ge.check(self.folder, image, "cover"))

    def test_qa_evidence_rejects_blank_prompt_and_multiple_samples(self):
        import generation_evidence as ge
        from manifest_model import QA_FIELDS
        image = self.folder / "03-qa-01-04.png"; Image.new("RGB", (1086, 1448), "white").save(image)
        event = self.full_event(image, "qa")
        self.write_json("production/qa-call.json", event)
        spec = {"mode": "generated", "method": "whole_page", "event_file": "production/qa-call.json", "sample": "self"}
        with self.assertRaises(ValueError): ge.register(self.folder, image, "qa", spec)
        event["request"]["prompt"] = "\n".join(q[f] for q in questions(self.data)[:4] for f in QA_FIELDS)
        self.write_json("production/qa-call.json", event); ge.register(self.folder, image, "qa", spec)
        self.assertFalse(ge.check(self.folder, image, "qa"))
        later = self.folder / "04-qa-05-07.png"; shutil.copy2(image, later)
        event["request"]["prompt"] = "\n".join(q[f] for q in questions(self.data)[4:7] for f in QA_FIELDS)
        self.write_json("production/qa-call-2.json", event)
        ge.register(self.folder, later, "qa", {**spec, "event_file": "production/qa-call-2.json"})
        self.assertTrue(ge.check_samples(self.folder, [(image, "qa"), (later, "qa")]))

    def test_sample_binding_time_method_and_changed_review(self):
        import generation_evidence as ge
        import review_image as review
        from manifest_model import QA_FIELDS
        first = self.folder / "03-qa-01-04.png"
        second = self.folder / "04-qa-05-07.png"
        for path, color in [(first, "white"), (second, "lightblue")]: Image.new("RGB", (1086, 1448), color).save(path)
        event = self.full_event(first, "qa")
        event["request"]["prompt"] = "\n".join(q[f] for q in questions(self.data)[:4] for f in QA_FIELDS)
        self.write_json("production/sample-call.json", event)
        spec = {"mode": "generated", "method": "whole_page", "event_file": "production/sample-call.json", "sample": "self"}
        ge.register(self.folder, first, "qa", spec)
        r, receipt = review.prepare(self.folder, first, "qa")
        findings = {key: {"status": "pass", "observation": "Synthetic inspection fixture, not actual visual approval."} for key in r["required_visual_checks"]}
        fp = self.write_json("synthetic-findings.json", findings)
        review.record_findings(self.folder, receipt, fp)
        event = self.event(second, first)
        event["request"]["prompt"] = "\n".join(q[f] for q in questions(self.data)[4:7] for f in QA_FIELDS)
        self.write_json("production/later-call.json", event)
        later = {"mode": "generated", "method": "whole_page", "event_file": "production/later-call.json", "sample": first.name}
        ge.register(self.folder, second, "qa", later)
        self.assertFalse(ge.check(self.folder, second, "qa"))
        self.assertFalse(ge.check_samples(self.folder, [(first, "qa"), (second, "qa")]))
        data, _ = review.prepare(self.folder, second, "qa")
        self.assertIn(first.name, data["sources_sha256"])
        coverage = load(ge.record_path(self.folder, second))["reference_coverage"]
        self.assertEqual(coverage["origins"]["qa_layout"][0]["type"], "current_topic_sample")
        missing_sample = self.full_event(second, "qa")
        missing_sample["request"]["prompt"] = event["request"]["prompt"]
        self.write_json("production/later-call.json", missing_sample)
        with self.assertRaisesRegex(ValueError, "actually use the inspected sample"):
            ge.register(self.folder, second, "qa", later)
        self.write_json("production/later-call.json", event)
        earlier = copy.deepcopy(event); earlier["response"]["completed_at"] = "2000-01-01T00:00:00+00:00"
        self.write_json("production/later-call.json", earlier)
        with self.assertRaises(ValueError): ge.register(self.folder, second, "qa", later)
        self.write_json("production/later-call.json", event)
        with self.assertRaises(ValueError): ge.register(self.folder, second, "qa", {**later, "method": "changed_method"})
        data = json.loads(receipt.read_text(encoding="utf-8")); data["findings"]["page_rhythm"]["observation"] = "Changed inspection fixture"
        receipt.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.assertTrue(ge.check(self.folder, second, "qa"))

    def test_reference_roles_reject_scale_only_and_fake_role(self):
        import generation_evidence as ge
        image = self.folder / "01-cover.png"; Image.new("RGB", (1086, 1448), "white").save(image)
        spec = {"mode": "generated", "method": "whole_page", "event_file": "production/call.json"}
        event = self.event(image, SKILL / "assets/approved-carrot/cover-size-reference.png")
        self.write_json("production/call.json", event)
        with self.assertRaisesRegex(ValueError, "primary role mismatch"):
            ge.register(self.folder, image, "cover", spec)
        event["request"]["reference_images"][0]["role"] = "scale"
        self.write_json("production/call.json", event)
        with self.assertRaisesRegex(ValueError, "Missing reference duties.*illustration_style"):
            ge.register(self.folder, image, "cover", spec)
        event = self.full_event(image, "cover")
        for role, token in [("illustration_style", "key-cup-style"), ("subject_scale", "approved-carrot"), ("home_treatment", "approved-window")]:
            changed = copy.deepcopy(event)
            changed["request"]["reference_images"] = [r for r in changed["request"]["reference_images"] if token not in r["path"]]
            self.write_json("production/call.json", changed)
            with self.assertRaisesRegex(ValueError, role): ge.register(self.folder, image, "cover", spec)
        self.write_json("production/call.json", event); record = ge.register(self.folder, image, "cover", spec)
        coverage = load(record)["reference_coverage"]
        self.assertEqual(coverage["required"], ["cover_layout", "home_treatment", "illustration_style", "subject_scale"])
        self.data["visual_family"] = "general"; self.write_manifest()
        event["request"]["reference_images"] = [r for r in event["request"]["reference_images"] if "approved-window" not in r["path"]]
        self.write_json("production/call.json", event); ge.register(self.folder, image, "cover", spec)
        self.assertFalse(ge.check(self.folder, image, "cover"))

    def test_practice_cover_inheritance_and_format_roles(self):
        import generation_evidence as ge
        for kind, name, missing in [("practice", "02-picture-practice.png", "practice_layout")]:
            image = self.folder / name; image.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (1086, 1448), "lightblue").save(image)
            event = self.full_event(image, kind)
            self.write_json("production/format.json", event)
            spec = {"mode": "generated", "method": "whole_page", "event_file": "production/format.json"}
            ge.register(self.folder, image, kind, spec)
            self.assertFalse(ge.check(self.folder, image, kind))
            changed = copy.deepcopy(event)
            changed["request"]["reference_images"] = [r for r in changed["request"]["reference_images"] if "approved-dog" not in r["path"]]
            self.write_json("production/format.json", changed)
            with self.assertRaisesRegex(ValueError, missing): ge.register(self.folder, image, kind, spec)
        # Current cover inheritance is revoked when its visual findings change.
        cover = self.folder / "01-cover.png"
        receipt = ge.receipt_path(self.folder, cover)
        d = load(receipt); d["visual_status"] = "fail"; self.write_json(receipt.relative_to(self.folder).as_posix(), d)
        self.write_json("production/format.json", event)
        self.assertTrue(ge.check(self.folder, image, kind))

    def test_catalog_coverage_and_qa_subject_requirement(self):
        from reference_roles import catalog
        import generation_evidence as ge
        from manifest_model import QA_FIELDS
        self.assertEqual(len(catalog()), 16)
        image = self.folder / "03-qa-01-04.png"
        Image.new("RGB", (1086, 1448), "white").save(image)
        event = self.full_event(image, "qa")
        event["request"]["prompt"] = "\n".join(q[f] for q in questions(self.data)[:4] for f in QA_FIELDS)
        spec = {"mode": "generated", "method": "whole_page", "event_file": "production/qa-roles.json", "sample": "self"}
        for missing in ["subject_continuity", "qa_layout"]:
            changed = copy.deepcopy(event)
            if missing == "subject_continuity":
                changed["request"]["reference_images"] = [r for r in changed["request"]["reference_images"] if r["path"] != "01-cover.png"]
            else:
                changed["request"]["reference_images"] = [r for r in changed["request"]["reference_images"] if "qa-" not in r["path"]]
            self.write_json("production/qa-roles.json", changed)
            with self.assertRaisesRegex(ValueError, missing): ge.register(self.folder, image, "qa", spec)

    def test_reference_plan_before_generation(self):
        import reference_roles
        image = self.folder / "not-generated.png"
        Image.new("RGB", (16, 16), "white").save(image)
        event = self.full_event(image, "cover")
        refs = [r["path"] for r in event["request"]["reference_images"]]
        image.unlink()
        with patch.object(sys, "argv", ["reference_roles.py", str(self.folder), "--kind", "cover", "--references", *refs]):
            self.assertEqual(reference_roles.main(), 0)
        with patch.object(sys, "argv", ["reference_roles.py", str(self.folder), "--kind", "cover", "--references", refs[2]]):
            self.assertEqual(reference_roles.main(), 1)

    def test_connector_raster_binding_and_no_line_false_pass(self):
        from connector_checks import check as check_lines, record_path, digest
        from check_visual_reviews import check_image
        import review_image as review
        image=self.folder/"01-cover.png";Image.new("RGB",(1086,1448),"white").save(image)
        data,receipt=review.prepare(self.folder,image,"cover")
        fp=self.write_json("bad-pass.json",{k:{"status":"pass","observation":"Synthetic false-pass attempt"} for k in data["required_visual_checks"]})
        with self.assertRaises(ValueError):review.record_findings(self.folder,receipt,fp)
        data.update(structure_status="pass",visual_status="pass",reviewed_at="2026-10-26T12:00:00+00:00",findings=load(fp))
        self.write_json(receipt.relative_to(self.folder).as_posix(),data)
        self.assertTrue(any("connector check failed" in e for e in check_image(self.folder,image,"cover")))
        self.connect_fixture(image)
        self.assertFalse(check_lines(self.folder,image,"cover"))
        self.inspect_fixture(image,"cover")
        pf=self.folder/"01-cover-plan.json";original=pf.read_bytes()
        pf.write_text(pf.read_text(encoding="utf-8")+" ",encoding="utf-8")
        self.assertTrue(check_image(self.folder,image,"cover"))
        pf.write_bytes(original)
        # Even relabelling the new output hash cannot hide erased connector pixels.
        Image.new("RGB",(1086,1448),"white").save(image)
        record=record_path(self.folder,image);d=load(record);d["candidate_sha256"]=digest(image);self.write_json(record.relative_to(self.folder).as_posix(),d)
        self.assertTrue(any("Final pixels" in e for e in check_lines(self.folder,image,"cover")))

    def test_connector_neatness_rejects_bad_geometry(self):
        from connector_checks import validate
        good=self.connector_plan_fixture()
        validate(self.data,good)
        cases=[]
        p=copy.deepcopy(good);p["width"]=0;cases.append(p)
        p=copy.deepcopy(good);p["color"]=[255,255,255];cases.append(p)
        p=copy.deepcopy(good);p["branches"][0]["points"][0]=[10,10];cases.append(p)
        p=copy.deepcopy(good);p["branches"][0]["points"][1]=[5,1400];cases.append(p)
        p=copy.deepcopy(good);p["branches"][0]["content_box"]=[280,60,1055,170];cases.append(p)
        p=copy.deepcopy(good);p["branches"][0]["points"][-1]=[700,80];cases.append(p)
        for p in cases:
            with self.assertRaises(ValueError):validate(self.data,p)
        crossed=copy.deepcopy(good)
        crossed["branches"][3]["points"]=[[290,660],[320,660],[350,515],[385,515]]
        crossed["branches"][4]["points"]=[[290,515],[320,515],[350,660],[385,660]]
        with self.assertRaisesRegex(ValueError,"cross"):
            validate(self.data,crossed)
        practice=self.connector_plan_fixture("practice");validate(self.data,practice)
        practice["title_box"]=[40,920,290,995]
        with self.assertRaises(ValueError):validate(self.data,practice)

    def test_release_integration_binds_evidence_gallery_and_inspection(self):
        import generation_evidence as ge
        import review_image as review
        import build_review_gallery
        image = self.folder / "01-cover.png"; Image.new("RGB", (1086, 1448), "white").save(image)
        self.connect_fixture(image)
        self.write_json("production/cover-call.json", self.full_event(image, "cover"))
        ge.register(self.folder, image, "cover", {"mode": "generated", "method": "whole_page", "event_file": "production/cover-call.json"})
        data, receipt = review.prepare(self.folder, image, "cover")
        findings = {key: {"status": "pass", "observation": "Synthetic integration fixture only; not actual artwork approval."} for key in data["required_visual_checks"]}
        fp = self.write_json("synthetic-findings.json", findings); review.record_findings(self.folder, receipt, fp)
        (self.folder / "prompt-notes.md").write_text("Synthetic test fixture", encoding="utf-8")
        with patch.object(sys, "argv", ["build_review_gallery.py", str(self.folder)]):
            self.assertEqual(build_review_gallery.main(), 0)
        self.assertFalse(check_release.check(self.folder, "cover")[0])
        event = json.loads((self.folder / "production/cover-call.json").read_text(encoding="utf-8"))
        event["request"]["prompt"] = "changed tool input"
        self.write_json("production/cover-call.json", event)
        self.assertTrue(check_release.check(self.folder, "cover")[0])


    def test_three_format_scope_and_removed_modes(self):
        self.assertEqual(check_release.scope_set("full"), {"cover", "practice", "qa"})
        for scope in ["video", "text", "caption", "qa,text", "unknown"]:
            with self.assertRaises(ValueError):
                check_release.scope_set(scope)

    def test_multi_question_page_mapping(self):
        self.assertEqual(len(self.data["groups"]), 9)
        self.assertEqual(len(questions(self.data)), 13)
        expected = expected_content(self.folder, self.folder / "04-qa-05-07.png", "qa")
        self.assertEqual([q["id"] for q in expected["qa_items"]], [5, 6, 7])
        pages = build_qa_pages.paginate(questions(self.data), [4, 3, 3, 3])
        markup = "\n".join(build_qa_pages.page_html("Cup", self.data["brand"], page) for page in pages)
        self.assertEqual(sum(len(page) for page in pages), 13)
        self.assertIn('qa-art/13.png', markup)
        self.assertIn(self.data["qa_items"][12]["answer_zh"], markup)

    @patch("check_release.check_samples", return_value=[])
    @patch("check_release.check_generation", return_value=[])
    @patch("check_release.check_binding", return_value=[])
    @patch("check_release.check_image", return_value=[])
    def test_image_only_full_release_and_archive(self, *mocks):
        import zipfile
        from package_images import package
        self.make_outputs()
        self.assertFalse(check_release.check(self.folder)[0])
        self.assertFalse((self.folder / "video").exists())
        self.assertFalse((self.folder / "qa-en-only.txt").exists())
        self.assertFalse((self.folder / "caption.md").exists())
        self.assertFalse(check_release.check(self.folder, "cover")[0])
        archive = self.folder / "images.zip"
        package(self.folder, archive)
        with zipfile.ZipFile(archive) as z:
            members = z.namelist()
        self.assertEqual(len(members), 6)
        self.assertTrue(all(Path(name).suffix == ".png" for name in members))
        self.assertFalse(any("review" in name for name in members))
        (self.folder / "06-qa-11-13.png").unlink()
        with self.assertRaises(ValueError): package(self.folder, self.folder / "bad.zip")
        self.assertFalse((self.folder / "bad.zip").exists())

    @patch("check_release.check_samples", return_value=[])
    @patch("check_release.check_generation", return_value=[])
    @patch("check_release.check_binding", return_value=[])
    @patch("check_release.check_image", return_value=[])
    def test_qa_rejects_duplicate_and_missing_ranges(self, *mocks):
        self.make_outputs()
        shutil.copy2(self.folder / "03-qa-01-04.png", self.folder / "07-qa-01-04.png")
        self.assertTrue(check_release.check(self.folder, "qa")[0])
        (self.folder / "07-qa-01-04.png").unlink()
        (self.folder / "06-qa-11-13.png").unlink()
        self.assertTrue(check_release.check(self.folder, "qa")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
