#!/usr/bin/env python3
"""
Generate learning content with Ollama + Muse Glimmer using low reasoning.

IMPORTANT:
    think="low" DOES NOT disable reasoning.
    Muse Glimmer still reasons, but uses its lower reasoning level.

The script:
    - streams Ollama output
    - keeps thinking separate from final content
    - saves ONLY the final response to .md
    - sends num_ctx / num_predict correctly through Ollama options
    - prints input, thinking, output and total token statistics
    - detects done_reason="length"
    - retries length-truncated generations with a larger num_predict
    - never marks a truncated generation as completed
    - preserves truncated content as .partial.md

Example:
    python generate_content_stream_low_thinking.py \
        --model muse-glimmer \
        --section 10.1.13

Default:
    think          = low
    num_ctx        = 16384
    num_predict    = 16384
    max_num_predict= 32768
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

DEFAULT_MODEL = "muse-glimmer"

# Low still means reasoning. It does NOT turn thinking off.
DEFAULT_THINK = "low"

# Context allocated to this request.
DEFAULT_NUM_CTX = 16384

# Maximum final-generation budget for the first attempt.
DEFAULT_NUM_PREDICT = 16384

# If done_reason=length, grow the output budget up to this value.
DEFAULT_MAX_NUM_PREDICT = 32768

DEFAULT_KEEP_ALIVE = "30m"
DEFAULT_TIMEOUT = 3600
DEFAULT_MAX_RETRIES = 2

BASE_PROMPT_FILE = "master_base_prompt.md"
LEARNING_PATH_FILE = "learning_path.json"


def slugify(value: str) -> str:
    """Convert a topic title into a filesystem-friendly name."""
    return re.sub(
        r"[^a-z0-9]+",
        "-",
        value.lower().strip(),
    ).strip("-")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Atomically save JSON so an interrupted write does not corrupt it."""
    temporary = path.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    temporary.replace(path)


def build_prompt(
    template: str,
    topic: dict[str, Any],
) -> str:
    """
    Replace the topic placeholders in master_base_prompt.md.
    """

    replacements = {
        "{{TOPIC}}": topic["topic_title"],
        "{{TOPIC_TITLE}}": topic["topic_title"],
        "{{SECTION_NUMBER}}": topic["section_number"],
        "{{PHASE_TITLE}}": topic["phase_title"],
        "{{SECTION_TITLE}}": topic["section_title"],
    }

    prompt = template

    for placeholder, value in replacements.items():
        prompt = prompt.replace(
            placeholder,
            value,
        )

    if prompt == template:
        raise ValueError(
            "No topic placeholder was found in master_base_prompt.md"
        )

    return prompt


def stream_ollama(
    model: str,
    prompt: str,
    think: str,
    num_ctx: int,
    num_predict: int,
    keep_alive: str,
    timeout: int,
) -> tuple[str, str, dict[str, Any]]:
    """
    Generate one response from Ollama.

    Returns:
        final_response
        thinking_text
        final_ollama_metadata

    Ollama streaming chunks can contain:

        thinking -> model reasoning
        response -> final answer

    We keep them separate.

    The reasoning is NEVER written into the learning material.
    """

    request_payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,

        # Muse Glimmer reasoning level.
        # "low" still uses reasoning.
        "think": think,

        "keep_alive": keep_alive,

        # Ollama generation options belong here.
        "options": {
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
    }

    response = requests.post(
        OLLAMA_URL,
        json=request_payload,
        stream=True,
        timeout=timeout,
    )

    response.raise_for_status()

    answer_chunks: list[str] = []
    thinking_chunks: list[str] = []
    final_metadata: dict[str, Any] = {}

    try:
        for raw_line in response.iter_lines(
            decode_unicode=True
        ):
            if not raw_line:
                continue

            payload = json.loads(raw_line)

            if payload.get("error"):
                raise RuntimeError(
                    payload["error"]
                )

            thinking = payload.get(
                "thinking",
                "",
            )

            answer = payload.get(
                "response",
                "",
            )

            if thinking:
                thinking_chunks.append(
                    thinking
                )

            if answer:
                answer_chunks.append(
                    answer
                )

            # Keep console output compact during long generations.
            if thinking or answer:
                print(
                    ".",
                    end="",
                    flush=True,
                )

            if payload.get("done"):
                final_metadata = payload
                break

    finally:
        response.close()

    print()

    final_response = "".join(
        answer_chunks
    ).strip()

    thinking_text = "".join(
        thinking_chunks
    ).strip()

    if not final_response:
        raise RuntimeError(
            "Ollama returned an empty final response."
        )

    return (
        final_response,
        thinking_text,
        final_metadata,
    )


