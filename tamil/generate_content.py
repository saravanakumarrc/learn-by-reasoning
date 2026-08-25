#!/usr/bin/env python3
"""
Generate learning content from learning_path.json using a local Ollama model.

Expected project structure:

ai_solution_architect_learning/
├── learning_path.json
├── master_base_prompt.md
├── generate_content.py
└── <generated phase/topic folders>/

The master prompt should contain:
    {{TOPIC}}

Optional placeholders:
    {{SECTION_NUMBER}}
    {{PHASE_TITLE}}
    {{SECTION_TITLE}}
    {{TOPIC_TITLE}}

Example:
    python generate_content.py --model gemma3:12b
    python generate_content.py --model gemma3:12b --section 8.1.1
    python generate_content.py --status pending --limit 5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3:12b"
BASE_PROMPT_FILE = "master_base_prompt.md"
LEARNING_PATH_FILE = "ai-solution-architect-learning-path.json"


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)


def build_prompt(template: str, topic: dict[str, Any]) -> str:
    replacements = {
        "{{TOPIC}}": topic["topic_title"],
        "{{TOPIC_TITLE}}": topic["topic_title"],
        "{{SECTION_NUMBER}}": topic["section_number"],
        "{{PHASE_TITLE}}": topic["phase_title"],
        "{{SECTION_TITLE}}": topic["section_title"],
    }

    prompt = template
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)

    # Helpful validation: the master prompt must explicitly identify a topic.
    if prompt == template:
        raise ValueError(
            "No topic placeholder found in master_base_prompt.md. "
            "Add {{TOPIC}} where the generated topic should be inserted."
        )

    return prompt


def call_ollama(model: str, prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=1800,
    )
    response.raise_for_status()
    payload = response.json()

    result = payload.get("response", "").strip()
    if not result:
        raise RuntimeError("Ollama returned an empty response.")

    return result


def topic_output_path(root: Path, topic: dict[str, Any]) -> Path:
    folder = root / topic["folder"]
    filename = (
        f"{topic['section_number'].replace('.', '-')}-"
        f"{slugify(topic['topic_title'])}.md"
    )
    return folder / filename


def select_topics(
    topics: list[dict[str, Any]],
    status: str | None,
    section: str | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    selected = topics

    if status:
        selected = [t for t in selected if t["status"] == status]

    if section:
        selected = [
            t for t in selected
            if t["section_number"] == section
        ]

    if limit:
        selected = selected[:limit]

    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--status", default="pending")
    parser.add_argument("--section", help="Exact section number, e.g. 8.1.1")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without calling Ollama.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    path_file = root / LEARNING_PATH_FILE
    prompt_file = root / BASE_PROMPT_FILE

    if not path_file.exists():
        print(f"Missing {path_file}", file=sys.stderr)
        return 1

    if not prompt_file.exists():
        print(
            f"Missing {prompt_file}. "
            "Create master_base_prompt.md with a {{TOPIC}} placeholder.",
            file=sys.stderr,
        )
        return 1

    learning_path = load_json(path_file)
    template = prompt_file.read_text(encoding="utf-8")

    topics = select_topics(
        learning_path["topics"],
        args.status,
        args.section,
        args.limit,
    )

    if not topics:
        print("No matching topics found.")
        return 0

    print(f"Selected {len(topics)} topic(s). Model: {args.model}")

    for topic in topics:
        section_number = topic["section_number"]
        title = topic["topic_title"]
        output = topic_output_path(root, topic)

        print(f"\n[{section_number}] {title}")
        print(f"Output: {output}")

        try:
            prompt = build_prompt(template, topic)

            if args.dry_run:
                print("\n--- PROMPT ---")
                print(prompt)
                print("--- END PROMPT ---")
                continue

            topic["status"] = "in_progress"
            save_json(path_file, learning_path)

            content = call_ollama(args.model, prompt)

            output.parent.mkdir(parents=True, exist_ok=True)

            document = (
                f"# {title}\n\n"
                f"> **Learning Path:** {topic['phase_title']}\n"
                f"> **Section:** {section_number} — {topic['section_title']}\n\n"
                f"{content}\n"
            )

            output.write_text(document, encoding="utf-8")

            topic["status"] = "completed"
            topic["output_file"] = str(output.relative_to(root))

            save_json(path_file, learning_path)

            print("✓ Completed")

        except Exception as exc:
            topic["status"] = "failed"
            topic["error"] = str(exc)
            save_json(path_file, learning_path)
            print(f"✗ Failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
