#!/usr/bin/env python3
"""Stream learning content from a local Ollama model safely."""
from __future__ import annotations
import argparse, json, re, sys, time
from pathlib import Path
from typing import Any
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3:12b"
DEFAULT_NUM_PREDICT = 8192
DEFAULT_KEEP_ALIVE = "30m"
DEFAULT_TIMEOUT = 3600
DEFAULT_MAX_RETRIES = 2
BASE_PROMPT_FILE = "master_base_prompt.md"
LEARNING_PATH_FILE = "learning_path.json"

def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower().strip()).strip("-")

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

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
    for key, value in replacements.items():
        prompt = prompt.replace(key, value)
    if prompt == template:
        raise ValueError("No topic placeholder found in master_base_prompt.md.")
    return prompt

def basic_completeness_check(text: str, done_reason: str | None) -> tuple[bool, str]:
    if not text.strip():
        return True, "empty response"
    if done_reason == "length":
        return True, "Ollama reported done_reason=length"
    if text.count("```") % 2 != 0:
        return True, "unclosed Markdown/code fence"
    # Deliberately do not guess whether Tamil prose is grammatically complete.
    return False, ""

def stream_ollama(model: str, prompt: str, num_predict: int, keep_alive: str, timeout: int):
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
        raise RuntimeError("Ollama returned an empty response.")
    return content, final_payload

def output_path(root: Path, topic: dict[str, Any]) -> Path:
    return root / topic["folder"] / (
        f"{topic['section_number'].replace('.', '-')}-"
        f"{slugify(topic['topic_title'])}.md"
    )

def save_partial(path: Path, topic: dict[str, Any], content: str, reason: str) -> None:
    partial = path.with_suffix(".partial.md")
    partial.parent.mkdir(parents=True, exist_ok=True)
    partial.write_text(
        f"# PARTIAL — {topic['topic_title']}\n\n"
        f"> Generation was not accepted as complete.\n"
        f"> Reason: {reason}\n\n{content}\n",
        encoding="utf-8",
    )

def save_completed(path: Path, topic: dict[str, Any], content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = (
        f"# {topic['topic_title']}\n\n"
        f"> **Learning Path:** {topic['phase_title']}\n"
        f"> **Section:** {topic['section_number']} — {topic['section_title']}\n\n"
        f"{content.strip()}\n"
    )
    tmp = path.with_suffix(".tmp.md")
    tmp.write_text(document, encoding="utf-8")
    tmp.replace(path)

def update_metadata(topic: dict[str, Any], metadata: dict[str, Any]) -> None:
    for key in ("done_reason", "eval_count", "eval_duration", "prompt_eval_count",
                "prompt_eval_duration", "total_duration", "load_duration"):
        if key in metadata:
            topic[key] = metadata[key]

def select_topics(topics, status, section, limit):
    selected = [t for t in topics if not status or t["status"] == status]
    if section:
        selected = [t for t in selected if t["section_number"] == section]
    return selected[:limit] if limit else selected

def generate_topic(root, path_file, learning_path, topic, template, args) -> bool:
    path = output_path(root, topic)
    prompt = build_prompt(template, topic)
    attempts = args.max_retries + 1
    for attempt in range(1, attempts + 1):
        print(f"  Attempt {attempt}/{attempts} | num_predict={args.num_predict}")
        topic["status"] = "in_progress"
        topic["attempts"] = attempt
        save_json(path_file, learning_path)
        try:
            content, metadata = stream_ollama(
                args.model, prompt, args.num_predict, args.keep_alive, args.timeout
            )
            update_metadata(topic, metadata)
            incomplete, reason = basic_completeness_check(content, metadata.get("done_reason"))
            if incomplete:
                print(f"  ⚠ NOT accepted: {reason}")
                save_partial(path, topic, content, reason)
                topic["last_error"] = reason
                save_json(path_file, learning_path)
                if attempt < attempts:
                    time.sleep(2)
                    continue
                topic["status"] = "failed"
                topic["error"] = f"Incomplete generation after {attempts} attempts: {reason}"
                save_json(path_file, learning_path)
                return False
            save_completed(path, topic, content)
            partial = path.with_suffix(".partial.md")
            if partial.exists():
                partial.unlink()
            topic["status"] = "completed"
            topic["output_file"] = str(path.relative_to(root))
            topic.pop("last_error", None)
            topic.pop("error", None)
            save_json(path_file, learning_path)
            print(f"  ✓ Completed | done_reason={metadata.get('done_reason', '?')} | output_tokens={metadata.get('eval_count', '?')}")
            return True
        except requests.RequestException as exc:
            reason = f"HTTP error: {exc}"
        except Exception as exc:
            reason = f"Generation error: {exc}"
        print(f"  ⚠ {reason}", file=sys.stderr)
        topic["last_error"] = reason
        save_json(path_file, learning_path)
        if attempt < attempts:
            time.sleep(5)
            continue
        topic["status"] = "failed"
        topic["error"] = reason
        save_json(path_file, learning_path)
        return False
    return False

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--status", default="pending")
    parser.add_argument("--section")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--num-predict", type=int, default=DEFAULT_NUM_PREDICT)
    parser.add_argument("--keep-alive", default=DEFAULT_KEEP_ALIVE)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    path_file = root / LEARNING_PATH_FILE
    prompt_file = root / BASE_PROMPT_FILE
    if not path_file.exists() or not prompt_file.exists():
        print("Missing learning_path.json or master_base_prompt.md", file=sys.stderr)
        return 1
    learning_path = load_json(path_file)
    template = prompt_file.read_text(encoding="utf-8")
    topics = select_topics(learning_path["topics"], args.status, args.section, args.limit)
    if not topics:
        print("No matching topics found.")
        return 0
    print(f"Topics={len(topics)} Model={args.model} num_predict={args.num_predict} keep_alive={args.keep_alive} timeout={args.timeout}s retries={args.max_retries}")
    completed = failed = 0
    for topic in topics:
        print(f"\n[{topic['section_number']}] {topic['topic_title']}")
        if args.dry_run:
            print(build_prompt(template, topic))
            continue
        if topic.get("status") == "completed":
            print("  ↷ Already completed; skipping.")
            continue
        if generate_topic(root, path_file, learning_path, topic, template, args):
            completed += 1
        else:
            failed += 1
    print(f"\nCompleted: {completed}\nFailed: {failed}")
    return 0 if failed == 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
