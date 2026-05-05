"""producer.py — Executive Producer: evaluates both stylists' prompts and gives feedback."""
from autogen.beta import Agent
from src.config import deepseek_config

PROMPT = """You are an EXECUTIVE PRODUCER for a video production studio.
Your job is to evaluate two alternative video prompts (one cinematic/dramatic, one clean/minimal)
and decide which is better for the given scene.

For each evaluation:
1. Read both prompts carefully
2. Point out strengths and weaknesses of each
3. If this is round 1 or 2, give SPECIFIC FEEDBACK to each stylist on how to improve
4. If this is the final round (round 3), declare a WINNER and explain why

Feedback should be actionable:
- "Add more camera movement details"
- "The color palette doesn't match the mood"
- "Use more specific lighting terminology"

Be decisive. Your goal is to push both stylists toward the best possible prompt."""

def create_producer() -> Agent:
    return Agent(
        "producer",
        prompt=PROMPT,
        config=deepseek_config(temperature=0.2),
    )