def get_output_path(
    root: Path,
    topic: dict[str, Any],
) -> Path:
    folder = root / topic["folder"]

    filename = (
        f"{topic['section_number'].replace('.', '-')}-"
        f"{slugify(topic['topic_title'])}.md"
    )

    return folder / filename


def save_partial(
    output: Path,
    topic: dict[str, Any],
    content: str,
    reason: str,
    num_predict: int,
) -> None:
    """
    Save the visible response from an incomplete generation.

    Thinking is deliberately NOT saved.
    """

    partial = output.with_suffix(
        ".partial.md"
    )

    partial.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    partial.write_text(
        f"# PARTIAL — {topic['topic_title']}\n\n"
        f"> Reason: {reason}\n"
        f"> num_predict: {num_predict}\n\n"
        f"{content}\n",
        encoding="utf-8",
    )


def save_completed(
    output: Path,
    topic: dict[str, Any],
    content: str,
) -> None:
    """Atomically write the completed lesson."""

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = (
        f"# {topic['topic_title']}\n\n"
        f"> **Learning Path:** "
        f"{topic['phase_title']}\n"
        f"> **Section:** "
        f"{topic['section_number']} — "
        f"{topic['section_title']}\n\n"
        f"{content.strip()}\n"
    )

    temporary = output.with_suffix(
        ".tmp.md"
    )

    temporary.write_text(
        document,
        encoding="utf-8",
    )

    temporary.replace(output)


