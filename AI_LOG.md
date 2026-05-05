# AI_LOG.md — Multi-Agent Video Prompt Studio

## Project: C5-AG2 — Multi-Agent Video Generation Studio

### Iteration Record

| # | Date | What | Verifiable outcome |
|---|------|------|--------------------|
| 1 | 2026-05-05 | Installed AG2 v0.12.2 (GitHub main branch), set up Python 3.12 venv | `python3 -c "from autogen.beta import Agent"` succeeded |
| 2 | 2026-05-05 | Tested DeepSeek via AG2 Beta OpenAIConfig | `test_ag2_beta.py` — "Focus on understanding basic principles..." reply received |
| 3 | 2026-05-05 | Tested MiniMax-M2.7 via AG2 Beta OpenAIConfig | `test_minimax.py` — valid reply received |
| 4 | 2026-05-05 | Tested multi-agent agent-as-tool pattern (DeepSeek calls MiniMax) | `test_multiagent.py` — Stylist A ("cinematic") consulted Stylist B ("minimal"), received alternative perspective |
| 5 | 2026-05-05 | Cloned Mesh Shield reference repo | `git clone https://github.com/roshaninfordham/meshshieldai.git` — studied `ag2_adapter.py` and `pipeline.py` |
| 6 | 2026-05-05 | Built agent architecture (5 agents) | `src/agents/director.py`, `stylist_a.py`, `stylist_b.py`, `producer.py`, `critic.py` |
| 7 | 2026-05-05 | Built ComfyUI client | `src/comfyui_client.py` — `check_comfyui()` confirmed running (0.20.1, 687 nodes) |
| 8 | 2026-05-05 | Full pipeline test with "星尘" (sci-fi game trailer) | 3 scenes created, 3 rounds of mutual review per scene, Critic scored 8/10 for all |

### AI Tools Used

| Tool | Version | Usage |
|------|---------|-------|
| Hermes Agent (DeepSeek v4 Flash) | — | Orchestrating the entire build: code generation, testing, debugging |
| AG2 Beta | 0.12.2 (main) | Multi-agent framework |
| DeepSeek Chat API | deepseek-chat | Stylist A, Director, Producer, Critic |
| MiniMax M2.7 API | MiniMax-M2.7 | Stylist B (second provider for different model) |

### Manual Steps Required

1. Setting up `.env` with API keys — cannot be automated (secrets)
2. Installing `openai` pip package (optional dep for OpenAIConfig)
3. ComfyUI must be running for actual video generation (optional for prompt-only mode)
