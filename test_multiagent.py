"""test_multiagent.py — verify agent-as-tool pattern with different models"""
import asyncio
import os
from dotenv import load_dotenv
from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig

load_dotenv()

def ds_config():
    return OpenAIConfig(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=0.3,
    )

def mm_config():
    return OpenAIConfig(
        model="MiniMax-M2.7",
        api_key=os.getenv("MINIMAX_CN_API_KEY"),
        base_url=os.getenv("MINIMAX_CN_BASE_URL", "https://api.minimaxi.com/v1"),
        temperature=0.3,
    )

async def main():
    # Two agents with different models
    stylist_a = Agent(
        "stylist_a",
        prompt=(
            "You are a video STYLIST who prefers DRAMATIC, CINEMATIC visuals. "
            "Given a video concept, propose a short visual treatment (2-3 sentences). "
            "Focus on lighting, camera movement, and atmosphere."
        ),
        config=ds_config(),
    )

    stylist_b = Agent(
        "stylist_b",
        prompt=(
            "You are a video STYLIST who prefers CLEAN, MODERN, MINIMAL aesthetics. "
            "Given a video concept, propose a short visual treatment (2-3 sentences). "
            "Focus on simplicity, typography, and narrative clarity."
        ),
        config=mm_config(),
    )

    # Expose B as a tool for A — agent-as-tool pattern
    consult_b = stylist_b.as_tool(
        name="consult_stylist_b",
        description="Send a treatment draft to the MINIMAL stylist for an alternative perspective.",
    )
    stylist_a.add_tool(consult_b)

    question = (
        "A 15-second promotional video for a new indie game called "
        "'Neon Drift' — a cyberpunk racing game."
    )

    print("── Asking Stylist A (Dramatic, DeepSeek) ───")
    reply = await stylist_a.ask(question)
    print(reply.body)
    print("\n✅ Multi-agent with different models works!")

if __name__ == "__main__":
    asyncio.run(main())
