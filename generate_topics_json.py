#!/usr/bin/env python3
"""
Walks a folder structure like:

    english/
      01-architect-s-developer-foundation/     (phase)
        01-1-programming-mastery/               (section)
          1-1-1-clean-code/                     (topic)
            videos/
            README.md
          1-1-2-solid/
            videos/
            README.md
          1-1-3-oop/
            ...

...and generates a topics.json file like:

{
  "topics": [
    {
      "section_number": "1.1.1",
      "phase_number": 1,
      "phase_title": "Architect's Developer Foundation",
      "section_title": "1. Programming mastery",
      "topic_title": "Clean code",
      "folder": "01-architect-s-developer-foundation/01-1-programming-mastery/",
      "status": "completed",
      "output_file": "01-architect-s-developer-foundation\\01-1-programming-mastery\\1-1-1-clean-code.md"
    },
    ...
  ]
}

Usage:
    python generate_topics_json.py <root_folder> [output.json]

Example:
    python generate_topics_json.py ./english topics.json
"""

import os
import re
import sys
import json

def split_leading_numbers(name: str):
    """
    Splits a folder name into its leading run of numeric dash-separated
    tokens and the remaining title text.

    '01-1-programming-mastery' -> (['01', '1'], 'programming-mastery')
    '01-core-concepts'         -> (['01'], 'core-concepts')
    '1-1-1-clean-code'         -> (['1', '1', '1'], 'clean-code')
    'videos'                   -> ([], 'videos')
    """
    parts = name.split('-')
    nums = []
    for p in parts:
        if p.isdigit():
            nums.append(p)
        else:
            break
    rest = '-'.join(parts[len(nums):])
    return nums, rest


def title_case(raw: str) -> str:
    """'developer-foundation' -> 'Developer Foundation'"""
    words = raw.replace('-', ' ').replace('_', ' ').split()
    return ' '.join(w.capitalize() for w in words)


def sentence_case(raw: str) -> str:
    """'clean-code' -> 'Clean code'"""
    text = raw.replace('-', ' ').replace('_', ' ').strip()
    return text[:1].upper() + text[1:] if text else text


def build_topics(root_dir: str, verbose: bool = True):
    topics = []
    root_dir = os.path.abspath(root_dir)

    for phase_name in sorted(os.listdir(root_dir)):
        phase_path = os.path.join(root_dir, phase_name)
        if not os.path.isdir(phase_path):
            continue
        phase_nums, phase_rest = split_leading_numbers(phase_name)
        if not phase_nums or not phase_rest:
            if verbose:
                print(f"[SKIP phase]  '{phase_name}' has no leading number + title", file=sys.stderr)
            continue
        phase_number = int(phase_nums[0])
        phase_title = title_case(phase_rest)

        for section_name in sorted(os.listdir(phase_path)):
            section_path = os.path.join(phase_path, section_name)
            if not os.path.isdir(section_path):
                continue
            section_nums, section_rest = split_leading_numbers(section_name)
            if not section_nums or not section_rest:
                if verbose:
                    print(f"[SKIP section] '{phase_name}/{section_name}' has no leading number + title", file=sys.stderr)
                continue
            # Use the LAST numeric token as the local section number, since
            # some phases prefix the phase number again (01-1-...) and some
            # don't (01-...).
            section_num_label = int(section_nums[-1])
            section_title = f"{section_num_label}. {title_case(section_rest)}"
            folder_rel = f"{phase_name}/{section_name}/"

            for topic_name in sorted(os.listdir(section_path)):
                topic_path = os.path.join(section_path, topic_name)
                if not os.path.isdir(topic_path):
                    continue
                topic_nums, topic_rest = split_leading_numbers(topic_name)
                if not topic_nums or not topic_rest:
                    if verbose:
                        print(f"[SKIP topic]   '{phase_name}/{section_name}/{topic_name}' has no leading number + title", file=sys.stderr)
                    continue

                section_number = '.'.join(topic_nums)
                topic_title = sentence_case(topic_rest)

                has_readme = os.path.isfile(os.path.join(topic_path, "README.md"))
                status = "completed" if has_readme else "pending"

                output_file = f"{phase_name}\\{section_name}\\{topic_name}.md"

                topics.append({
                    "section_number": section_number,
                    "phase_number": phase_number,
                    "phase_title": phase_title,
                    "section_title": section_title,
                    "topic_title": topic_title,
                    "folder": folder_rel,
                    "status": status,
                    "output_file": output_file
                })

    return topics


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_topics_json.py <root_folder> [output.json]", file=sys.stderr)
        sys.exit(1)

    root_dir = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "topics.json"

    topics = build_topics(root_dir, verbose=True)
    result = {"topics": topics}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(topics)} topics to {out_path}")


if __name__ == "__main__":
    main()
