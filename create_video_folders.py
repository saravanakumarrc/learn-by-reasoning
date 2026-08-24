#!/usr/bin/env python3
"""
create_video_folders.py

Reads the "AI Solution Architect Learning Path" JSON and, for every topic,
ensures:

    english/<phase-section-folder>/<topic-folder>/videos/

exists.

- If the topic folder already exists, it is left alone (not recreated).
- The "videos" subfolder is created if missing (safe to re-run any time).
- Nothing is deleted or overwritten. This script never touches README.md
  or any phase/section folders — those are assumed to already exist.
- Script/video files themselves are intentionally NOT created here; that's
  handled by your separate generation script.

Usage:
    python create_video_folders.py path/to/learning_path.json --root english
    python create_video_folders.py path/to/learning_path.json --root english --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path


def slugify(text: str) -> str:
    """Turn a topic title into a filesystem-safe slug, e.g.
    'Test doubles: mocks, stubs, fakes' -> 'test-doubles-mocks-stubs-fakes'
    """
    text = text.lower().strip()
    text = text.replace("&", " and ")
    # replace anything that isn't a letter/number with a hyphen
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def topic_folder_name(topic: dict) -> str:
    """
    Determine the folder name for a single topic, e.g. '1-1-1-clean-code'.

    Preference order:
    1. If output_file is present, derive the name from its basename
       (this guarantees consistency with topics already generated).
    2. Otherwise, build it from section_number + slugified topic_title,
       matching the same '<section-number-with-dashes>-<slug>' pattern.
    """
    output_file = topic.get("output_file")
    if output_file:
        # output_file may use backslashes (Windows) or forward slashes
        basename = re.split(r"[\\/]", output_file)[-1]
        stem = basename.rsplit(".", 1)[0]
        return stem

    section_number = topic.get("section_number", "")
    prefix = section_number.replace(".", "-")
    slug = slugify(topic.get("topic_title", ""))
    return f"{prefix}-{slug}" if prefix else slug


def ensure_topic_video_folder(root: Path, topic: dict, dry_run: bool) -> str:
    """
    Ensures <root>/<topic.folder>/<topic_folder_name>/videos exists.
    Returns a short status string for reporting.
    """
    section_folder = topic.get("folder", "")
    if not section_folder:
        return "SKIP (no 'folder' field)"

    t_folder_name = topic_folder_name(topic)
    if not t_folder_name:
        return "SKIP (could not derive folder name)"

    topic_path = root / section_folder / t_folder_name
    videos_path = topic_path / "videos"

    topic_existed = topic_path.exists()
    videos_existed = videos_path.exists()

    if dry_run:
        status = []
        status.append("topic exists" if topic_existed else "topic CREATE")
        status.append("videos exists" if videos_existed else "videos CREATE")
        return " / ".join(status) + f"  -> {topic_path}"

    topic_path.mkdir(parents=True, exist_ok=True)
    videos_path.mkdir(parents=True, exist_ok=True)

    if not topic_existed:
        return f"CREATED topic + videos -> {topic_path}"
    if not videos_existed:
        return f"topic existed, CREATED videos -> {videos_path}"
    return f"already complete -> {videos_path}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", help="Path to the learning path JSON file")
    parser.add_argument(
        "--root",
        default="english",
        help="Root folder that contains the phase/section folders (default: english)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without creating any folders",
    )
    args = parser.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"ERROR: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    root = Path(args.root)
    topics = data.get("topics", [])

    created_count = 0
    already_count = 0
    skip_count = 0

    for topic in topics:
        result = ensure_topic_video_folder(root, topic, args.dry_run)
        label = f"[{topic.get('section_number', '?'):>8}] {topic.get('topic_title', '')}"
        print(f"{label:60s} {result}")

        if result.startswith("SKIP"):
            skip_count += 1
        elif result.startswith("already"):
            already_count += 1
        else:
            created_count += 1

    print()
    print(f"Total topics processed: {len(topics)}")
    print(f"Newly created / updated: {created_count}")
    print(f"Already complete:        {already_count}")
    print(f"Skipped:                 {skip_count}")

    if args.dry_run:
        print("\n(dry run — no folders were actually created)")


if __name__ == "__main__":
    main()
