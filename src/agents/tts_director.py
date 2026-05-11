"""tts_director.py — Agent that selects voice, palette, and pacing.

Analyzes the script and topic to recommend optimal TTS and visual parameters.
"""
from autogen.beta import Agent
from src.config import deepseek_config

PROMPT = """You are the TTS + VISUAL DIRECTOR for AI video production.

Your job: given a video script and topic, select the BEST combination of:
1. Voice (TTS voice that matches the tone)
2. Color palette (visual mood)
3. Pacing (duration adjustments per slide)
4. Whether subtitles are needed

Available voices:
- xiaoxiao — 亲切女声，适合通用/教程/产品介绍
- xiaoyi — 活泼女声，适合年轻/创意/娱乐内容
- yunjian — 沉稳男声，适合科技/商务/正式场合
- yunxi — 阳光男声，适合积极/励志/教育内容
- xiaohan — 温柔女声，适合情感/生活/人文内容
- en-us — 英文女声，适合英文内容

Available palettes:
- dark — 深色Catppuccin，科技感专业
- light — 浅色白底，清晰商务
- midnight — 午夜深蓝，沉稳大气
- sunset — 紫金落日，创意活力
- forest — 森林深绿，自然环保

Output exactly in this format — no extra text:
VOICE: <voice_key>
PALETTE: <palette_name>
SUBTITLES: yes|no
FPS: 30
REASONING: <1-2 sentence explanation>
"""


def create_tts_director(temperature: float = 0.2) -> Agent:
    """Create the TTS Director agent."""
    return Agent(
        "tts_director",
        prompt=PROMPT,
        config=deepseek_config(temperature=temperature),
    )


def parse_tts_params(text: str) -> dict:
    """Parse the TTS director's output into a params dict."""
    params = {
        "voice": "xiaoxiao",
        "palette": "dark",
        "subtitles": True,
        "fps": 30,
        "reasoning": "",
    }
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.lower().startswith("voice:"):
            params["voice"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("palette:"):
            params["palette"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("subtitles:"):
            val = line.split(":", 1)[1].strip().lower()
            params["subtitles"] = val in ("yes", "true", "1")
        elif line.lower().startswith("fps:"):
            try:
                params["fps"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.lower().startswith("reasoning:"):
            params["reasoning"] = line.split(":", 1)[1].strip()
    return params
