#!/usr/bin/env python3
"""
generate_video_script.py

Batch video-script generator for the Learn by Reasoning learning-path JSON.

IMPORTANT:
- The learning-path JSON is the SINGLE SOURCE OF TRUTH.
- The JSON contains a `topics` array.
- Each topic contains:
    status
    output_file
    script_generation_status
    script_path
    video_generation_status
    video_path
- Only topics whose learning `status` is `completed` are eligible.
- Topics whose `script_generation_status` is already `completed` are skipped.
- The generated script is saved using the topic's existing identity/path.
- The SAME learning-path JSON is updated after every successful topic.

LLM:
    Local Ollama only.
    Default model: muse-glimmer

Usage:
    python generate_video_script.py path/to/learning_path.json

Optional:
    python generate_video_script.py path/to/learning_path.json path/to/video_script_master_prompt.md

Environment:
    OLLAMA_HOST=http://localhost:11434
    OLLAMA_MODEL=muse-glimmer
    VIDEO_SCRIPT_PROMPT=video_script_master_prompt.md

Dependency:
    pip install requests
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "muse-glimmer"
DEFAULT_PROMPT = "video_script_master_prompt.md"
DEFAULT_OUTPUT_DIR = "script_outputs"

MAX_RETRIES = 3
OLLAMA_TIMEOUT_SECONDS = 1800


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Learning-path JSON must contain an object.")

    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Atomically replace the source-of-truth JSON."""
    temp = path.with_suffix(path.suffix + ".tmp")

    with temp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    temp.replace(path)


def resolve_path(value: str, json_path: Path) -> Path:
    path = Path(value)

    if path.is_absolute():
        return path

    candidate = json_path.parent / path
    if candidate.exists():
        return candidate

    return Path.cwd() / path


def check_ollama(host: str, model: str) -> None:
    try:
        response = requests.get(
            host.rstrip("/") + "/api/tags",
            timeout=10,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Cannot connect to Ollama at {host}. "
            "Start Ollama with `ollama serve`."
        ) from exc

    models = response.json().get("models", [])
    names = {
        item.get("name")
        for item in models
        if item.get("name")
    }

    if model in names:
        return

    base_names = {name.split(":")[0] for name in names}

    if model in base_names:
        return

    raise RuntimeError(
        f"Ollama model '{model}' is not installed.\n"
        f"Available models: {', '.join(sorted(names))}"
    )


def call_ollama(host: str, model: str, prompt: str) -> str:
    response = requests.post(
        host.rstrip("/") + "/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
            },
        },
        timeout=OLLAMA_TIMEOUT_SECONDS,
    )

    response.raise_for_status()

    output = response.json().get("response")

    if not output:
        raise RuntimeError("Ollama returned an empty response.")

    return output


def parse_json(text: str) -> dict[str, Any]:
    text = text.strip()

    # Direct JSON.
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    # Markdown fenced JSON.
    if "```json" in text:
        text = text.split("```json", 1)[1]
        text = text.split("```", 1)[0]
    elif "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:]

    text = text.strip()

    # JSON embedded in accidental prose.
    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:
        value = json.loads(text[start:end + 1])
        if isinstance(value, dict):
            return value

    raise ValueError("Ollama did not return a valid JSON object.")


def validate_script(script: dict[str, Any], section_number: str) -> None:
    if script.get("section_number") != section_number:
        raise ValueError(
            f"section_number mismatch: expected '{section_number}', "
            f"got '{script.get('section_number')}'"
        )

    required = [
        "video_title",
        "thumbnail_text",
        "core_insight",
        "video_type",
        "language",
        "duration_target_seconds",
        "scenes",
        "mental_model",
        "final_takeaway",
    ]

    missing = [field for field in required if not script.get(field)]

    if missing:
        raise ValueError(
            "Generated script is missing: " + ", ".join(missing)
        )

    if not isinstance(script["scenes"], list) or not script["scenes"]:
        raise ValueError("Generated script must contain non-empty scenes.")

    for index, scene in enumerate(script["scenes"], 1):
        if not isinstance(scene, dict):
            raise ValueError(f"Scene {index} must be an object.")

        if not scene.get("voice"):
            raise ValueError(f"Scene {index} has no voice narration.")

        if not scene.get("visual"):
            raise ValueError(f"Scene {index} has no visual direction.")


