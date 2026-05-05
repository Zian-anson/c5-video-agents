"""test_ag2_beta.py — verify AG2 Beta works with DeepSeek"""
import asyncio
import os
from dotenv import load_dotenv
from autogen.beta import Agent
from autogen.beta.config import OpenAIConfig

load_dotenv()

async def main():
    # Use DeepSeek via OpenAI-compatible config
    config = OpenAIConfig(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=0.2,
    )

    agent = Agent(
        "greeter",
        prompt="You are a friendly assistant. Reply in one short sentence.",
        config=config,
    )

    reply = await agent.ask("Give me one tip for learning chess.")
    print(f"Reply: {reply.body}")
    print("✅ AG2 Beta with DeepSeek works!")

if __name__ == "__main__":
    asyncio.run(main())
