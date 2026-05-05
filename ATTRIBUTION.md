# ATTRIBUTION.md — C5-AG2 Video Prompt Studio

## Fork Source

This project is inspired by **Mesh Shield** ([roshaninfordham/meshshieldai](https://github.com/roshaninfordham/meshshieldai))
from the AG2 Hackathon (May 2026, NYC).

### What was borrowed

| Concept | From Mesh Shield | How we adapted |
|---------|-----------------|----------------|
| AG2 Beta agent pipeline | `apps/agent/src/agent/llm/ag2_adapter.py` — LLMAdapter wrapping `autogen.beta.Agent` | Used same `Agent(config=OpenAIConfig(...))` pattern |
| Sequential agent stages | `pipeline.py` — Prioritizer → Allocator → Justifier → Escalator | Changed to Director → Stylist A/B (parallel) → Producer → Critic |
| Pydantic config pattern | `pyproject.toml` project structure | Used similar src/ layout |

### What's original

- **Cinematic vs Minimal stylist prompts** — hand-crafted agent prompts for video generation
- **3-round mutual review loop** — Stylist A ↔ Stylist B cross-review orchestrated by Producer
- **ComfyUI integration** — REST API client for AI video generation
- **Dual-provider architecture** — DeepSeek (cinematic) + MiniMax (minimal) in same pipeline

---

## AG2 Beta Documentation References

| Doc | What we used |
|-----|-------------|
| `11_beta_agents.mdx` | `Agent(name, prompt, config)` instantiation |
| `13_beta_task_delegation.mdx` | Multi-agent orchestration pattern |
| `20_beta_example_hello_agent.mdx` | `agent.ask()` / `reply.body` pattern |
| `21_beta_example_research_squad.mdx` | Multi-agent collaboration structure |
| `30_beta_tools_builtin.mdx` | Tool-based agent interaction |
