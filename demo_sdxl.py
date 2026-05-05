"""demo_sdxl.py — Quick SDXL generation test with the best prompt from the pipeline.

Runs a fast single-scene demo: craft a prompt → generate SDXL image → done.

Usage:
  python3 demo_sdxl.py "a cyberpunk cat in neon rain, cinematic"
"""
import asyncio
import sys
from src.comfyui_client import check_comfyui, generate_sdxl_image


async def main():
    # Get prompt from command line or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = (
            "Cinematic shot, lone astronaut on desolate alien planet, "
            "colossal crystal city in background, bioluminescent blue light, "
            "dramatic sky, 35mm film grain, highly detailed"
        )

    print("🎬 Multi-Agent Video Studio — SDXL Demo")
    print(f"Prompt: {prompt}\n")

    comfy = await check_comfyui()
    if not comfy:
        print("❌ ComfyUI not running. Start it first.")
        return

    print("⏳ Generating SDXL image...")
    result = await generate_sdxl_image(prompt, scene_num=1, seed=42, steps=25)

    if result["status"] == "success":
        print(f"\n✅ SDXL image generated!")
        print(f"   📍 {result['image']}")
    else:
        print(f"\n❌ Failed: {result.get('detail', result['status'])}")


if __name__ == "__main__":
    asyncio.run(main())
