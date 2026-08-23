#!/usr/bin/env python3
"""
generate_video_script.py

Reads a single source-of-truth JSON file, generates a short-video script
from the referenced canonical learning content, saves the script under
script_outputs/, and updates the same JSON with:

    script_generation_status
    script_path

Expected JSON shape (minimum):

{
  "lesson_id": "AI-RAG-001",
  "lesson_path": "learning/ai/rag/01-why-rag/lesson.md",
  "script_generation_status": "pending",
  "script_path": "",
  "video_generation_status": "pending",
  "video_path": ""
}

Environment:
    OPENAI_API_KEY=<required>

Optional:
    OPENAI_SCRIPT_MODEL=gpt-5.6
    SCRIPT_OUTPUT_DIR=script_outputs

Usage:
    python generate_video_script.py path/to/lesson.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    print("Missing dependency: openai")
    print("Install with: pip install openai")
    sys.exit(1)


VIDEO_PROMPT = r"""
You are the Learn by Reasoning Short Video Master Prompt.

The supplied learning content is the canonical source of truth.

Create a short educational video plan from this lesson.

Core philosophy:
- One video = one powerful reasoning insight.
- Do not compress the whole lesson into one video.
- Start with a problem, not a definition.
- Create curiosity.
- Explain the reasoning.
- Let the technology/pattern emerge from the reasoning.
- Show the important trade-off.
- End with a reusable mental model.
- The learner should think: "Oh! That's why."
- Do not create generic tutorial narration.
- Do not invent technical facts that are not supported by the source content.
- Preserve established English technical terminology.
- If the source language is Tamil, use natural spoken Tamil (Pechu Tamil), not literary Tamil.
- Technical words such as RAG, Cache, Cache Aside, Embedding, Vector Database,
  Agent, Memory, Kubernetes, Kafka, Latency, Consistency, etc. must remain in English.
- Mermaid is a first-class visual learning medium.
- Use Mermaid when it improves reasoning: flow, sequence, architecture,
  decisions, state transitions, cause/effect, or trade-offs.
- Prefer progressive diagrams rather than one giant architecture diagram.
- Keep the video concise and speakable.

Return ONLY valid JSON matching this schema:

{
  "lesson_id": "string",
  "video_title": "string",
  "thumbnail_text": "string",
  "core_insight": "string",
  "video_type": "why|how|when|what_if|failure|tradeoff",
  "language": "en|ta",
  "duration_target_seconds": 60,
  "scenes": [
    {
      "scene_id": "scene-01",
      "start_seconds": 0,
      "end_seconds": 6,
      "voice": "spoken narration",
      "visual": "specific visual direction",
      "on_screen_text": "short text",
      "mermaid": "optional Mermaid code without markdown fences"
    }
  ],
  "mental_model": "one concise reusable principle",
  "final_takeaway": "one concise takeaway",
  "visual_assets": [
    "asset description"
  ],
  "source_mapping": [
    "source section/concept used"
  ],
  "related_video_ideas": [
    "future video idea"
  ]
}

Rules:
- Do not use markdown fences around the JSON.
- Do not put the entire lesson into the video.
- Select the strongest single reasoning moment.
- Generate a natural spoken script, not an article.
- Every scene must have a clear visual purpose.
"""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Input JSON must contain a JSON object.")
    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def resolve_source_path(input_json: Path, data: dict[str, Any]) -> Path:
    # Keep this flexible so the existing JSON can use one of these names.
    raw = (
        data.get("lesson_path")
        or data.get("source_path")
        or data.get("content_path")
        or data.get("learning_content_path")
    )
    if not raw:
        raise ValueError(
            "JSON must contain one of: lesson_path, source_path, "
            "content_path, learning_content_path"
        )

    source = Path(raw)
    if not source.is_absolute():
        source = input_json.parent / source
        if not source.exists():
            # Also try relative to the current working directory.
            source = Path(raw)

    if not source.exists():
        raise FileNotFoundError(f"Learning content not found: {source}")

    return source.resolve()


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    # Handle accidental markdown fences gracefully.
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError("Model output is not a JSON object.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()

    input_json = args.json_file.resolve()

    try:
        data = load_json(input_json)

        lesson_id = data.get("lesson_id")
        if not lesson_id:
            raise ValueError("JSON is missing required field: lesson_id")

        # Do not overwrite an already completed script unless explicitly reset.
        if data.get("script_generation_status") == "completed":
            print(f"[SKIP] {lesson_id}: script_generation_status is already completed.")
            return 0

        data["script_generation_status"] = "running"
        save_json(input_json, data)

        source_path = resolve_source_path(input_json, data)
        source_content = source_path.read_text(encoding="utf-8")

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.getenv("OPENAI_SCRIPT_MODEL", "gpt-5.6")

        prompt = (
            VIDEO_PROMPT
            + "\n\n"
            + f"lesson_id: {lesson_id}\n"
            + f"canonical_source_path: {source_path}\n\n"
            + "CANONICAL LEARNING CONTENT:\n"
            + "============================\n"
            + source_content
        )

        response = client.responses.create(
            model=model,
            input=prompt,
        )

        script = extract_json(response.output_text)

        if script.get("lesson_id") != lesson_id:
            raise ValueError(
                f"Generated lesson_id mismatch: "
                f"{script.get('lesson_id')} != {lesson_id}"
            )

        output_root = Path(
            os.getenv("SCRIPT_OUTPUT_DIR", input_json.parent / "script_outputs")
        )
        if not output_root.is_absolute():
            output_root = input_json.parent / output_root

        output_root.mkdir(parents=True, exist_ok=True)

        # Keep the artifact name deterministic and based on the canonical lesson_id.
        script_path = output_root / f"{lesson_id}.json"
        script_path.write_text(
            json.dumps(script, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        data["script_generation_status"] = "completed"
        data["script_path"] = str(script_path)
        save_json(input_json, data)

        print(f"[DONE] {lesson_id}")
        print(f"       script: {script_path}")
        return 0

    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)

        # Best effort: preserve failure in the same source-of-truth JSON.
        try:
            data = load_json(input_json)
            data["script_generation_status"] = "failed"
            data["script_generation_error"] = str(exc)
            save_json(input_json, data)
        except Exception:
            pass

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