def topic_identity(topic: dict[str, Any], index: int) -> str:
    """
    Prefer the canonical topic title. If a future schema adds a section_number,
    use it. Never invent a new persistent ID.
    """
    return str(
        topic.get("section_number")
        or topic.get("topic_id")
        or topic.get("topic_title")
        or f"topic-{index:04d}"
    )


def get_topic_source_path(
    topic: dict[str, Any],
    json_path: Path,
) -> Path:
    output_file = topic.get("output_file")

    if not output_file:
        raise ValueError("Topic has no output_file.")

    source = resolve_path(str(output_file), json_path)

    if not source.exists():
        raise FileNotFoundError(
            f"Topic source file not found: {source}"
        )

    return source


def build_prompt(
    master_prompt: str,
    topic: dict[str, Any],
    source_path: Path,
    source_content: str,
    index: int,
) -> str:
    identity = topic_identity(topic, index)

    return f"""
{master_prompt}

============================================================
SOURCE TOPIC METADATA
============================================================

topic_identity:
{identity}

topic_title:
{topic.get("topic_title", "")}

section_number:
{topic.get("section_number", "")}

phase_number:
{topic.get("phase_number", "")}

phase_title:
{topic.get("phase_title", "")}

section_title:
{topic.get("section_title", "")}

source_file:
{source_path}

============================================================
CANONICAL LEARNING CONTENT
============================================================

{source_content}

============================================================
FINAL INSTRUCTIONS
============================================================

Generate ONE short-video learning script from this topic.

The topic's canonical identity is:

{identity}

The generated JSON `section_number` MUST be exactly:

{identity}

Do not invent a different ID.

Use only the supplied canonical learning content as the factual source.

Return ONLY valid JSON according to the master prompt.
"""


