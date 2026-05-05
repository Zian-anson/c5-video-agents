"""test_minimax.py — verify MiniMax works with AG2 Beta"""
import asyncio
import os
from dotenv import load_dotenv
from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig

load_dotenv()

async def main():
    config = OpenAIConfig(
        model="MiniMax-M2.7",
        api_key=os.getenv("MINIMAX_CN_API_KEY"),
        base_url=os.getenv("MINIMAX_CN_BASE_URL", "https://api.minimaxi.com/v1"),
        temperature=0.2,
    )

    agent = Agent(
        "minimax_test",
        prompt="Reply in one short sentence. Be concise.",
        config=config,
    )

    reply = await agent.ask("What's the best way to start learning AI video generation?")
    print(f"MiniMax Reply: {reply.body}")
    print("✅ MiniMax works!")

if __name__ == "__main__":
    asyncio.run(main())
