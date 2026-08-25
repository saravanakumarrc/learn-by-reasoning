#!/usr/bin/env python3
"""Generate Learn-by-Reasoning video scripts with a local Ollama model.

No OpenAI dependency.

Usage:
  python generate_video_script_ollama.py path/to/lesson.json
  python generate_video_script_ollama.py path/to/lesson.json prompts/video_script_master_prompt.md

Environment:
  OLLAMA_HOST=http://localhost:11434
  OLLAMA_MODEL=muse-gilmer
  VIDEO_SCRIPT_PROMPT=prompts/video_script_master_prompt.md
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

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "muse-gilmer"
DEFAULT_PROMPT = "video_script_master_prompt.md"
DEFAULT_OUTPUT = "script_outputs"
MAX_RETRIES = 3
TIMEOUT = 1800


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Source JSON must be an object.")
    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def resolve_path(value: str, json_path: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    candidate = json_path.parent / path
    return candidate if candidate.exists() else Path.cwd() / path


def get_lesson_path(data: dict[str, Any]) -> str:
    for key in ("lesson_path", "source_path", "content_path",
                "learning_content_path"):
        if data.get(key):
            return str(data[key])
    raise ValueError(
        "JSON must contain lesson_path, source_path, "
        "content_path, or learning_content_path."
    )


def check_ollama(host: str, model: str) -> None:
    try:
        r = requests.get(host.rstrip("/") + "/api/tags", timeout=10)
        r.raise_for_status()
        names = {
            m.get("name") for m in r.json().get("models", [])
            if m.get("name")
        }
        if model not in names and model.split(":")[0] not in {
            n.split(":")[0] for n in names
        }:
            raise RuntimeError(
                f"Model '{model}' is not installed. Available: "
                + ", ".join(sorted(names))
            )
    except requests.RequestException as e:
        raise RuntimeError(
            f"Cannot connect to Ollama at {host}. Run `ollama serve`."
        ) from e


def call_ollama(host: str, model: str, prompt: str) -> str:
    r = requests.post(
        host.rstrip("/") + "/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    output = r.json().get("response")
    if not output:
        raise RuntimeError("Ollama returned an empty response.")
    return output


def parse_model_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

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

    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(text[start:end + 1])
        if isinstance(value, dict):
            return value

    raise ValueError("Ollama did not return valid JSON.")


def validate_script(script: dict[str, Any], section_number: str) -> None:
    if script.get("section_number") != section_number:
        raise ValueError("Generated section_number does not match source section_number.")

    required = [
        "video_title", "thumbnail_text", "core_insight", "video_type",
        "language", "duration_target_seconds", "scenes",
        "mental_model", "final_takeaway",
    ]
    missing = [x for x in required if not script.get(x)]
    if missing:
        raise ValueError("Missing generated fields: " + ", ".join(missing))

    if not isinstance(script["scenes"], list) or not script["scenes"]:
        raise ValueError("Generated scenes must be a non-empty array.")

    for i, scene in enumerate(script["scenes"], 1):
        if not isinstance(scene, dict):
            raise ValueError(f"Scene {i} is not an object.")
        if not scene.get("voice"):
            raise ValueError(f"Scene {i} has no voice.")
        if not scene.get("visual"):
            raise ValueError(f"Scene {i} has no visual.")


def build_prompt(master: str, section_number: str, lesson_path: Path,
                 lesson: str) -> str:
    return f"""{master}

SOURCE-OF-TRUTH METADATA
section_number: {section_number}
lesson_path: {lesson_path}

CANONICAL LEARNING CONTENT
==========================
{lesson}

FINAL INSTRUCTIONS
==================
Generate the short-video script according to the master prompt.
The section_number MUST be exactly: {section_number}
Return ONLY valid JSON. Do not use Markdown fences.
"""


def main() -> int:

    json_path = Path("learning_path.json")

    try:
        data = load_json(json_path)
        section_number = data.get("section_number")
        if not section_number:
            raise ValueError("JSON is missing section_number.")

        if data.get("script_generation_status") == "completed":
            print(f"[SKIP] {section_number}: script already completed.")
            return 0

        prompt_value = os.getenv(
            "VIDEO_SCRIPT_PROMPT", DEFAULT_PROMPT
        )
        prompt_path = resolve_path(prompt_value, json_path)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Master prompt not found: {prompt_path}")

        lesson_path = resolve_path(get_lesson_path(data), json_path)
        if not lesson_path.exists():
            raise FileNotFoundError(f"Lesson not found: {lesson_path}")

        host = os.getenv("OLLAMA_HOST", DEFAULT_HOST)
        model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)

        print(f"[INFO] lesson : {section_number}")
        print(f"[INFO] model  : {model}")
        print(f"[INFO] ollama : {host}")

        check_ollama(host, model)

        data["script_generation_status"] = "running"
        data.pop("script_generation_error", None)
        save_json(json_path, data)

        master = prompt_path.read_text(encoding="utf-8")
        lesson = lesson_path.read_text(encoding="utf-8")
        prompt = build_prompt(master, section_number, lesson_path, lesson)

        script = None
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"[INFO] generation {attempt}/{MAX_RETRIES}")
                raw = call_ollama(host, model, prompt)
                script = parse_model_json(raw)
                validate_script(script, section_number)
                break
            except Exception as e:
                last_error = e
                print(f"[WARNING] {e}", file=sys.stderr)
                if attempt < MAX_RETRIES:
                    time.sleep(3)

        if script is None:
            raise RuntimeError(
                f"Generation failed after {MAX_RETRIES} attempts: {last_error}"
            )

        script.setdefault("prompt_version", prompt_path.stem)
        script["generation"] = {
            "provider": "ollama",
            "model": model,
            "host": host,
            "prompt_file": str(prompt_path),
        }

        output_dir = resolve_path(
            str(data.get("script_output_dir", DEFAULT_OUTPUT)),
            json_path,
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        script_path = output_dir / f"{section_number}.json"
        script_path.write_text(
            json.dumps(script, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        data["script_generation_status"] = "completed"
        data["script_path"] = str(script_path)
        save_json(json_path, data)

        print(f"[DONE] {section_number}")
        print(f"       script: {script_path}")
        return 0

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        try:
            data = load_json(json_path)
            data["script_generation_status"] = "failed"
            data["script_generation_error"] = str(e)
            save_json(json_path, data)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
