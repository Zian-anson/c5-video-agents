"""pipeline_adapter.py — Bridge between AG2 agents and ai-video-pipeline.

Calls the pipeline via subprocess (no dependency conflicts).
Converts agent output → pipeline args → actual video files.
"""
import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

# Path to the ai-video-pipeline project
PIPELINE_DIR = os.path.expanduser("~/hermes工作空间/项目/ai-video-pipeline")
DEFAULT_OUTPUT = os.path.expanduser("~/hermes工作空间/项目/c5-video-agents/output")

# Use the same Python that's running us (venv-safe)
PYTHON = sys.executable or "python3"

# Available options from the pipeline
PALETTES = ["dark", "light", "midnight", "sunset", "forest"]
VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",  # 亲切女声
    "xiaoyi": "zh-CN-XiaoyiNeural",      # 活泼女声
    "yunjian": "zh-CN-YunjianNeural",    # 男声
    "yunxi": "zh-CN-YunxiNeural",        # 阳光男声
    "xiaohan": "zh-CN-XiaohanNeural",    # 温柔女声
    "en-us": "en-US-AriaNeural",         # 英文女声
    "en-guy": "en-US-GuyNeural",         # 英文男声
}
TEMPLATES = ["title", "content", "code", "quote", "section", "comparison"]


def validate_slide_data(slides: list[dict]) -> list[str]:
    """Validate slide JSON structure. Returns list of error messages (empty = valid)."""
    errors = []
    for i, slide in enumerate(slides):
        if "template" not in slide:
            errors.append(f"Slide {i}: missing 'template'")
        elif slide["template"] not in TEMPLATES:
            errors.append(f"Slide {i}: unknown template '{slide['template']}'")
        if "data" not in slide:
            errors.append(f"Slide {i}: missing 'data'")
        if "duration" not in slide:
            errors.append(f"Slide {i}: missing 'duration'")
        if "narration" not in slide:
            errors.append(f"Slide {i}: missing 'narration'")
    return errors


def generate_video(
    slides_data: list[dict],
    voice: str = "xiaoxiao",
    palette: str = "dark",
    subtitles: bool = True,
    name: str = "ag2_video",
    fps: int = 30,
) -> dict:
    """Call the ai-video-pipeline to generate a video from slide JSON.

    Args:
        slides_data: List of slide dicts in pipeline JSON format
        voice: TTS voice key
        palette: Color palette name
        subtitles: Whether to burn subtitles
        name: Output filename prefix

    Returns:
        dict with keys: status, video_path, errors (if any)
    """
    # Validate
    errors = validate_slide_data(slides_data)
    if errors:
        return {"status": "error", "errors": errors, "video_path": None}

    # Validate palette
    if palette not in PALETTES:
        return {"status": "error", "errors": [f"Unknown palette '{palette}'. Choose from: {PALETTES}"], "video_path": None}

    # Validate voice
    if voice not in VOICES:
        return {"status": "error", "errors": [f"Unknown voice '{voice}'. Choose from: {list(VOICES.keys())}"], "video_path": None}

    # Create output dir
    output_dir = os.path.join(DEFAULT_OUTPUT, name)
    os.makedirs(output_dir, exist_ok=True)

    # Write slide JSON to temp file
    config_path = os.path.join(output_dir, "slides_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(slides_data, f, ensure_ascii=False, indent=2)

    # Build pipeline command
    cmd = [
        PYTHON,
        os.path.join(PIPELINE_DIR, "pipeline.py"),  # pipeline.py directly (not run.sh, to avoid proxy overrides)
        "pptv",
        "--config", config_path,
        "--voice", voice,
        "--palette", palette,
        "--name", name,
        "--output", output_dir,
        "--fps", str(fps),
    ]
    if subtitles:
        cmd.append("--subtitles")

    # Call pipeline
    print(f"  🎞 Running pipeline: {' '.join(cmd[:8])}...")
    # Set proxy for edge-tts
    env = os.environ.copy()
    env["https_proxy"] = "http://127.0.0.1:7897"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
        cwd=PIPELINE_DIR,
    )

    if result.returncode != 0:
        return {
            "status": "error",
            "errors": [f"Pipeline exited with code {result.returncode}", result.stderr[:1000]],
            "video_path": None,
            "stdout": result.stdout[-500:],
        }

    expected_video = os.path.join(output_dir, f"{name}.mp4")
    if not os.path.exists(expected_video):
        # Try to find any mp4 in output dir
        mp4_files = list(Path(output_dir).glob("*.mp4"))
        if mp4_files:
            expected_video = str(mp4_files[0])
        else:
            return {
                "status": "error",
                "errors": ["Video file not found in output directory"],
                "video_path": None,
                "stdout": result.stdout[-500:],
            }

    return {
        "status": "success",
        "video_path": expected_video,
        "config_path": config_path,
        "output_dir": output_dir,
        "stdout": result.stdout[-300:],
    }
