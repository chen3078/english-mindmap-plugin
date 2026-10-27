#!/usr/bin/env python3
"""Check and package only cover, picture-practice and bilingual Q&A PNGs."""
import argparse
import zipfile
from pathlib import Path
import check_release

def package(folder, output):
    folder, output = Path(folder).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Output already exists; choose a new archive name")
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must be a ZIP archive")
    errors, warnings, count = check_release.check(folder)
    if errors:
        raise ValueError("Image release is incomplete or unverified: " + "; ".join(errors))
    images = [folder / "01-cover.png", folder / "02-picture-practice.png"]
    images += sorted(folder.glob("*-qa-*.png"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for image in images:
            archive.write(image, folder.name + "/" + image.name)
    return len(images)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic_folder", type=Path)
    parser.add_argument("output_zip", type=Path)
    args = parser.parse_args()
    try:
        count = package(args.topic_folder, args.output_zip)
        print(f"IMAGE PACKAGE: {args.output_zip.resolve()} ({count} PNGs; three formats only)")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("ERROR:", exc)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