def select_topics(
    topics: list[dict[str, Any]],
    status: str | None,
    section: str | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    selected = topics

    if status:
        selected = [
            topic
            for topic in selected
            if topic["status"] == status
        ]

    if section:
        selected = [
            topic
            for topic in selected
            if topic["section_number"] == section
        ]

    if limit:
        selected = selected[:limit]

    return selected


def next_num_predict(
    current: int,
    maximum: int,
) -> int:
    """
    Increase output budget for a length-truncated retry.

    Example:

        16384 -> 24576 -> 32768
    """

    if current >= maximum:
        return current

    increased = int(
        current * 1.5
    )

    # Round to 1024-token boundary.
    increased = (
        (increased + 1023) // 1024
    ) * 1024

    return min(
        increased,
        maximum,
    )


def print_generation_stats(
    metadata: dict[str, Any],
    answer: str,
    thinking: str,
    num_ctx: int,
    num_predict: int,
) -> None:
    """
    Print the real token statistics returned by Ollama.

    Note:
        eval_count is Ollama's generated-token count and can include
        reasoning tokens when thinking is enabled.
    """

    input_tokens = metadata.get(
        "prompt_eval_count"
    )

    generated_tokens = metadata.get(
        "eval_count"
    )

    done_reason = metadata.get(
        "done_reason"
    )

    print()
    print("  --- Generation stats ---")
    print(
        f"  Context limit     : {num_ctx}"
    )
    print(
        f"  num_predict       : {num_predict}"
    )
    print(
        f"  Input tokens      : "
        f"{input_tokens if input_tokens is not None else '?'}"
    )
    print(
        f"  Generated tokens  : "
        f"{generated_tokens if generated_tokens is not None else '?'}"
    )
    print(
        f"  Thinking chars    : "
        f"{len(thinking):,}"
    )
    print(
        f"  Final answer chars: "
        f"{len(answer):,}"
    )
    print(
        f"  Done reason       : "
        f"{done_reason or '?'}"
    )

    if (
        input_tokens is not None
        and generated_tokens is not None
    ):
        print(
            f"  Input + generated : "
            f"{input_tokens + generated_tokens:,}"
        )

    if metadata.get(
        "total_duration"
    ):
        print(
            f"  Total duration    : "
            f"{metadata['total_duration'] / 1e9:.1f}s"
        )

    if (
        metadata.get("eval_duration")
        and generated_tokens
    ):
        generation_seconds = (
            metadata["eval_duration"]
            / 1_000_000_000
        )

        if generation_seconds > 0:
            speed = (
                generated_tokens
                / generation_seconds
            )

            print(
                f"  Generation speed  : "
                f"{speed:.2f} tok/s"
            )

    print(
        "  ------------------------"
    )


def update_metadata(
    topic: dict[str, Any],
    metadata: dict[str, Any],
    thinking: str,
    answer: str,
    num_ctx: int,
    num_predict: int,
    think: str,
) -> None:
    """Save diagnostics, but never save the reasoning text itself."""

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

    topic["think"] = think
    topic["num_ctx"] = num_ctx
    topic["num_predict_used"] = num_predict

    topic["thinking_chars"] = len(
        thinking
    )

    topic["visible_response_chars"] = len(
        answer
    )


def generate_topic(
    root: Path,
    path_file: Path,
    learning_path: dict[str, Any],
    topic: dict[str, Any],
    template: str,
    model: str,
    think: str,
    num_ctx: int,
    starting_num_predict: int,
    maximum_num_predict: int,
    keep_alive: str,
    timeout: int,
    max_retries: int,
) -> bool:
    output = get_output_path(
        root,
        topic,
    )

    prompt = build_prompt(
        template,
        topic,
    )

    num_predict = starting_num_predict
    total_attempts = max_retries + 1

    for attempt in range(
        1,
        total_attempts + 1,
    ):
        print(
            f"  Attempt {attempt}/{total_attempts} | "
            f"think={think} | "
            f"num_ctx={num_ctx} | "
            f"num_predict={num_predict}"
        )

        topic["status"] = "in_progress"
        topic["attempts"] = attempt
        topic["current_num_predict"] = (
            num_predict
        )

        save_json(
            path_file,
            learning_path,
        )

        try:
            answer, thinking, metadata = (
                stream_ollama(
                    model=model,
                    prompt=prompt,
                    think=think,
                    num_ctx=num_ctx,
                    num_predict=num_predict,
                    keep_alive=keep_alive,
                    timeout=timeout,
                )
            )

            update_metadata(
                topic=topic,
                metadata=metadata,
                thinking=thinking,
                answer=answer,
                num_ctx=num_ctx,
                num_predict=num_predict,
                think=think,
            )

            print_generation_stats(
                metadata=metadata,
                answer=answer,
                thinking=thinking,
                num_ctx=num_ctx,
                num_predict=num_predict,
            )

            # This is the authoritative Ollama signal that the
            # generation reached the output-token limit.
            if metadata.get(
                "done_reason"
            ) == "length":

                reason = (
                    "Ollama reached num_predict"
                )

                print(
                    f"  ⚠ NOT accepted: {reason}"
                )

                save_partial(
                    output=output,
                    topic=topic,
                    content=answer,
                    reason=reason,
                    num_predict=num_predict,
                )

                topic["last_error"] = reason

                save_json(
                    path_file,
                    learning_path,
                )

                if attempt < total_attempts:
                    new_limit = (
                        next_num_predict(
                            num_predict,
                            maximum_num_predict,
                        )
                    )

                    if new_limit > num_predict:
                        print(
                            "  ↻ Retrying with "
                            f"num_predict={new_limit}"
                        )

                        num_predict = new_limit

                        time.sleep(2)

                        continue

                break

            # Do not accept a structurally broken Markdown response.
            if answer.count("```") % 2 != 0:
                reason = (
                    "unclosed Markdown/code fence"
                )

                print(
                    f"  ⚠ NOT accepted: {reason}"
                )

                save_partial(
                    output=output,
                    topic=topic,
                    content=answer,
                    reason=reason,
                    num_predict=num_predict,
                )

                topic["last_error"] = reason

                save_json(
                    path_file,
                    learning_path,
                )

                if attempt < total_attempts:
                    time.sleep(2)
                    continue

                break

            # Successful final answer.
            save_completed(
                output=output,
                topic=topic,
                content=answer,
            )

            partial = output.with_suffix(
                ".partial.md"
            )

            if partial.exists():
                partial.unlink()

            topic["status"] = "completed"
            topic["output_file"] = str(
                output.relative_to(root)
            )
            topic["final_num_predict"] = (
                num_predict
            )

            topic.pop(
                "last_error",
                None,
            )

            topic.pop(
                "error",
                None,
            )

            save_json(
                path_file,
                learning_path,
            )

            print(
                "  ✓ Completed | "
                f"done_reason={metadata.get('done_reason', '?')} | "
                f"output_tokens={metadata.get('eval_count', '?')}"
            )

            return True

        except requests.RequestException as exc:
            reason = f"HTTP error: {exc}"

            print(
                f"  ⚠ {reason}",
                file=sys.stderr,
            )

            topic["last_error"] = reason

            save_json(
                path_file,
                learning_path,
            )

            if attempt < total_attempts:
                time.sleep(5)
                continue

            topic["status"] = "failed"
            topic["error"] = reason

            save_json(
                path_file,
                learning_path,
            )

            return False

        except Exception as exc:
            reason = (
                f"Generation error: {exc}"
            )

            print(
                f"  ⚠ {reason}",
                file=sys.stderr,
            )

            topic["last_error"] = reason

            save_json(
                path_file,
                learning_path,
            )

            if attempt < total_attempts:
                time.sleep(5)
                continue

            topic["status"] = "failed"
            topic["error"] = reason

            save_json(
                path_file,
                learning_path,
            )

            return False

    topic["status"] = "failed"

    topic["error"] = (
        f"Incomplete after {total_attempts} attempts; "
        f"maximum num_predict={maximum_num_predict}"
    )

    save_json(
        path_file,
        learning_path,
    )

    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate learning content using "
            "Muse Glimmer with low reasoning."
        )
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--think",
        choices=(
            "low",
            "medium",
            "high",
            "xhigh",
        ),
        default=DEFAULT_THINK,
        help=(
            "Muse Glimmer reasoning level. "
            "Default: low"
        ),
    )

    parser.add_argument(
        "--num-ctx",
        type=int,
        default=DEFAULT_NUM_CTX,
        help=(
            f"Ollama context size. "
            f"Default: {DEFAULT_NUM_CTX}"
        ),
    )

    parser.add_argument(
        "--num-predict",
        type=int,
        default=DEFAULT_NUM_PREDICT,
        help=(
            f"Starting output-token limit. "
            f"Default: {DEFAULT_NUM_PREDICT}"
        ),
    )

    parser.add_argument(
        "--max-num-predict",
        type=int,
        default=DEFAULT_MAX_NUM_PREDICT,
        help=(
            f"Maximum retry output-token limit. "
            f"Default: {DEFAULT_MAX_NUM_PREDICT}"
        ),
    )

    parser.add_argument(
        "--keep-alive",
        default=DEFAULT_KEEP_ALIVE,
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
    )

    parser.add_argument(
        "--status",
        default="pending",
    )

    parser.add_argument(
        "--section",
    )

    parser.add_argument(
        "--limit",
        type=int,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    args = parser.parse_args()

    if args.num_ctx <= 0:
        parser.error(
            "--num-ctx must be greater than 0"
        )

    if args.num_predict <= 0:
        parser.error(
            "--num-predict must be greater than 0"
        )

    if (
        args.max_num_predict
        < args.num_predict
    ):
        parser.error(
            "--max-num-predict must be "
            ">= --num-predict"
        )

    root = Path(__file__).resolve().parent

    path_file = (
        root / LEARNING_PATH_FILE
    )

    prompt_file = (
        root / BASE_PROMPT_FILE
    )

    if not path_file.exists():
        print(
            f"Missing: {path_file}",
            file=sys.stderr,
        )
        return 1

    if not prompt_file.exists():
        print(
            f"Missing: {prompt_file}",
            file=sys.stderr,
        )
        return 1

    learning_path = load_json(
        path_file
    )

    template = prompt_file.read_text(
        encoding="utf-8"
    )

    topics = select_topics(
        learning_path["topics"],
        args.status,
        args.section,
        args.limit,
    )

    if not topics:
        print(
            "No matching topics found."
        )
        return 0

    print(
        "========================================"
    )
    print(
        " Muse Glimmer Learning Content Generator"
    )
    print(
        "========================================"
    )
    print(
        f"Topics            : {len(topics)}"
    )
    print(
        f"Model             : {args.model}"
    )
    print(
        f"Thinking          : {args.think}"
    )
    print(
        f"Context            : {args.num_ctx}"
    )
    print(
        f"num_predict       : {args.num_predict}"
    )
    print(
        f"max_num_predict   : {args.max_num_predict}"
    )
    print(
        f"keep_alive        : {args.keep_alive}"
    )
    print(
        f"timeout           : {args.timeout}s"
    )
    print(
        f"max_retries       : {args.max_retries}"
    )
    print(
        "stream            : True"
    )
    print(
        "========================================"
    )

    completed = 0
    failed = 0

    for topic in topics:
        print(
            f"\n[{topic['section_number']}] "
            f"{topic['topic_title']}"
        )

        if args.dry_run:
            print(
                "\n--- PROMPT ---"
            )
            print(
                build_prompt(
                    template,
                    topic,
                )
            )
            print(
                "--- END PROMPT ---"
            )
            continue

        if topic.get(
            "status"
        ) == "completed":
            print(
                "  ↷ Already completed; skipping."
            )
            continue

        success = generate_topic(
            root=root,
            path_file=path_file,
            learning_path=learning_path,
            topic=topic,
            template=template,
            model=args.model,
            think=args.think,
            num_ctx=args.num_ctx,
            starting_num_predict=(
                args.num_predict
            ),
            maximum_num_predict=(
                args.max_num_predict
            ),
            keep_alive=args.keep_alive,
            timeout=args.timeout,
            max_retries=args.max_retries,
        )

        if success:
            completed += 1
        else:
            failed += 1

    print(
        "\n========================================"
    )
    print(
        f"Completed={completed} Failed={failed}"
    )
    print(
        "========================================"
    )

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
