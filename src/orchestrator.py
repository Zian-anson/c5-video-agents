"""orchestrator.py — AG2 Multi-Agent Video Pipeline Orchestrator.

This is the AI director that coordinates a team of specialist agents
to create video content using the ai-video-pipeline as the rendering engine.

Flow:
1. Director — breaks down user request into scenes
2. ScriptWriter — writes narration scripts + slide outlines
3. SlideDesigner — converts scripts into valid pipeline JSON
4. TTSDirector — selects voice, palette, pacing
5. VideoProducer — calls pipeline to generate video
6. Critic — reviews output, accepts or triggers revise loop

Usage:
    python3 orchestrator.py --topic "产品介绍视频" [--max-revise 2]
"""
import asyncio
import json
import os
import sys
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen.beta import Agent
from src.config import deepseek_config
from src.agents.director import create_director
from src.agents.script_writer import create_script_writer
from src.agents.slide_designer import create_slide_designer, parse_slide_json
from src.agents.tts_director import create_tts_director, parse_tts_params
from src.agents.critic_v2 import create_critic_v2, parse_critic_verdict
from src.pipeline_adapter import generate_video


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def main():
    parser = argparse.ArgumentParser(description="AG2 Multi-Agent Video Studio — produce video from topic")
    parser.add_argument("--topic", "-t", help="Video topic or description")
    parser.add_argument("--max-revise", type=int, default=2, help="Max revision rounds (default: 2)")
    args = parser.parse_args()

    topic = args.topic
    if not topic:
        topic = input("🎥 做什么视频？输入主题: ")

    max_revise = args.max_revise
    print(f"\n🎬 AG2 Multi-Agent Video Studio")
    print(f"   主题: {topic}")
    print(f"   最大修订轮次: {max_revise}")
    print(f"   Agent Team: Director → ScriptWriter → SlideDesigner → TTSDirector → Producer → Critic")

    # ═══════════════════════════════════════════════
    # STEP 1: Director — Scene Breakdown
    # ═══════════════════════════════════════════════
    separator("STEP 1: Director — 场景分解")
    director = create_director()
    scene_reply = await director.ask(
        f"Break this video topic into scenes and plan the overall structure: {topic}"
    )
    print(scene_reply.body)

    # ═══════════════════════════════════════════════
    # STEP 2: ScriptWriter — Write narration scripts
    # ═══════════════════════════════════════════════
    separator("STEP 2: ScriptWriter — 编写配音脚本")
    script_writer = create_script_writer()
    script_reply = await script_writer.ask(
        f"Video topic: {topic}\n\n"
        f"Scene breakdown from Director:\n{scene_reply.body}\n\n"
        f"Write a complete narration script and slide outline. "
        f"Aim for 4-8 slides total. Each slide narration should be 15-40 Chinese characters."
        f"Make the slides flow naturally as a complete presentation."
    )
    print(script_reply.body)

    # ═══════════════════════════════════════════════
    # STEP 3: SlideDesigner — Convert to JSON
    # ═══════════════════════════════════════════════
    separator("STEP 3: SlideDesigner — 转换为管道JSON")
    slide_designer = create_slide_designer()
    slide_reply = await slide_designer.ask(
        f"Topic: {topic}\n\n"
        f"Script outline:\n{script_reply.body}\n\n"
        f"Convert this into valid pipeline JSON. Remember:\n"
        f"- Output ONLY valid JSON array\n"
        f"- Every slide needs: template, data, duration, narration\n"
        f"- Do NOT use markdown code blocks in your output\n"
        f"- 4-8 slides total\n"
        f"- First slide: 'title' template\n"
        f"- Last slide: 'title' template (thank you/closing)"
    )

    # Parse and validate slide JSON
    try:
        slides_data = parse_slide_json(slide_reply.body)
        print(f"  ✅ Parsed {len(slides_data)} slides")
        for i, s in enumerate(slides_data):
            print(f"     Slide {i+1}: [{s.get('template')}] {s.get('data', {}).get('title', '?')} — {s.get('duration', '?')}s")
    except ValueError as e:
        print(f"  ❌ Failed to parse slide JSON: {e}")
        print("  Attempting fallback: asking SlideDesigner to fix...")

        # One retry with stricter instructions
        fix_reply = await slide_designer.ask(
            f"You previously produced invalid JSON. Here is what you wrote:\n\n{slide_reply.body}\n\n"
            f"This is NOT valid JSON. Please output ONLY a valid JSON array — no markdown, no extra text.\n"
            f"Start with [ and end with ]. Valid JSON only."
        )
        try:
            slides_data = parse_slide_json(fix_reply.body)
            print(f"  ✅ Retry: parsed {len(slides_data)} slides")
        except ValueError as e2:
            print(f"  ❌ Still failed: {e2}")
            print("  Using demo slides as fallback.")
            slides_data = _demo_slides_for_topic(topic)

    # ═══════════════════════════════════════════════
    # STEP 4: TTSDirector — Select production params
    # ═══════════════════════════════════════════════
    separator("STEP 4: TTSDirector — 选择参数")
    tts_director = create_tts_director()

    # Summarize slides for the TTS director
    slides_summary = "\n".join([
        f"Slide {i+1}: [{s.get('template')}] {s.get('data', {}).get('title', s.get('data', {}).get('quote', '?'))} — {s.get('narration', '')[:40]}..."
        for i, s in enumerate(slides_data[:8])
    ])

    tts_reply = await tts_director.ask(
        f"Topic: {topic}\n\n"
        f"Slides:\n{slides_summary}\n\n"
        f"Select the best TTS voice, palette, and production parameters."
    )
    print(tts_reply.body)
    params = parse_tts_params(tts_reply.body)
    print(f"\n  Selected: voice={params['voice']}, palette={params['palette']}, "
          f"subtitles={params['subtitles']}, fps={params['fps']}")

    # ═══════════════════════════════════════════════
    # STEP 5: VideoProducer — Generate video
    # ═══════════════════════════════════════════════
    separator("STEP 5: VideoProducer — 生成视频")
    print(f"  正在调用 ai-video-pipeline 生成视频...\n")

    result = generate_video(
        slides_data=slides_data,
        voice=params["voice"],
        palette=params["palette"],
        subtitles=params["subtitles"],
        fps=params["fps"],
        name=f"ag2_video_{topic[:20].replace(' ', '_')}",
    )

    if result["status"] == "error":
        print(f"  ❌ 视频生成失败:")
        for err in result.get("errors", []):
            print(f"     - {err}")
        print(f"\n  📋 Pipeline stdout:\n{result.get('stdout', 'N/A')}")
        return

    video_path = result["video_path"]
    print(f"  ✅ 视频生成成功!")
    print(f"  📁 {video_path}")
    print(f"  📄 配置: {result.get('config_path', 'N/A')}")

    # Get file size
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"  📏 文件大小: {size_mb:.1f} MB")

    # ═══════════════════════════════════════════════
    # STEP 6: Critic — Review and iterate
    # ═══════════════════════════════════════════════
    separator("STEP 6: Critic — 视频评审")

    critic = create_critic_v2()
    revision_round = 0

    while revision_round <= max_revise:
        # Build review context for critic
        slide_detail = json.dumps(slides_data, ensure_ascii=False, indent=2)

        review_reply = await critic.ask(
            f"Video Topic: {topic}\n\n"
            f"Production parameters:\n"
            f"  Voice: {params['voice']}\n"
            f"  Palette: {params['palette']}\n"
            f"  Subtitles: {params['subtitles']}\n\n"
            f"Slide content:\n{slide_detail[:2000]}\n\n"
            f"Evaluate this video based on:\n"
            f"1. Content accuracy — does it match the topic?\n"
            f"2. Slide design — clear and professional?\n"
            f"3. Narration — natural and well-paced?\n"
            f"4. Audio-visual sync — timing appropriate?\n"
            f"5. Overall impact — engaging and effective?\n\n"
            f"Output VERDICT: PASS, REVISE, or FAIL at the end."
        )
        print(f"\n📋 Critic 评审 (第 {revision_round + 1} 轮):")
        print(review_reply.body)

        verdict = parse_critic_verdict(review_reply.body)

        if verdict == "PASS":
            print(f"\n  ✅ Critic 通过! 视频可以交付。")
            break
        elif revision_round >= max_revise:
            print(f"\n  ⚠️ 达到最大修订次数 {max_revise}，接受当前版本。")
            break
        else:
            revision_round += 1
            print(f"\n  🔄 启动第 {revision_round} 轮修订...")

            # Ask ScriptWriter to revise based on critic feedback
            revise_reply = await script_writer.ask(
                f"Original topic: {topic}\n\n"
                f"Current slide content:\n{slide_detail[:2000]}\n\n"
                f"Critic feedback:\n{review_reply.body}\n\n"
                f"Revise the narration and content based on this feedback. "
                f"Output in the same format as before."
            )

            # Ask SlideDesigner to regenerate JSON
            redesign_reply = await slide_designer.ask(
                f"Revised script:\n{revise_reply.body}\n\n"
                f"Convert to valid pipeline JSON. Array only, no extra text."
            )

            try:
                slides_data = parse_slide_json(redesign_reply.body)
                print(f"  ✅ Revised: {len(slides_data)} slides")
            except ValueError:
                print(f"  ⚠️ 修订JSON解析失败，保留之前的版本")
                break

            # Regenerate video
            print(f"  重新生成视频...")
            result = generate_video(
                slides_data=slides_data,
                voice=params["voice"],
                palette=params["palette"],
                subtitles=params["subtitles"],
                fps=params["fps"],
                name=f"ag2_video_{topic[:20].replace(' ', '_')}_rev{revision_round}",
            )

            if result["status"] == "success":
                video_path = result["video_path"]
                print(f"  ✅ 修订版视频: {video_path}")
            else:
                print(f"  ❌ 修订版生成失败: {result.get('errors', [])}")
                break

    # ═══════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════
    separator("SUMMARY")
    print(f"  主题: {topic}")
    print(f"  幻灯片: {len(slides_data)} 页")
    print(f"  配音: {params['voice']} | 配色: {params['palette']}")
    print(f"  修订轮次: {revision_round}")
    print(f"  最终视频: {video_path}")
    print(f"\n  Agent Team 协作完成:")
    print(f"    🎬 Director (DeepSeek) — 场景分解")
    print(f"    ✍️ ScriptWriter (DeepSeek) — 配音脚本")
    print(f"    🎨 SlideDesigner (DeepSeek) — 幻灯片设计")
    print(f"    🎙 TTSDirector (DeepSeek) — 参数选择")
    print(f"    🎞 VideoProducer — 调用管线生成")
    print(f"    🔍 Critic (DeepSeek) — 质量评审")
    print(f"\n  💾 可交付: {video_path}")


