"""Check declared layout bounds; this does not locate artwork in actual pixels."""
import argparse
import json
import math
from pathlib import Path

HEIGHT = 1448
WIDTH = 1086


def checked_box(value):
    if (not isinstance(value, list) or len(value) != 4
            or any(type(n) not in (int, float) or not math.isfinite(n) for n in value)
            or not (0 <= value[0] < value[2] < WIDTH and 0 <= value[1] < value[3] < HEIGHT)):
        raise ValueError("Layout needs actual, finite subject/title bounds inside the page")
    return value


def validate_layout(manifest, plan, cover_plan=None):
    policy = manifest.get("layout_policy", {"version": 1, "mode": "centered"})
    if not isinstance(policy, dict) or policy.get("version") != 1:
        raise ValueError("layout_policy.version must be 1")
    mode = policy.get("mode", "centered")
    if mode not in ("centered", "user_directed"):
        raise ValueError("Unknown layout_policy.mode")
    instruction = policy.get("user_instruction")
    if mode == "user_directed" and (not isinstance(instruction, str) or not instruction.strip()):
        raise ValueError("A non-centered exception needs the user's actual layout instruction")
    subject = checked_box(plan.get("subject_box"))
    unit = list(subject)
    if plan.get("kind") == "cover" and "title_box" in plan:
        title = checked_box(plan["title_box"])
        unit = [min(subject[0], title[0]), min(subject[1], title[1]),
                max(subject[2], title[2]), max(subject[3], title[3])]
    center = (unit[1] + unit[3]) / 2
    result = {"policy": 1, "mode": mode, "subject_box": subject,
              "unit_box": unit, "center_y": center,
              "center_ratio": round(center / HEIGHT, 6),
              "offset_ratio": round(abs(center / HEIGHT - .5), 6),
              "pixel_bounds_verified_by_script": False}
    # This is a coarse rejection boundary, not an aesthetic score.
    if mode == "centered" and abs(center / HEIGHT - .5) > .10 + 1e-9:
        raise ValueError(f"Left subject/title is not vertically centered: center_y={center:g}, "
                         f"ratio={center/HEIGHT:.3f}; default permitted band is 0.40-0.60")
    if mode == "user_directed":
        result["user_instruction"] = instruction
    if cover_plan is not None:
        cover = checked_box(cover_plan.get("subject_box"))
        delta = max(abs(a-b) for a, b in zip(subject, cover))
        result["cover_subject_box"] = cover
        result["cover_max_edge_delta_px"] = delta
        if delta > 18:
            raise ValueError("Practice subject position/scale differs from the selected cover by more than 18px")
    return result


def measure_candidate(folder, candidate, kind):
    if kind not in ("cover", "practice"):
        return {}
    folder, candidate = Path(folder).resolve(), Path(candidate).resolve()
    from connector_checks import local, record_path
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8-sig"))
    receipt = json.loads(record_path(folder, candidate).read_text(encoding="utf-8"))
    plan = json.loads(local(folder, receipt["plan"]).read_text(encoding="utf-8"))
    parent = None
    cover_record = record_path(folder, folder / "01-cover.png")
    if kind == "practice" and cover_record.is_file():
        data = json.loads(cover_record.read_text(encoding="utf-8"))
        parent = json.loads(local(folder, data["plan"]).read_text(encoding="utf-8"))
    return validate_layout(manifest, plan, parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("--candidate", type=Path, default=Path("01-cover.png"))
    parser.add_argument("--kind", choices=("cover", "practice"), default="cover")
    args = parser.parse_args()
    try:
        candidate = (args.topic_folder / args.candidate).resolve()
        candidate.relative_to(args.topic_folder.resolve())
        print(json.dumps(measure_candidate(args.topic_folder, candidate, args.kind), indent=2, ensure_ascii=False))
        print("LAYOUT BOUNDS PASS; inspect actual pixel bounds, optical balance and connectors at 350px separately.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("LAYOUT FAIL:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
