"""config.py — Model configurations for the multi-agent video studio.

Two different providers for the two prompt engineers:
- Stylist A: DeepSeek v4 Flash (dramatic/cinematic)
- Stylist B: MiniMax-M2.7 (clean/minimal)
"""
import os
from dotenv import load_dotenv
from autogen.beta.config import OpenAIConfig

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MINIMAX_API_KEY = os.getenv("MINIMAX_CN_API_KEY")

def deepseek_config(temperature: float = 0.3) -> OpenAIConfig:
    """Stylist A — DeepSeek (text-focused, strong reasoning)"""
    return OpenAIConfig(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=temperature,
        max_completion_tokens=2048,
    )

def minimax_config(temperature: float = 0.3) -> OpenAIConfig:
    """Stylist B — MiniMax (creative, visual)"""
    return OpenAIConfig(
        model="MiniMax-M2.7",
        api_key=MINIMAX_API_KEY,
        base_url=os.getenv("MINIMAX_CN_BASE_URL", "https://api.minimaxi.com/v1"),
        temperature=temperature,
        max_completion_tokens=2048,
    )

# Validate keys on import
if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY not found in .env")
if not MINIMAX_API_KEY:
    raise RuntimeError("MINIMAX_CN_API_KEY not found in .env")
