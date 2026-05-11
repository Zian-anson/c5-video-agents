"""slide_designer.py — Agent that converts script outlines into valid pipeline JSON.

Takes the ScriptWriter's narration script → outputs valid slide JSON
that the ai-video-pipeline can consume directly.
"""
import json
import re
from autogen.beta import Agent
from src.config import deepseek_config

# Available palette choices for reference
PALETTE_OPTIONS = {
    "dark": "深色 Catppuccin 风格，专业科技感",
    "light": "浅色白底，清晰商务风",
    "midnight": "午夜深蓝，沉稳大气",
    "sunset": "紫金落日，创意活力",
    "forest": "森林深绿，自然环保",
}

PROMPT = """You are a SLIDE DESIGNER for AI video generation.

Your job is to take a script outline (from the ScriptWriter) and convert it into 
valid JSON that the video generation pipeline can use.

The pipeline accepts this JSON format:
```json
[
  {
    "template": "title|content|code|quote|section|comparison",
    "data": { ... template-specific fields ... },
    "duration": 5.0,
    "narration": "配音文字"
  }
]
```

TEMPLATE RULES (be precise):

title:
  data: {"title": "主标题", "subtitle": "副标题", "accent": "强调文字（可选）"}

content:
  data: {"title": "标题", "items": ["第一项", "第二项", "第三项"]}

code:
  data: {"title": "标题", "language": "python|bash|json", "code": "actual code here"}

quote:
  data: {"quote": "引用内容", "author": "作者名"}

section:
  data: {"title": "标题", "subtitle": "副标题（可选）"}

comparison:
  data: {"title": "对比标题", "left_title": "左侧标题", "left_items": ["A", "B"], "right_title": "右侧标题", "right_items": ["C", "D"]}

CRITICAL REQUIREMENTS:
1. Output ONLY valid JSON — no markdown fences, no extra text
2. Every slide MUST have: template, data, duration, narration
3. narration must be 15-40 Chinese characters
4. duration must be 4-12 seconds (match the narration length)
5. Ensure the JSON is parseable by json.loads()
6. Total slides: 4-8 slides
7. First slide should be "title" template
8. Last slide should be "title" template (closing/thank you)

Your output will be directly parsed by json.loads() — failure will crash the pipeline.
DO NOT include any text outside the JSON array.
DO NOT use markdown code blocks.
"""


def create_slide_designer(temperature: float = 0.2) -> Agent:
    """Create the SlideDesigner agent. Low temperature for consistent JSON output."""
    return Agent(
        "slide_designer",
        prompt=PROMPT,
        config=deepseek_config(temperature=temperature),
    )


def parse_slide_json(text: str) -> list[dict]:
    """Extract valid JSON array from agent output (handles markdown fences)."""
    # Try direct parse first
    text = text.strip()
    if text.startswith("```"):
        # Strip markdown fences
        text = re.sub(r'^```(?:json)?\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()
    
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON array in the text
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not parse slide JSON from agent output:\n{text[:500]}")
