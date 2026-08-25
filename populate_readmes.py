"""
Matches each file in a flat source folder to a nested "topic" folder inside
a target folder tree, and copies the source file's content into that topic
folder as README.md.

Target folder structure expected:
    target_folder/
        01-PhaseName/
            01-SectionName/
                01-TopicName/          <-- README.md goes here
                02-AnotherTopic/
            02-AnotherSection/
                ...
        02-NextPhase/
            ...

Phase, section, and topic folders are all prefixed with a 2-digit number
followed by a hyphen (e.g. "01-", "02-"). Since phase/section/topic NUMBERS
can be inconsistent/confusing, matching is done purely by NAME (the part
after the "NN-" prefix), not by number.

Matching rules (topic folder name vs source file name):
    - The numeric "NN-" prefix on the folder name is ignored.
    - The source file's extension is ignored.
    - Comparison is case-insensitive.
    - Hyphens/underscores are treated the same as spaces.

For every source file:
    - If a matching topic folder is found:
        - If README.md already exists there -> print a message, do NOT overwrite.
        - If README.md does not exist there -> print a message, then copy the
          source file's content into that folder as README.md.
    - If no matching topic folder is found -> print a message and skip.

Usage:
    python populate_readmes.py <source_folder> <target_folder>
"""

import os
import re
import shutil
import sys

PREFIX_PATTERN = re.compile(r"^\d+-\d+-\d+-")


def normalize(name: str) -> str:
    """Strip a leading 'NN-' prefix (if present) and normalize for comparison."""
    name = PREFIX_PATTERN.sub("", name)
    name = name.replace("_", " ").replace("-", " ")
    return name.strip().lower()


def find_topic_folders(target_folder: str):
    """
    Walk phase -> section -> topic and yield (normalized_name, full_path)
    for every topic-level (deepest) folder.
    """
    for phase in sorted(os.listdir(target_folder)):
        phase_path = os.path.join(target_folder, phase)
        if not os.path.isdir(phase_path):
            continue

        for section in sorted(os.listdir(phase_path)):
            section_path = os.path.join(phase_path, section)
            if not os.path.isdir(section_path):
                continue

            for topic in sorted(os.listdir(section_path)):
                topic_path = os.path.join(section_path, topic)
                if not os.path.isdir(topic_path):
                    continue

                yield normalize(topic), topic_path


def populate_readmes(source_folder: str, target_folder: str) -> None:
    if not os.path.isdir(source_folder):
        raise NotADirectoryError(f"Source folder does not exist: {source_folder}")
    if not os.path.isdir(target_folder):
        raise NotADirectoryError(f"Target folder does not exist: {target_folder}")

    # Build a lookup of normalized topic name -> list of matching folder paths
    topic_lookup = {}
    for norm_name, path in find_topic_folders(target_folder):
        topic_lookup.setdefault(norm_name, []).append(path)

    copied_count = 0
    skipped_existing = 0
    not_found_count = 0

    for filename in sorted(os.listdir(source_folder)):
        source_path = os.path.join(source_folder, filename)
        if not os.path.isfile(source_path):
            continue

        file_stem = os.path.splitext(filename)[0]
        norm_stem = normalize(file_stem)

        matches = topic_lookup.get(norm_stem, [])

        if not matches:
            print(f"[NOT FOUND] No matching topic folder for '{filename}'")
            not_found_count += 1
            continue

        if len(matches) > 1:
            print(f"[WARNING] Multiple topic folders match '{filename}': {matches}")

        for topic_path in matches:
            readme_path = os.path.join(topic_path, "README.md")

            if os.path.exists(readme_path):
                print(f"[EXISTS] README.md already exists in '{topic_path}' - skipped '{filename}'")
                skipped_existing += 1
            else:
                shutil.copy2(source_path, readme_path)
                print(f"[COPIED] '{filename}' -> '{readme_path}'")
                copied_count += 1

    print(
        f"\nDone. {copied_count} README.md file(s) copied, "
        f"{skipped_existing} skipped (already existed), "
        f"{not_found_count} source file(s) had no matching topic folder."
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python populate_readmes.py <source_folder> <target_folder>")
        sys.exit(1)

    src = sys.argv[1]
    tgt = sys.argv[2]

    populate_readmes(src, tgt)
