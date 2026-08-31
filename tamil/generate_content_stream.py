#!/usr/bin/env python3
"""Streaming Ollama learning-content generator.

Length handling:
  --num-predict is the starting output-token limit.
  If Ollama returns done_reason=length, the next attempt increases the limit
  by 50%, up to --max-num-predict.

Example:
  python generate_content_stream.py --model muse-glimmer --num-predict 16384
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3:12b"
DEFAULT_NUM_PREDICT = 16384
DEFAULT_MAX_NUM_PREDICT = 32768
DEFAULT_KEEP_ALIVE = "30m"
DEFAULT_TIMEOUT = 3600
DEFAULT_MAX_RETRIES = 2
BASE_PROMPT_FILE = "master_base_prompt.md"
LEARNING_PATH_FILE = "learning_path.json"


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower().strip()).strip("-")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
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
    if prompt == template:
        raise ValueError("No topic placeholder found in master_base_prompt.md")
    return prompt


def stream_ollama(
    model: str,
    prompt: str,
    num_predict: int,
    keep_alive: str,
    timeout: int,
) -> tuple[str, dict[str, Any]]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": True,
            "num_predict": num_predict,
            "keep_alive": keep_alive,
        },
        stream=True,
        timeout=timeout,
    )
    response.raise_for_status()

    chunks: list[str] = []
    final_payload: dict[str, Any] = {}

    try:
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            payload = json.loads(raw_line)
            if payload.get("error"):
                raise RuntimeError(payload["error"])

            chunk = payload.get("response", "")
            if chunk:
                chunks.append(chunk)
                print(".", end="", flush=True)

            if payload.get("done"):
                final_payload = payload
                break
    finally:
        response.close()

    print()
    content = "".join(chunks).strip()
    if not content:
        raise RuntimeError("Ollama returned an empty response")
    return content, final_payload


def output_path(root: Path, topic: dict[str, Any]) -> Path:
    folder = root / topic["folder"]
    filename = (
        f"{topic['section_number'].replace('.', '-')}-"
        f"{slugify(topic['topic_title'])}.md"
    )
    return folder / filename


def save_partial(output: Path, topic: dict[str, Any], content: str, reason: str, limit: int) -> None:
    partial = output.with_suffix(".partial.md")
    partial.parent.mkdir(parents=True, exist_ok=True)
    partial.write_text(
        f"# PARTIAL — {topic['topic_title']}\n\n"
        f"> Reason: {reason}\n"
        f"> num_predict: {limit}\n\n"
        f"{content}\n",
        encoding="utf-8",
    )


def save_completed(output: Path, topic: dict[str, Any], content: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    document = (
        f"# {topic['topic_title']}\n\n"
        f"> **Learning Path:** {topic['phase_title']}\n"
        f"> **Section:** {topic['section_number']} — {topic['section_title']}\n\n"
        f"{content.strip()}\n"
    )
    tmp = output.with_suffix(".tmp.md")
    tmp.write_text(document, encoding="utf-8")
    tmp.replace(output)


def next_limit(current: int, maximum: int) -> int:
    if current >= maximum:
        return current
    increased = int(current * 1.5)
    increased = ((increased + 1023) // 1024) * 1024
    return min(increased, maximum)


def select_topics(topics, status, section, limit):
    selected = topics
    if status:
        selected = [t for t in selected if t["status"] == status]
    if section:
        selected = [t for t in selected if t["section_number"] == section]
    if limit:
        selected = selected[:limit]
    return selected


def update_metadata(topic: dict[str, Any], metadata: dict[str, Any]) -> None:
    for key in (
        "done_reason",
        "eval_count",
        "eval_duration",
        "prompt_eval_count",
        "prompt_eval_duration",
        "total_duration",
        "load_duration",
    ):
        if key in metadata:
            topic[key] = metadata[key]


def generate_topic(
    root: Path,
    path_file: Path,
    learning_path: dict[str, Any],
    topic: dict[str, Any],
    template: str,
    model: str,
    starting_limit: int,
    maximum_limit: int,
    keep_alive: str,
    timeout: int,
    max_retries: int,
) -> bool:
    output = output_path(root, topic)
    prompt = build_prompt(template, topic)
    limit = starting_limit
    total_attempts = max_retries + 1

    for attempt in range(1, total_attempts + 1):
        print(f"  Attempt {attempt}/{total_attempts} | num_predict={limit}")
        topic["status"] = "in_progress"
        topic["attempts"] = attempt
        topic["current_num_predict"] = limit
        save_json(path_file, learning_path)

        try:
            content, metadata = stream_ollama(
                model=model,
                prompt=prompt,
                num_predict=limit,
                keep_alive=keep_alive,
                timeout=timeout,
            )
            update_metadata(topic, metadata)

            done_reason = metadata.get("done_reason")

            # This is the strongest reliable signal that output was truncated.
            if done_reason == "length":
                reason = "Ollama reached num_predict"
                print(f"  ⚠ NOT accepted: {reason}")
                save_partial(output, topic, content, reason, limit)
                topic["last_error"] = reason
                save_json(path_file, learning_path)

                if attempt < total_attempts:
                    new_limit = next_limit(limit, maximum_limit)
                    if new_limit > limit:
                        print(f"  ↻ Retrying with num_predict={new_limit}")
                        limit = new_limit
                        time.sleep(2)
                        continue
                break

            # Don't accept structurally broken Markdown/Mermaid.
            if content.count("```") % 2 != 0:
                reason = "unclosed Markdown/code fence"
                print(f"  ⚠ NOT accepted: {reason}")
                save_partial(output, topic, content, reason, limit)
                topic["last_error"] = reason
                save_json(path_file, learning_path)
                if attempt < total_attempts:
                    time.sleep(2)
                    continue
                break

            save_completed(output, topic, content)
            partial = output.with_suffix(".partial.md")
            if partial.exists():
                partial.unlink()

            topic["status"] = "completed"
            topic["output_file"] = str(output.relative_to(root))
            topic["final_num_predict"] = limit
            topic.pop("last_error", None)
            topic.pop("error", None)
            save_json(path_file, learning_path)

            print(
                f"  ✓ Completed | done_reason={done_reason or '?'} "
                f"| output_tokens={metadata.get('eval_count', '?')}"
            )
            return True

        except requests.RequestException as exc:
            reason = f"HTTP error: {exc}"
            print(f"  ⚠ {reason}", file=sys.stderr)
            topic["last_error"] = reason
            save_json(path_file, learning_path)
            if attempt < total_attempts:
                time.sleep(5)
                continue
            topic["status"] = "failed"
            topic["error"] = reason
            save_json(path_file, learning_path)
            return False

        except Exception as exc:
            reason = f"Generation error: {exc}"
            print(f"  ⚠ {reason}", file=sys.stderr)
            topic["last_error"] = reason
            save_json(path_file, learning_path)
            if attempt < total_attempts:
                time.sleep(5)
                continue
            topic["status"] = "failed"
            topic["error"] = reason
            save_json(path_file, learning_path)
            return False

    topic["status"] = "failed"
    topic["error"] = (
        f"Incomplete after {total_attempts} attempts; "
        f"maximum num_predict={maximum_limit}"
    )
    save_json(path_file, learning_path)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--status", default="pending")
    parser.add_argument("--section")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--num-predict", type=int, default=DEFAULT_NUM_PREDICT)
    parser.add_argument("--max-num-predict", type=int, default=DEFAULT_MAX_NUM_PREDICT)
    parser.add_argument("--keep-alive", default=DEFAULT_KEEP_ALIVE)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.num_predict <= 0:
        parser.error("--num-predict must be > 0")
    if args.max_num_predict < args.num_predict:
        parser.error("--max-num-predict must be >= --num-predict")

    root = Path(__file__).resolve().parent
    path_file = root / LEARNING_PATH_FILE
    prompt_file = root / BASE_PROMPT_FILE

    if not path_file.exists():
        print(f"Missing: {path_file}", file=sys.stderr)
        return 1
    if not prompt_file.exists():
        print(f"Missing: {prompt_file}", file=sys.stderr)
        return 1

    learning_path = load_json(path_file)
    template = prompt_file.read_text(encoding="utf-8")
    topics = select_topics(
        learning_path["topics"], args.status, args.section, args.limit
    )

    if not topics:
        print("No matching topics found.")
        return 0

    print(
        f"Topics={len(topics)} Model={args.model} "
        f"num_predict={args.num_predict} "
        f"max_num_predict={args.max_num_predict} "
        f"keep_alive={args.keep_alive} "
        f"timeout={args.timeout}s retries={args.max_retries}"
    )

    completed = failed = 0

    for topic in topics:
        print(f"\n[{topic['section_number']}] {topic['topic_title']}")

        if args.dry_run:
            print(build_prompt(template, topic))
            continue

        if topic.get("status") == "completed":
            print("  ↷ Already completed; skipping.")
            continue

        if generate_topic(
            root=root,
            path_file=path_file,
            learning_path=learning_path,
            topic=topic,
            template=template,
            model=args.model,
            starting_limit=args.num_predict,
            maximum_limit=args.max_num_predict,
            keep_alive=args.keep_alive,
            timeout=args.timeout,
            max_retries=args.max_retries,
        ):
            completed += 1
        else:
            failed += 1

    print(f"\nCompleted={completed} Failed={failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
