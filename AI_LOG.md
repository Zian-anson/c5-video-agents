# AI_LOG.md — Multi-Agent Video Studio

## Project: C5-AG2 — Multi-Agent Video Generation Studio

### Iteration Record

| # | Date | What | Verifiable outcome |
|---|------|------|--------------------|
| 1 | 2026-05-05 | Installed AG2 v0.12.2 (GitHub main branch), set up Python 3.12 venv | `python3 -c "from autogen.beta import Agent"` succeeded |
| 2 | 2026-05-05 | Tested DeepSeek via AG2 Beta OpenAIConfig | `test_ag2_beta.py` — valid reply received |
| 3 | 2026-05-05 | Tested MiniMax-M2.7 via AG2 Beta OpenAIConfig | `test_minimax.py` — valid reply received |
| 4 | 2026-05-05 | Tested multi-agent agent-as-tool pattern | `test_multiagent.py` — Stylist A consulted Stylist B |
| 5 | 2026-05-05 | Cloned Mesh Shield reference repo | Studied `ag2_adapter.py` and `pipeline.py` |
| 6 | 2026-05-05 | Built agent architecture (5 agents) | `src/agents/director.py`, `stylist_a.py`, `stylist_b.py`, `producer.py`, `critic.py` |
| 7 | 2026-05-05 | Built ComfyUI client | `src/comfyui_client.py` — confirmed running |
| 8 | 2026-05-05 | Full pipeline test with "星尘" (sci-fi game trailer) | 3 scenes, 3 rounds mutual review, Critic 8/10 |
| 9 | 2026-05-06 | Refactored main.py — helper functions, parallelized A/B, fixed variables | Syntax OK |
| 10 | 2026-05-10 | **v2 architecture**: full orchestration pipeline — Director → ScriptWriter → SlideDesigner → TTSDirector → VideoProducer → Critic revision loop | 45-75s video output |
| 11 | 2026-05-10 | `pipeline_adapter.py` — bridges AG2 agents with ai-video-pipeline via subprocess | Generated .mp4 |
| 12 | 2026-05-10 | Subtitle improvements: black stroke outline, Heiti SC (index=1) for CN punctuation | Correct punctuation |
| 13 | 2026-05-10 | TTS: edge-tts → SiliconFlow CosyVoice2 + macOS say fallback | Stable behind GFW |
| 14 | 2026-05-10 | BGM ambient drone via ffmpeg synthesis | Background music in output |
| 15 | 2026-05-10 | SDXL background via ComfyUI (reverted — chaotic quality) | BGs generated but unpredictable |
| 16 | 2026-05-10 | **ppt-agent-skills integration**: Puppeteer rendering, 1280x720, 5-layer depth, typography scale | Professional slide design |
| 17 | 2026-05-10 | dom-to-pptx installed (npm), ready for PPTX export | `npm install dom-to-pptx` |
| 18 | 2026-05-11 | Updated README, AI_LOG, committed and pushed to GitHub | All v2 work on main |

### AI Tools Used

| Tool | Version | Usage |
|------|---------|-------|
| Hermes Agent (DeepSeek v4 Flash) | — | Orchestrating the entire build |
| AG2 Beta | 0.12.2 (main) | Multi-agent framework |
| DeepSeek Chat API | deepseek-chat | All agents |
| SiliconFlow CosyVoice2 | — | TTS voice generation |
| ppt-agent-skills | v4.1 | Slide design system + Puppeteer rendering |

### Manual Steps Required

1. Setting up `.env` with API keys — cannot be automated (secrets)
2. Installing `openai` pip package (optional dep for OpenAIConfig)
3. ComfyUI optional for SDXL background generation
4. Puppeteer node package for ppt-agent-skills rendering
5. Clash Verge Rev for proxy (edge-tts, GitHub access in China)
