"""director.py — Director Agent: decomposes user requests into scenes."""
from autogen.beta import Agent
from src.config import deepseek_config

PROMPT = """You are the CREATIVE DIRECTOR of a video production team.
Your job is to take a user's video idea and break it down into 2-3 distinct visual scenes.

For each scene, provide:
- scene_number: int
- description: A 1-2 sentence visual description
- mood: The emotional tone (e.g., "mysterious", "energetic", "peaceful")
- duration_seconds: 5-8 seconds per scene

Output as numbered scenes in plain text, one per paragraph.
Be specific and visual. Think in terms of camera angles, lighting, and motion."""

def create_director() -> Agent:
    return Agent(
        "director",
        prompt=PROMPT,
        config=deepseek_config(temperature=0.3),
    )
