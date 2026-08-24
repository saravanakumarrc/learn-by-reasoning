#!/usr/bin/env python3
"""
create_readme_files.py

Copies the already-generated content file for each topic (living as a flat
.md file inside your source folder, e.g. '1-1-1-clean-code.md') into that
topic's folder inside the 'english' structure, renamed to README.md:

    <source>/<phase-section-folder>/1-1-1-clean-code.md
        --> <english>/<phase-section-folder>/1-1-1-clean-code/README.md

- Topics with no matching source file are reported and skipped (nothing
  written).
- By default, an existing README.md in the target topic folder is left
  untouched (skipped). Pass --overwrite to replace it anyway.
- The topic folder itself is created if it somehow doesn't exist yet, but
  this script does NOT touch the 'videos' subfolder — that's handled by
  the other script.

Usage:
    python create_readme_files.py learning_path.json --source content --target english
    python create_readme_files.py learning_path.json --source content --target english --dry-run
    python create_readme_files.py learning_path.json --source content --target english --overwrite
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def topic_folder_name(topic: dict) -> str:
    """Same naming logic used by create_video_folders.py, so the two scripts
    always agree on the folder name for a given topic."""
    output_file = topic.get("output_file")
    if output_file:
        basename = re.split(r"[\\/]", output_file)[-1]
        return basename.rsplit(".", 1)[0]

    section_number = topic.get("section_number", "")
    prefix = section_number.replace(".", "-")
    slug = slugify(topic.get("topic_title", ""))
    return f"{prefix}-{slug}" if prefix else slug


def process_topic(source_root: Path, target_root: Path, topic: dict,
                   overwrite: bool, dry_run: bool) -> str:
    section_folder = topic.get("folder", "")
    if not section_folder:
        return "SKIP (no 'folder' field)"

    name = topic_folder_name(topic)
    if not name:
        return "SKIP (could not derive folder name)"

    source_file = source_root / section_folder / f"{name}.md"
    topic_folder = target_root / section_folder / name
    readme_path = topic_folder / "README.md"

    if not source_file.exists():
        return f"MISSING SOURCE -> {source_file}"

    readme_existed = readme_path.exists()
    if readme_existed and not overwrite:
        return f"SKIP (README already exists) -> {readme_path}"

    if dry_run:
        action = "OVERWRITE" if readme_existed else "CREATE"
        return f"{action} (dry run) -> {readme_path}"

    topic_folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_file, readme_path)

    return ("OVERWROTE" if readme_existed else "CREATED") + f" -> {readme_path}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", help="Path to the learning path JSON file")
    parser.add_argument(
        "--source", required=True,
        help="Root folder containing the flat '<phase-section-folder>/<topic>.md' content files",
    )
    parser.add_argument(
        "--target", default="english",
        help="Root 'english' folder containing the topic folders (default: english)",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Replace README.md even if it already exists",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without writing any files",
    )
    args = parser.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"ERROR: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    source_root = Path(args.source)
    target_root = Path(args.target)

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    topics = data.get("topics", [])

    created = overwritten = skipped_exists = missing = other_skip = 0

    for topic in topics:
        result = process_topic(source_root, target_root, topic, args.overwrite, args.dry_run)
        label = f"[{topic.get('section_number', '?'):>8}] {topic.get('topic_title', '')}"
        print(f"{label:60s} {result}")

        if result.startswith("CREATED") or result.startswith("CREATE"):
            created += 1
        elif result.startswith("OVERWR"):
            overwritten += 1
        elif result.startswith("SKIP (README"):
            skipped_exists += 1
        elif result.startswith("MISSING"):
            missing += 1
        else:
            other_skip += 1

    print()
    print(f"Total topics processed:      {len(topics)}")
    print(f"README created:              {created}")
    print(f"README overwritten:          {overwritten}")
    print(f"Skipped (already exists):    {skipped_exists}")
    print(f"Missing source file:         {missing}")
    print(f"Skipped (other):             {other_skip}")

    if args.dry_run:
        print("\n(dry run — no files were actually written)")


if __name__ == "__main__":
    main()
