#!/usr/bin/env python3
"""
check_readmes.py

Walks a folder tree and verifies that every directory (except ones you
choose to exclude, e.g. "videos") contains a non-empty README.md.

Usage:
    python check_readmes.py /path/to/english
    python check_readmes.py /path/to/english --exclude videos images assets
    python check_readmes.py /path/to/english --readme-name readme.md

Exit code:
    0  -> everything OK
    1  -> at least one problem found (missing or empty README)
"""

import argparse
import os
import sys


def find_readme(dir_path: str, readme_name: str):
    """Case-insensitive lookup of a README file in dir_path. Returns full path or None."""
    target = readme_name.lower()
    try:
        for entry in os.listdir(dir_path):
            if entry.lower() == target and os.path.isfile(os.path.join(dir_path, entry)):
                return os.path.join(dir_path, entry)
    except PermissionError:
        return None
    return None


def main():
    parser = argparse.ArgumentParser(description="Check README.md exists and is non-empty in every folder level.")
    parser.add_argument("root", help="Root folder to start checking from (e.g. the 'english' folder)")
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["videos"],
        help="Folder names to skip (no README expected inside them). Default: videos",
    )
    parser.add_argument(
        "--readme-name",
        default="README.md",
        help="Filename to look for (case-insensitive). Default: README.md",
    )
    parser.add_argument(
        "--include-root",
        action="store_true",
        help="Also require a README directly inside the root folder itself.",
    )
    parser.add_argument(
        "--only-problems",
        action="store_true",
        help="Only print MISSING/EMPTY entries (skip the OK lines) — good for a quick log of what needs fixing.",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Error: '{root}' is not a directory.")
        sys.exit(2)

    exclude_set = {name.lower() for name in args.exclude}

    problems = []
    checked = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # don't descend into excluded folders
        dirnames[:] = [d for d in dirnames if d.lower() not in exclude_set]

        rel = os.path.relpath(dirpath, root)
        is_root = rel == "."

        # skip the root itself unless explicitly requested
        if is_root and not args.include_root:
            continue

        # skip excluded folders themselves (in case root walk lands on one)
        base_name = os.path.basename(dirpath)
        if base_name.lower() in exclude_set:
            continue

        checked += 1
        readme_path = find_readme(dirpath, args.readme_name)
        display = rel if not is_root else os.path.basename(root)

        if readme_path is None:
            problems.append((display, "MISSING"))
            print(f"[MISSING]  {display}/")
        else:
            size = os.path.getsize(readme_path)
            if size == 0:
                problems.append((display, "EMPTY"))
                print(f"[EMPTY]    {display}/{os.path.basename(readme_path)}")
            elif not args.only_problems:
                print(f"[OK]       {display}/{os.path.basename(readme_path)} ({size} bytes)")

    print("\n--- Summary ---")
    print(f"Folders checked: {checked}")
    print(f"Problems found : {len(problems)}")
    for display, issue in problems:
        print(f"  - {issue}: {display}")

    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