def generate_one_topic(
    topic: dict[str, Any],
    topic_index: int,
    data_path: Path,
    master_prompt: str,
    host: str,
    model: str,
    output_root: Path,
) -> str:
    identity = topic_identity(topic, topic_index)

    source_path = get_topic_source_path(
        topic,
        data_path,
    )

    source_content = source_path.read_text(
        encoding="utf-8"
    )

    prompt = build_prompt(
        master_prompt=master_prompt,
        topic=topic,
        source_path=source_path,
        source_content=source_content,
        index=topic_index,
    )

    script = None
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(
                f"    generation attempt {attempt}/{MAX_RETRIES}"
            )

            raw = call_ollama(
                host=host,
                model=model,
                prompt=prompt,
            )

            script = parse_json(raw)

            validate_script(
                script,
                identity,
            )

            break

        except Exception as exc:
            last_error = exc
            print(
                f"    warning: {exc}",
                file=sys.stderr,
            )

            if attempt < MAX_RETRIES:
                time.sleep(3)

    if script is None:
        raise RuntimeError(
            f"Generation failed for {identity}: {last_error}"
        )

    script.setdefault(
        "prompt_version",
        "video_script_master_prompt",
    )

    script["generation"] = {
        "provider": "ollama",
        "model": model,
        "host": host,
        "source_file": str(source_path),
    }

    # Preserve the topic's folder structure where possible.
    #
    # Example:
    #   topic.folder =
    #       01-architect-s-developer-foundation/
    #       01-1-programming-mastery/
    #
    # becomes:
    #   script_outputs/
    #       01-architect-s-developer-foundation/
    #       01-1-programming-mastery/
    #
    # If folder is absent, save directly under script_outputs.
    folder = str(topic.get("folder") or "").strip()

    if folder:
        output_dir = output_root / Path(folder)
    else:
        output_dir = output_root

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Use the source lesson filename stem when available.
    # This keeps artifact names aligned with existing content.
    filename_stem = source_path.stem

    script_path = output_dir / f"{filename_stem}.json"

    script_path.write_text(
        json.dumps(
            script,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    # Store a path relative to the learning-path JSON when possible.
    try:
        relative_script_path = script_path.relative_to(
            data_path.parent
        )
        return str(relative_script_path)

    except ValueError:
        return str(script_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate video scripts for completed topics in "
            "the Learn by Reasoning learning-path JSON."
        )
    )

    parser.add_argument(
        "learning_path_json",
        type=Path,
        help="The master learning-path JSON.",
    )

    parser.add_argument(
        "prompt_file",
        type=Path,
        nargs="?",
        help="Optional video master prompt Markdown file.",
    )

    args = parser.parse_args()

    json_path = args.learning_path_json.resolve()

    try:
        data = load_json(json_path)

        topics = data.get("topics")

        if not isinstance(topics, list):
            raise ValueError(
                "Learning-path JSON must contain a `topics` array."
            )

        prompt_value = (
            # str(args.prompt_file)
            # if args.prompt_file
            os.getenv(
                "VIDEO_SCRIPT_PROMPT",
                DEFAULT_PROMPT,
            )
        )

        prompt_path = resolve_path(
            prompt_value,
            json_path,
        )

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Master video prompt not found: {prompt_path}"
            )

        master_prompt = prompt_path.read_text(
            encoding="utf-8"
        )

        host = os.getenv(
            "OLLAMA_HOST",
            DEFAULT_OLLAMA_HOST,
        )

        model = os.getenv(
            "OLLAMA_MODEL",
            DEFAULT_OLLAMA_MODEL,
        )

        output_root_value = data.get(
            "script_output_dir",
            DEFAULT_OUTPUT_DIR,
        )

        output_root = resolve_path(
            str(output_root_value),
            json_path,
        )

        print("==============================================")
        print(" Learn by Reasoning - Video Script Generator")
        print("==============================================")
        print(f"JSON   : {json_path}")
        print(f"Model  : {model}")
        print(f"Ollama : {host}")
        print(f"Prompt : {prompt_path}")
        print(f"Output : {output_root}")
        print(f"Topics : {len(topics)}")
        print("==============================================")

        check_ollama(
            host,
            model,
        )

        completed = 0
        skipped = 0
        failed = 0

        for index, topic in enumerate(topics, start=1):
            if not isinstance(topic, dict):
                print(
                    f"[SKIP] topic {index}: not an object"
                )
                skipped += 1
                continue

            identity = topic_identity(
                topic,
                index,
            )

            print()
            print(
                f"[{index}/{len(topics)}] {identity}"
            )

            # ------------------------------------------------
            # Only learning-content-complete topics proceed.
            # ------------------------------------------------

            if topic.get("status") != "completed":
                print(
                    f"  [SKIP] learning status = "
                    f"{topic.get('status')}"
                )
                skipped += 1
                continue

            # ------------------------------------------------
            # Script already exists according to SSoT.
            # ------------------------------------------------

            if (
                topic.get(
                    "script_generation_status"
                )
                == "completed"
            ):
                print(
                    "  [SKIP] script already completed"
                )
                skipped += 1
                continue

            # ------------------------------------------------
            # Mark this individual topic as running.
            # Save immediately so the JSON remains stateful.
            # ------------------------------------------------

            topic[
                "script_generation_status"
            ] = "in_progress"

            topic.pop(
                "script_generation_error",
                None,
            )

            save_json(
                json_path,
                data,
            )

            try:
                script_path = generate_one_topic(
                    topic=topic,
                    topic_index=index,
                    data_path=json_path,
                    master_prompt=master_prompt,
                    host=host,
                    model=model,
                    output_root=output_root,
                )

                # --------------------------------------------
                # Update the SAME topic object.
                # --------------------------------------------

                topic[
                    "script_generation_status"
                ] = "completed"

                topic[
                    "script_path"
                ] = script_path

                save_json(
                    json_path,
                    data,
                )

                print(
                    f"  [DONE] script = {script_path}"
                )

                completed += 1

            except Exception as exc:
                topic[
                    "script_generation_status"
                ] = "failed"

                topic[
                    "script_generation_error"
                ] = str(exc)

                save_json(
                    json_path,
                    data,
                )

                print(
                    f"  [FAILED] {exc}",
                    file=sys.stderr,
                )

                failed += 1

                # Continue to the next topic.
                # This is important for long-running batch jobs.
                continue

        print()
        print("==============================================")
        print("Generation finished")
        print("==============================================")
        print(f"Generated : {completed}")
        print(f"Skipped   : {skipped}")
        print(f"Failed    : {failed}")
        print("==============================================")

        return 1 if failed else 0

    except Exception as exc:
        print(
            f"[FATAL] {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
