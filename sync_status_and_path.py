#!/usr/bin/env python3
"""
sync_status_and_path.py

Reads a learning-path JSON (with a top-level "topics" array) and, for every
topic, checks what's ACTUALLY on disk. It then rewrites only three fields
per topic:

    - "folder"       -> the real folder path found on disk (or the
                         "expected" path computed from phase/section numbers
                         if nothing matching was found)
    - "output_file"  -> the real file path found on disk (or the expected
                         path if nothing was found)
    - "status"       -> "completed" if the output file actually exists on
                         disk, otherwise forced to "pending"

Everything else in the JSON (titles, phase/section metadata, the "phases"
block, etc.) is left untouched.

WHY THE FUZZY MATCHING:
Your phase/section folders on disk currently have inconsistent numeric
prefixes (e.g. both "02-distributed-systems" and "03-distributed-systems"
exist). This script ignores the numeric prefix when looking for a folder
match and compares only the slugified title, so it can still find your
files even when the number is wrong. It then writes back the folder/number
combo it actually found on disk.

USAGE:
    1. Edit the CONFIG section below (ROOT_DIR, JSON_PATH).
    2. python sync_status_and_path.py

A timestamped backup of the original JSON is written next to it before any
changes are made.
"""

import json
import os
import re
import shutil
from datetime import datetime

# ----------------------------- CONFIG ---------------------------------
ROOT_DIR = "english"                 # folder that contains 01-..., 02-..., etc.
JSON_PATH = "learning_path_new.json"     # path to your JSON file
# ------------------------------------------------------------------------


def slugify(text: str) -> str:
    """Matches the slug style already used in your folder names:
    "Architect's Developer Foundation" -> "architect-s-developer-foundation"
    "1. Programming mastery"           -> "1-programming-mastery"
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def strip_num_prefix(name: str) -> str:
    """'03-distributed-systems' -> 'distributed-systems'"""
    return re.sub(r"^\d+-", "", name)


def list_subdirs(path: str):
    if not os.path.isdir(path):
        return []
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


def find_matching_dir(parent: str, target_slug: str):
    """Look inside `parent` for a directory whose slug (ignoring leading
    number) matches target_slug. Returns the actual dir name or None."""
    for d in list_subdirs(parent):
        if strip_num_prefix(d) == target_slug:
            return d
    return None


def find_matching_file(folder: str, topic_slug: str):
    """Look inside `folder` for a .md file that ends with the topic slug,
    regardless of its numeric prefix. Returns the filename or None."""
    if not os.path.isdir(folder):
        return None
    for f in os.listdir(folder):
        if f.lower().endswith(topic_slug + ".md"):
            return f
    return None


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    backup_path = JSON_PATH + ".bak." + datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.copyfile(JSON_PATH, backup_path)
    print(f"Backed up original JSON to {backup_path}")

    updated = 0
    forced_pending = 0
    not_found_at_all = 0

    for topic in data.get("topics", []):
        phase_num = topic["phase_number"]
        phase_title_slug = slugify(topic["phase_title"])
        section_title_slug = slugify(topic["section_title"])
        topic_slug = slugify(topic["topic_title"])

        parts = str(topic["section_number"]).split(".")
        section_idx = int(parts[1])
        topic_idx = int(parts[2])

        # 1. Find the phase folder actually on disk
        actual_phase_dir = find_matching_dir(ROOT_DIR, phase_title_slug)
        expected_phase_dir = f"{phase_num:02d}-{phase_title_slug}"
        phase_dir_name = actual_phase_dir or expected_phase_dir

        # 2. Find the section folder actually on disk (inside the phase dir)
        phase_path = os.path.join(ROOT_DIR, phase_dir_name)
        actual_section_dir = find_matching_dir(phase_path, section_title_slug)
        expected_section_dir = f"{section_idx:02d}-{section_title_slug}"
        section_dir_name = actual_section_dir or expected_section_dir

        section_path = os.path.join(phase_path, section_dir_name)

        # 3. Find the actual output file inside that section folder
        actual_file = find_matching_file(section_path, topic_slug)
        expected_file = f"{phase_num}-{section_idx}-{topic_idx}-{topic_slug}.md"
        file_name = actual_file or expected_file

        new_folder = f"{phase_dir_name}/{section_dir_name}/"
        new_output_file = f"{phase_dir_name}\\{section_dir_name}\\{file_name}"

        file_exists = actual_file is not None

        if topic.get("folder") != new_folder or topic.get("output_file") != new_output_file:
            updated += 1
        topic["folder"] = new_folder
        topic["output_file"] = new_output_file

        if file_exists:
            topic["status"] = "completed"
        else:
            if topic.get("status") != "pending":
                forced_pending += 1
            topic["status"] = "pending"

        if actual_phase_dir is None or actual_section_dir is None:
            not_found_at_all += 1

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Done. {updated} topics had folder/output_file corrected.")
    print(f"{forced_pending} topics were forced back to 'pending' (file not found on disk).")
    print(f"{not_found_at_all} topics could not be matched to an existing folder at all "
          f"(their path is a best guess, status is pending).")


if __name__ == "__main__":
    main()
