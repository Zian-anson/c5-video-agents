"""critic_v2.py — Enhanced Critic that reviews actual video output.

Reviews not just prompts but the completed video:
- Watches screenshot frames (via vision_analyze)
- Evaluates pacing, audio sync, visual quality
- Decides PASS / REVISE / FAIL with detailed feedback
"""
from autogen.beta import Agent
from src.config import deepseek_config

PROMPT = """You are a PROFESSIONAL VIDEO CRITIC. You review AI-generated videos
and provide actionable feedback.

Your evaluation criteria:
1. **Content accuracy** — Does the video match the intended topic?
2. **Slide design** — Is the visual design clear and professional?
3. **Narration quality** — Is the voiceover natural and well-paced?
4. **Audio-visual sync** — Do the slides change at the right moments?
5. **Overall impact** — Is the video engaging and effective?

For each criterion, score 0-10 and give specific improvement suggestions.

At the end, output a verdict:
VERDICT: PASS | REVISE | FAIL

- PASS: Ready for delivery, minor tweaks only
- REVISE: Good foundation but needs specific improvements (list them)
- FAIL: Major issues, needs fundamental rework

Be specific and constructive. "The pacing is too fast" is better than "needs work."
"""


def create_critic_v2(temperature: float = 0.3) -> Agent:
    """Create the enhanced Critic agent for video review."""
    return Agent(
        "critic_v2",
        prompt=PROMPT,
        config=deepseek_config(temperature=temperature),
    )


def parse_critic_verdict(text: str) -> str:
    """Extract PASS/REVISE/FAIL from critic output."""
    for line in text.strip().split("\n"):
        line = line.strip().upper()
        if line.startswith("VERDICT:"):
            verdict = line.split(":", 1)[1].strip()
            if verdict in ("PASS", "REVISE", "FAIL"):
                return verdict
    return "REVISE"  # Default to revise if can't parse