def _demo_slides_for_topic(topic: str) -> list[dict]:
    """Fallback slides when agent output can't be parsed."""
    return [
        {
            "template": "title",
            "data": {"title": topic, "subtitle": "AI 自动生成的演示视频", "accent": "Powered by AG2 Multi-Agent"},
            "duration": 5.0,
            "narration": f"欢迎收看{topic}的介绍，本视频由 AI 多智能体系统全自动生成。"
        },
        {
            "template": "content",
            "data": {
                "title": "核心内容",
                "items": ["智能规划与编排", "自动化生成管线", "多轮质量审核"]
            },
            "duration": 6.0,
            "narration": f"这个视频展示了 AI 多智能体协作的能力，从场景分解到脚本编写，再到幻灯片设计和视频生成，全部自动完成。"
        },
        {
            "template": "quote",
            "data": {"quote": "智能协作，创造无限可能", "author": "AG2 Multi-Agent Video Studio"},
            "duration": 4.0,
            "narration": "智能协作，创造无限可能。"
        },
        {
            "template": "title",
            "data": {"title": "谢谢观看", "subtitle": "AG2 Multi-Agent + AI Video Pipeline", "accent": ""},
            "duration": 4.0,
            "narration": "感谢观看，欢迎体验 AG2 多智能体视频创作。"
        }
    ]


if __name__ == "__main__":
    # Force unbuffered output so real-time progress shows in piped/head output
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    asyncio.run(main())
