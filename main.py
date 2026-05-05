#!/usr/bin/env python3
"""main.py — Multi-Agent Video Studio.

A team of AG2 Beta agents collaborating to generate video prompts:
1. Director — breaks down user request into scenes
2. Stylist A (DeepSeek) — cinematic/dramatic prompts
3. Stylist B (MiniMax) — clean/minimal prompts  
4. Producer — evaluates and selects the best prompt
5. Critic — reviews quality

3 rounds of mutual review between the two stylists.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.config import deepseek_config, minimax_config
from src.agents.director import create_director
from src.agents.stylist_a import create_stylist_a
from src.agents.stylist_b import create_stylist_b
from src.agents.producer import create_producer
from src.agents.critic import create_critic
from src.comfyui_client import check_comfyui, simulate_generate


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def main():
    print("🎬 Multi-Agent Video Studio")
    print("   A team of AI agents collaborating on video generation\n")

    # Check ComfyUI
    comfy_ok = await check_comfyui()
    print(f"ComfyUI: {'✅ Running' if comfy_ok else '⏹️  Not running (will simulate)'}")

    # Get user input
    topic = input("\n🎥 What video do you want to create? ")
    print()

    # ─── Step 1: Director breaks down into scenes ───
    separator("STEP 1: Director — Scene Breakdown")
    director = create_director()
    scene_reply = await director.ask(
        f"Break this video idea into 2-3 scenes: {topic}"
    )
    print(scene_reply.body)

    # ─── Create the stylist agents ───
    stylist_a = create_stylist_a()
    stylist_b = create_stylist_b()
    producer = create_producer()
    critic = create_critic()

    # ─── Step 2-3: For each scene, 3 rounds of mutual review ───
    separator("STEP 2: Prompt Engineering — 3 Rounds of Mutual Review")

    prompt_a = ""
    prompt_b = ""
    final_prompts = []

    for scene_text in scene_reply.body.split("\n\n"):
        if not scene_text.strip():
            continue
        print(f"\n── Processing scene: {scene_text[:80]}... ───")

        for round_num in range(1, 4):
            print(f"\n  📍 Round {round_num}/3")

            # Stylist A writes/revises
            ctx_a = f"Scene: {scene_text}\n"
            if round_num > 1:
                ctx_a += (
                    f"\nYour previous prompt: {prompt_a}\n"
                    f"\nFeedback from last round: {feedback}\n"
                    f"Revise and improve your prompt based on this feedback."
                )
            ctx_a += "\nWrite a cinematic video prompt for this scene."
            reply_a = await stylist_a.ask(ctx_a)
            prompt_a = reply_a.body.strip()
            print(f"  🎨 Stylist A (Cinematic): {prompt_a[:120]}...")

            # Stylist B writes/revises
            ctx_b = f"Scene: {scene_text}\n"
            if round_num > 1:
                ctx_b += (
                    f"\nYour previous prompt: {prompt_b}\n"
                    f"\nFeedback from last round: {feedback}\n"
                    f"Revise and improve your prompt based on this feedback."
                )
            ctx_b += "\nWrite a clean, minimal video prompt for this scene."
            reply_b = await stylist_b.ask(ctx_b)
            prompt_b = reply_b.body.strip()
            print(f"  🎨 Stylist B (Minimal):  {prompt_b[:120]}...")

            # Producer evaluates
            eval_prompt = (
                f"Scene: {scene_text}\n\n"
                f"--- Stylist A (Cinematic) ---\n{prompt_a}\n\n"
                f"--- Stylist B (Minimal) ---\n{prompt_b}\n\n"
            f"Round: {round_num}/3\n"
            f"{'This is the FINAL round — declare a WINNER. End your evaluation with: WINNER: Stylist A  OR  WINNER: Stylist B' if round_num == 3 else 'Give specific feedback to both stylists for improvement.'}"
            )
            reply_prod = await producer.ask(eval_prompt)
            feedback = reply_prod.body.strip()
            print(f"  💼 Producer: {feedback[:200]}...\n")

        # Store final winner prompt for this scene
        final_prompts.append({
            "scene": scene_text,
            "prompt_a": prompt_a,
            "prompt_b": prompt_b,
            "producer_verdict": feedback,
        })

    # ─── Step 4: Generate via ComfyUI ───
    separator("STEP 3: Generate Video")
    for fp in final_prompts:
        print(f"\nScene: {fp['scene'][:80]}...")
        # Use the winning prompt based on Producer's WINNER declaration
        verdict = fp["producer_verdict"]
        if "winner: stylist b" in verdict.lower() or "winner: b" in verdict.lower():
            best_prompt = fp["prompt_b"]
        else:
            best_prompt = fp["prompt_a"]

        # Strip any <think> tags from the prompt text
        import re
        best_prompt = re.sub(r'<think>.*?</think>', '', best_prompt, flags=re.DOTALL).strip()
        if not best_prompt:
            best_prompt = fp["prompt_a"]
            best_prompt = re.sub(r'<think>.*?</think>', '', best_prompt, flags=re.DOTALL).strip()

        print(f"Best prompt: {best_prompt[:150]}...")

        if comfy_ok:
            result = await simulate_generate(best_prompt)
            print(f"🎥 Generated: {result['status']}")
        else:
            result = await simulate_generate(best_prompt)
            print(f"🎥 {result['note']}")

    # ─── Step 5: Critic review ───
    separator("STEP 4: Critic Evaluation")
    for fp in final_prompts:
        verdict = fp["producer_verdict"]
        if "winner: stylist b" in verdict.lower() or "winner: b" in verdict.lower():
            best_prompt = fp["prompt_b"]
        else:
            best_prompt = fp["prompt_a"]

        import re
        best_prompt = re.sub(r'<think>.*?</think>', '', best_prompt, flags=re.DOTALL).strip()
        if not best_prompt:
            best_prompt = fp["prompt_a"]
            best_prompt = re.sub(r'<think>.*?</think>', '', best_prompt, flags=re.DOTALL).strip()

        review = await critic.ask(
            f"Original scene: {fp['scene']}\n\n"
            f"Final video prompt: {best_prompt}\n\n"
            f"Evaluate this prompt."
        )
        print(f"\n📋 Critic for scene:\n{review.body}\n")

    # ─── Summary ───
    separator("SUMMARY")
    print(f"✅ Created {len(final_prompts)} scene prompts")
    print(f"✅ 3 rounds of A↔B mutual review per scene")
    print(f"✅ {len(final_prompts)} video prompts ready for generation")
    print("\n🎬 Multi-agent team composition:")
    print("  🎬 Director (DeepSeek) — Scene breakdown")
    print("  🎨 Stylist A (DeepSeek) — Cinematic prompts")
    print("  🎨 Stylist B (MiniMax) — Minimal prompts")
    print("  💼 Producer (DeepSeek) — Evaluation & selection")
    print("  🔍 Critic (DeepSeek) — Quality review")
    print("  🎥 ComfyUI — Video generation engine")


if __name__ == "__main__":
    asyncio.run(main())
