#!/usr/bin/env python3
"""
generate_video_from_script.py

Batch video generator for the Learn by Reasoning learning-path JSON.

The MASTER LEARNING-PATH JSON is the SINGLE SOURCE OF TRUTH.

Flow:

    learning_path.json
            |
            v
         topics[]
            |
            +-- status == completed
            |
            +-- script_generation_status == completed
            |
            +-- video_generation_status != completed
                         |
                         v
                    script_path
                         |
                         v
                 generated video
                         |
                         v
                  video_outputs/
                         |
                         v
                 update SAME JSON

This implementation is intentionally modular.

Current rendering pipeline:
    script JSON
       -> scene narration
       -> optional TTS
       -> scene visual cards
       -> FFmpeg
       -> MP4

It is designed so that the visual renderer can later be replaced with:
    - Mermaid rendering
    - generated images
    - animations
    - code animations
    - AI video generation
    - custom templates

No OpenAI dependency is used.

Default TTS:
    Ollama does NOT provide standard speech synthesis through /api/generate.
    Therefore this script supports a configurable local TTS command.

By default, it creates a video using scene cards WITHOUT TTS.

For TTS, set:
    TTS_COMMAND

The command receives:
    {text}
    {output}

Example:
    TTS_COMMAND=...

Required:
    pip install pillow

Also required:
    ffmpeg
    ffprobe

Usage:
    python generate_video_from_script.py path/to/learning_path.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


DEFAULT_OUTPUT_DIR = "video_outputs"

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

DEFAULT_SCENE_SECONDS = 6

# Optional local TTS command.
#
# The command must contain:
#     {text}
#     {output}
#
# Example concept:
#     TTS_COMMAND=my_tts.py --text "{text}" --output "{output}"
#
TTS_COMMAND = os.getenv("TTS_COMMAND", "").strip()


# ============================================================
# JSON
# ============================================================

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Learning-path JSON must contain an object.")

    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")

    with temp.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")

    temp.replace(path)


# ============================================================
# Paths
# ============================================================

def resolve_path(value: str, json_path: Path) -> Path:
    path = Path(value)

    if path.is_absolute():
        return path

    candidate = json_path.parent / path

    if candidate.exists():
        return candidate

    return Path.cwd() / path


def topic_identity(topic: dict[str, Any], index: int) -> str:
    return str(
        topic.get("lesson_id")
        or topic.get("topic_id")
        or topic.get("topic_title")
        or f"topic-{index:04d}"
    )


# ============================================================
# External tools
# ============================================================

def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg was not found on PATH."
        )

    if shutil.which("ffprobe") is None:
        raise RuntimeError(
            "ffprobe was not found on PATH."
        )


# ============================================================
# Fonts
# ============================================================

def load_font(size: int, bold: bool = False):
    candidates = []

    if os.name == "nt":
        candidates.extend(
            [
                "C:/Windows/Fonts/arialbd.ttf"
                if bold
                else "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/segoeuib.ttf"
                if bold
                else "C:/Windows/Fonts/segoeui.ttf",
            ]
        )

    candidates.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(
                candidate,
                size=size,
            )

    return ImageFont.load_default()


def wrap_text(
    text: str,
    max_chars: int,
) -> list[str]:
    words = text.split()

    lines: list[str] = []
    current = ""

    for word in words:
        candidate = (
            f"{current} {word}".strip()
        )

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# ============================================================
# Scene visual
# ============================================================

def render_scene_card(
    output_path: Path,
    title: str,
    on_screen_text: str,
    visual_description: str,
    scene_index: int,
) -> None:
    """
    Temporary visual renderer.

    This intentionally produces a simple readable scene card.

    Later this function can be replaced by a real visual pipeline
    without changing the JSON orchestration.
    """

    image = Image.new(
        "RGB",
        (
            VIDEO_WIDTH,
            VIDEO_HEIGHT,
        ),
    )

    draw = ImageDraw.Draw(image)

    title_font = load_font(
        64,
        bold=True,
    )

    text_font = load_font(
        50,
        bold=True,
    )

    visual_font = load_font(
        34,
        bold=False,
    )

    scene_font = load_font(
        28,
        bold=False,
    )

    left = 120
    y = 100

    draw.text(
        (left, y),
        title,
        font=title_font,
    )

    y += 140

    if on_screen_text:
        for line in wrap_text(
            on_screen_text,
            48,
        ):
            draw.text(
                (left, y),
                line,
                font=text_font,
            )

            y += 70

    y += 60

    if visual_description:
        for line in wrap_text(
            visual_description,
            70,
        ):
            draw.text(
                (left, y),
                line,
                font=visual_font,
            )

            y += 48

    draw.text(
        (
            left,
            VIDEO_HEIGHT - 90,
        ),
        f"Scene {scene_index:02d}",
        font=scene_font,
    )

    image.save(
        output_path,
        format="PNG",
    )


# ============================================================
# Optional TTS
# ============================================================

def generate_tts(
    text: str,
    output_path: Path,
) -> bool:
    """
    Run a user-provided local TTS command.

    The command must contain {text} and {output}.

    Returns True if audio was generated.
    """

    if not TTS_COMMAND:
        return False

    command = TTS_COMMAND.format(
        text=text.replace('"', '\\"'),
        output=str(output_path),
    )

    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "TTS command failed:\n"
            + result.stderr[-4000:]
        )

    return output_path.exists()


# ============================================================
# FFmpeg
# ============================================================

def run_ffmpeg(args: list[str]) -> None:
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed:\n"
            + result.stderr[-5000:]
        )


def get_audio_duration(
    audio_path: Path,
) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "ffprobe failed:\n"
            + result.stderr
        )

    return float(
        result.stdout.strip()
    )


def create_scene_video(
    image_path: Path,
    output_path: Path,
    duration: float,
    audio_path: Path | None = None,
) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
    ]

    if audio_path and audio_path.exists():
        command.extend(
            [
                "-i",
                str(audio_path),
            ]
        )

    command.extend(
        [
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(VIDEO_FPS),
            "-t",
            f"{duration:.3f}",
            "-vf",
            (
                f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2"
            ),
        ]
    )

    if audio_path and audio_path.exists():
        command.extend(
            [
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
            ]
        )
    else:
        command.extend(
            [
                "-an",
            ]
        )

    command.append(
        str(output_path)
    )

    run_ffmpeg(command)


def concatenate_videos(
    scene_videos: list[Path],
    output_path: Path,
    temp_dir: Path,
) -> None:
    concat_file = (
        temp_dir / "concat.txt"
    )

    with concat_file.open(
        "w",
        encoding="utf-8",
    ) as f:

        for scene in scene_videos:
            escaped = (
                str(scene)
                .replace("'", "'\\''")
            )

            f.write(
                f"file '{escaped}'\n"
            )

    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(output_path),
        ]
    )


# ============================================================
# Duration
# ============================================================

def scene_duration(
    scene: dict[str, Any],
) -> float:
    start = scene.get("start_seconds")
    end = scene.get("end_seconds")

    if (
        isinstance(start, (int, float))
        and isinstance(end, (int, float))
        and end > start
    ):
        return float(end - start)

    return float(
        DEFAULT_SCENE_SECONDS
    )


# ============================================================
# Video generation
# ============================================================

def generate_one_video(
    topic: dict[str, Any],
    topic_index: int,
    json_path: Path,
    output_root: Path,
) -> str:
    identity = topic_identity(
        topic,
        topic_index,
    )

    script_value = topic.get(
        "script_path"
    )

    if not script_value:
        raise ValueError(
            f"{identity} has no script_path."
        )

    script_path = resolve_path(
        str(script_value),
        json_path,
    )

    if not script_path.exists():
        raise FileNotFoundError(
            f"Script not found for {identity}: "
            f"{script_path}"
        )

    script = json.loads(
        script_path.read_text(
            encoding="utf-8"
        )
    )

    if script.get("lesson_id") != identity:
        raise ValueError(
            f"Script identity mismatch for {identity}."
        )

    scenes = script.get("scenes")

    if not isinstance(
        scenes,
        list,
    ) or not scenes:
        raise ValueError(
            f"{identity}: script contains no scenes."
        )

    # Preserve the same topic folder structure.
    folder = str(
        topic.get("folder") or ""
    ).strip()

    output_dir = (
        output_root / Path(folder)
        if folder
        else output_root
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Keep the same artifact naming convention.
    video_name = (
        script_path.stem
        + ".mp4"
    )

    final_video = (
        output_dir / video_name
    )

    with tempfile.TemporaryDirectory(
        prefix=f"{identity}-"
    ) as temp:

        temp_dir = Path(temp)

        scene_videos: list[Path] = []

        for index, scene in enumerate(
            scenes,
            start=1,
        ):
            scene_id = scene.get(
                "scene_id",
                f"scene-{index:02d}",
            )

            image_path = (
                temp_dir
                / f"{index:03d}.png"
            )

            audio_path = (
                temp_dir
                / f"{index:03d}.wav"
            )

            scene_video = (
                temp_dir
                / f"{index:03d}.mp4"
            )

            render_scene_card(
                output_path=image_path,
                title=scene_id,
                on_screen_text=str(
                    scene.get(
                        "on_screen_text",
                        "",
                    )
                ),
                visual_description=str(
                    scene.get(
                        "visual",
                        "",
                    )
                ),
                scene_index=index,
            )

            duration = scene_duration(
                scene
            )

            generated_audio = generate_tts(
                text=str(
                    scene.get(
                        "voice",
                        "",
                    )
                ),
                output_path=audio_path,
            )

            if generated_audio:
                duration = get_audio_duration(
                    audio_path
                )

            create_scene_video(
                image_path=image_path,
                output_path=scene_video,
                duration=duration,
                audio_path=(
                    audio_path
                    if generated_audio
                    else None
                ),
            )

            scene_videos.append(
                scene_video
            )

        temporary_final = (
            temp_dir
            / f"{identity}.mp4"
        )

        concatenate_videos(
            scene_videos=scene_videos,
            output_path=temporary_final,
            temp_dir=temp_dir,
        )

        shutil.copy2(
            temporary_final,
            final_video,
        )

    try:
        return str(
            final_video.relative_to(
                json_path.parent
            )
        )
    except ValueError:
        return str(final_video)


# ============================================================
# Main
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate videos from completed video scripts "
            "using the master learning-path JSON."
        )
    )

    parser.add_argument(
        "learning_path_json",
        type=Path,
        help="Master learning-path JSON.",
    )

    args = parser.parse_args()

    json_path = (
        args.learning_path_json
        .resolve()
    )

    try:
        check_ffmpeg()

        data = load_json(
            json_path
        )

        topics = data.get(
            "topics"
        )

        if not isinstance(
            topics,
            list,
        ):
            raise ValueError(
                "Learning-path JSON must contain a topics array."
            )

        output_root = resolve_path(
            str(
                data.get(
                    "video_output_dir",
                    DEFAULT_OUTPUT_DIR,
                )
            ),
            json_path,
        )

        print(
            "=============================================="
        )
        print(
            " Learn by Reasoning - Video Generator"
        )
        print(
            "=============================================="
        )
        print(
            f"JSON   : {json_path}"
        )
        print(
            f"Output : {output_root}"
        )
        print(
            f"Topics : {len(topics)}"
        )
        print(
            f"TTS    : "
            f"{'enabled' if TTS_COMMAND else 'disabled'}"
        )
        print(
            "=============================================="
        )

        generated = 0
        skipped = 0
        failed = 0

        for index, topic in enumerate(
            topics,
            start=1,
        ):
            if not isinstance(
                topic,
                dict,
            ):
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
            # Learning content must already be complete.
            # ------------------------------------------------

            if topic.get(
                "status"
            ) != "completed":

                print(
                    "  [SKIP] learning content not completed"
                )

                skipped += 1
                continue

            # ------------------------------------------------
            # Script must already be generated.
            # ------------------------------------------------

            if topic.get(
                "script_generation_status"
            ) != "completed":

                print(
                    "  [SKIP] video script not completed"
                )

                skipped += 1
                continue

            # ------------------------------------------------
            # Video already generated.
            # ------------------------------------------------

            if topic.get(
                "video_generation_status"
            ) == "completed":

                print(
                    "  [SKIP] video already completed"
                )

                skipped += 1
                continue

            # ------------------------------------------------
            # Mark this topic as running.
            # ------------------------------------------------

            topic[
                "video_generation_status"
            ] = "in_progress"

            topic.pop(
                "video_generation_error",
                None,
            )

            save_json(
                json_path,
                data,
            )

            try:
                video_path = generate_one_video(
                    topic=topic,
                    topic_index=index,
                    json_path=json_path,
                    output_root=output_root,
                )

                # ------------------------------------------------
                # Update SAME source-of-truth JSON.
                # ------------------------------------------------

                topic[
                    "video_generation_status"
                ] = "completed"

                topic[
                    "video_path"
                ] = video_path

                save_json(
                    json_path,
                    data,
                )

                print(
                    f"  [DONE] video = {video_path}"
                )

                generated += 1

            except Exception as exc:

                topic[
                    "video_generation_status"
                ] = "failed"

                topic[
                    "video_generation_error"
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

                # Continue processing remaining topics.
                continue

        print()
        print(
            "=============================================="
        )
        print(
            "Video generation finished"
        )
        print(
            "=============================================="
        )
        print(
            f"Generated : {generated}"
        )
        print(
            f"Skipped   : {skipped}"
        )
        print(
            f"Failed    : {failed}"
        )
        print(
            "=============================================="
        )

        return 1 if failed else 0

    except Exception as exc:

        print(
            f"[FATAL] {exc}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
