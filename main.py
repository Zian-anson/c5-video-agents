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
import re
import sys

from dotenv import load_dotenv
load_dotenv()

from src.agents.director import create_director
from src.agents.stylist_a import create_stylist_a
from src.agents.stylist_b import create_stylist_b
from src.agents.producer import create_producer
from src.agents.critic import create_critic
from src.comfyui_client import check_comfyui, generate_wan_video, simulate_generate


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def strip_think_tags(text: str) -> str:
    """Remove <think> blocks that MiniMax sometimes includes."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def extract_best_prompt(fp: dict) -> str:
    """Pick the winning prompt from the Producer's verdict."""
    verdict = fp["producer_verdict"]
    if "winner: stylist b" in verdict.lower() or "winner: b" in verdict.lower():
        prompt = fp["prompt_b"]
    else:
        prompt = fp["prompt_a"]
    prompt = strip_think_tags(prompt)
    if not prompt:
        prompt = strip_think_tags(fp["prompt_a"])
    return prompt


async def run_review_round(stylist_a, stylist_b, producer,
                           scene_text: str, round_num: int,
                           prev_prompt_a: str, prev_prompt_b: str,
                           prev_feedback: str) -> tuple[str, str, str]:
    """Run one mutual review round for a single scene.

    Returns (prompt_a, prompt_b, producer_feedback).
    """
    ctx_a = _build_stylist_context(scene_text, "cinematic", round_num,
                                    prev_prompt_a, prev_feedback)
    ctx_b = _build_stylist_context(scene_text, "minimal", round_num,
                                    prev_prompt_b, prev_feedback)

    reply_a, reply_b = await asyncio.gather(
        stylist_a.ask(ctx_a),
        stylist_b.ask(ctx_b),
    )

    prompt_a = reply_a.body.strip()
    prompt_b = reply_b.body.strip()

    print(f"  🎨 Stylist A (Cinematic): {prompt_a[:120]}...")
    print(f"  🎨 Stylist B (Minimal):  {prompt_b[:120]}...")

    is_final = round_num == 3
    eval_prompt = (
        f"Scene: {scene_text}\n\n"
        f"--- Stylist A (Cinematic) ---\n{prompt_a}\n\n"
        f"--- Stylist B (Minimal) ---\n{prompt_b}\n\n"
        f"Round: {round_num}/3\n"
        f"{'This is the FINAL round — declare a WINNER. End your evaluation with: WINNER: Stylist A  OR  WINNER: Stylist B' if is_final else 'Give specific feedback to both stylists for improvement.'}"
    )
    reply_prod = await producer.ask(eval_prompt)
    feedback = reply_prod.body.strip()
    print(f"  💼 Producer: {feedback[:200]}...\n")

    return prompt_a, prompt_b, feedback


def _build_stylist_context(scene_text: str, style: str, round_num: int,
                           prev_prompt: str, prev_feedback: str) -> str:
    """Build the prompt context for a stylist agent."""
    style_directive = {
        "cinematic": "Write a cinematic video prompt for this scene.",
        "minimal": "Write a clean, minimal video prompt for this scene.",
    }
    ctx = f"Scene: {scene_text}\n"
    if round_num > 1 and prev_feedback:
        ctx += (
            f"\nYour previous prompt: {prev_prompt}\n"
            f"\nFeedback from last round: {prev_feedback}\n"
            f"Revise and improve your prompt based on this feedback.\n\n"
        )
    ctx += style_directive.get(style, style_directive["cinematic"])
    return ctx


async def main():
    print("🎬 Multi-Agent Video Studio")
    print("   A team of AI agents collaborating on video generation\n")

    comfy_ok = await check_comfyui()
    print(f"ComfyUI: {'✅ Running' if comfy_ok else '⏹️  Not running (will simulate)'}")

    if len(sys.argv) > 1:
        topic = sys.argv[1]
        print(f"\n🎥 Video topic: {topic}\n")
    else:
        topic = input("\n🎥 What video do you want to create? ")
        print()

    # ─── Step 1: Director — Scene Breakdown ───
    separator("STEP 1: Director — Scene Breakdown")
    director = create_director()
    scene_reply = await director.ask(
        f"Break this video idea into 2-3 scenes: {topic}"
    )
    print(scene_reply.body)

    # ─── Create agents ───
    stylist_a = create_stylist_a()
    stylist_b = create_stylist_b()
    producer = create_producer()
    critic = create_critic()

    # ─── Step 2: 3 Rounds of Mutual Review per Scene ───
    separator("STEP 2: Prompt Engineering — 3 Rounds of Mutual Review")

    scenes = [s.strip() for s in scene_reply.body.split("\n\n") if s.strip()]
    final_prompts = []

    for scene_text in scenes:
        print(f"\n── Processing scene: {scene_text[:80]}... ───")

        prompt_a = ""
        prompt_b = ""
        feedback = ""

        for round_num in range(1, 4):
            print(f"\n  📍 Round {round_num}/3")
            prompt_a, prompt_b, feedback = await run_review_round(
                stylist_a, stylist_b, producer,
                scene_text, round_num,
                prompt_a, prompt_b, feedback,
            )

        final_prompts.append({
            "scene": scene_text,
            "prompt_a": prompt_a,
            "prompt_b": prompt_b,
            "producer_verdict": feedback,
        })

    # ─── Step 3: Generate Video via ComfyUI ───
    separator("STEP 3: Generate Video")
    for i, fp in enumerate(final_prompts):
        print(f"\nScene: {fp['scene'][:80]}...")
        best_prompt = extract_best_prompt(fp)
        print(f"Best prompt: {best_prompt[:150]}...")

        if comfy_ok:
            result = await generate_wan_video(best_prompt, scene_num=i + 1)
            if result["status"] == "success":
                print(f"  🎬 Wan2.1 video saved: {result.get('video', '?')}")
            else:
                print(f"  ⚠️ Wan2.1 generation: {result['status']} — {result.get('detail', '')}")
        else:
            result = await simulate_generate(best_prompt)
            print(f"  🎥 {result['note']}")

    # ─── Step 4: Critic Evaluation ───
    separator("STEP 4: Critic Evaluation")
    for fp in final_prompts:
        best_prompt = extract_best_prompt(fp)
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
