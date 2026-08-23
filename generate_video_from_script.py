#!/usr/bin/env python3
"""
generate_video_from_script.py

Reads the SAME source-of-truth JSON used by generate_video_script.py.

Rules:
1. script_generation_status must be "completed".
2. video_generation_status must NOT be "completed".
3. script_path must point to an existing generated video-script JSON.
4. Generates a simple MP4 from the script.
5. Saves it under video_outputs/.
6. Updates the SAME source JSON with:
       video_generation_status
       video_path

This implementation creates a clean narrated-video foundation:
- voice-over using OpenAI TTS
- scene cards rendered with Pillow
- Mermaid/code visuals can be integrated later through the visual_assets
  pipeline.

Required:
    OPENAI_API_KEY=<required>
    ffmpeg installed and available on PATH

Optional:
    OPENAI_TTS_MODEL=gpt-4o-mini-tts
    OPENAI_TTS_VOICE=alloy
    VIDEO_OUTPUT_DIR=video_outputs

Install:
    pip install openai pillow

Usage:
    python generate_video_from_script.py path/to/lesson.json
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

try:
    from openai import OpenAI
except ImportError:
    print("Missing dependency: openai")
    print("Install with: pip install openai")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Missing dependency: pillow")
    print("Install with: pip install pillow")
    sys.exit(1)


WIDTH = 1920
HEIGHT = 1080
FPS = 30


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


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg was not found on PATH. Install ffmpeg before generating videos."
        )


def wrap_text(text: str, width: int = 55) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)

    return ImageFont.load_default()


def render_scene_card(
    path: Path,
    title: str,
    on_screen_text: str,
    visual_description: str,
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    title_font = load_font(72)
    text_font = load_font(48)
    small_font = load_font(32)

    margin = 120
    y = 120

    draw.text((margin, y), title, font=title_font)
    y += 150

    for line in wrap_text(on_screen_text, 45):
        draw.text((margin, y), line, font=text_font)
        y += 70

    y += 70

    for line in wrap_text(visual_description, 65):
        draw.text((margin, y), line, font=small_font)
        y += 48

    image.save(path)


def generate_tts(
    client: OpenAI,
    text: str,
    output_path: Path,
) -> None:
    model = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    voice = os.getenv("OPENAI_TTS_VOICE", "alloy")

    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=text,
        response_format="mp3",
    ) as response:
        response.stream_to_file(output_path)


def run_ffmpeg(args: list[str]) -> None:
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed:\n"
            + result.stderr[-4000:]
        )


def get_audio_duration(audio_path: Path) -> float:
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
        raise RuntimeError("ffprobe failed: " + result.stderr)

    return float(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()

    input_json = args.json_file.resolve()

    try:
        check_ffmpeg()

        data = load_json(input_json)

        lesson_id = data.get("lesson_id")
        if not lesson_id:
            raise ValueError("JSON is missing required field: lesson_id")

        if data.get("script_generation_status") != "completed":
            print(
                f"[SKIP] {lesson_id}: script_generation_status is not completed."
            )
            return 0

        if data.get("video_generation_status") == "completed":
            print(
                f"[SKIP] {lesson_id}: video_generation_status is already completed."
            )
            return 0

        script_path_value = data.get("script_path")
        if not script_path_value:
            raise ValueError("JSON is missing required field: script_path")

        script_path = Path(script_path_value)
        if not script_path.is_absolute():
            script_path = input_json.parent / script_path

        if not script_path.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")

        script = json.loads(script_path.read_text(encoding="utf-8"))

        if script.get("lesson_id") != lesson_id:
            raise ValueError(
                f"Script lesson_id mismatch: "
                f"{script.get('lesson_id')} != {lesson_id}"
            )

        scenes = script.get("scenes")
        if not scenes:
            raise ValueError("Video script contains no scenes.")

        data["video_generation_status"] = "running"
        save_json(input_json, data)

        output_root = Path(
            os.getenv("VIDEO_OUTPUT_DIR", input_json.parent / "video_outputs")
        )
        if not output_root.is_absolute():
            output_root = input_json.parent / output_root

        output_root.mkdir(parents=True, exist_ok=True)

        final_video = output_root / f"{lesson_id}.mp4"

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        with tempfile.TemporaryDirectory(prefix=f"{lesson_id}-video-") as tmp:
            tmp_dir = Path(tmp)

            scene_files: list[Path] = []
            audio_files: list[Path] = []

            # Generate scene cards and narration.
            for index, scene in enumerate(scenes, start=1):
                scene_id = scene.get("scene_id", f"scene-{index:02d}")
                voice = scene.get("voice", "").strip()

                if not voice:
                    raise ValueError(f"{scene_id} has no voice narration.")

                card = tmp_dir / f"{index:03d}-scene.png"
                audio = tmp_dir / f"{index:03d}-voice.mp3"

                render_scene_card(
                    card,
                    title=scene_id,
                    on_screen_text=scene.get("on_screen_text", ""),
                    visual_description=scene.get("visual", ""),
                )

                generate_tts(client, voice, audio)

                scene_files.append(card)
                audio_files.append(audio)

            # Render each scene as an MP4.
            scene_videos: list[Path] = []

            for index, (card, audio) in enumerate(
                zip(scene_files, audio_files),
                start=1,
            ):
                scene_video = tmp_dir / f"{index:03d}-scene.mp4"

                duration = get_audio_duration(audio)

                run_ffmpeg(
                    [
                        "ffmpeg",
                        "-y",
                        "-loop",
                        "1",
                        "-i",
                        str(card),
                        "-i",
                        str(audio),
                        "-c:v",
                        "libx264",
                        "-tune",
                        "stillimage",
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-pix_fmt",
                        "yuv420p",
                        "-r",
                        str(FPS),
                        "-t",
                        f"{duration:.3f}",
                        "-vf",
                        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                        str(scene_video),
                    ]
                )

                scene_videos.append(scene_video)

            concat_file = tmp_dir / "concat.txt"

            with concat_file.open("w", encoding="utf-8") as f:
                for scene_video in scene_videos:
                    escaped = str(scene_video).replace("'", "'\\''")
                    f.write(f"file '{escaped}'\n")

            temp_final = tmp_dir / f"{lesson_id}.mp4"

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
                    str(temp_final),
                ]
            )

            shutil.copy2(temp_final, final_video)

        data["video_generation_status"] = "completed"
        data["video_path"] = str(final_video)
        save_json(input_json, data)

        print(f"[DONE] {lesson_id}")
        print(f"       video: {final_video}")
        return 0

    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)

        try:
            data = load_json(input_json)
            data["video_generation_status"] = "failed"
            data["video_generation_error"] = str(exc)
            save_json(input_json, data)
        except Exception:
            pass

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
