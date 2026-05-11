# 🎬 AG2 Multi-Agent Video Studio

> 将一句话需求 → 多智能体协作 → 完整视频。6 个 AG2 Beta Agent 编排 + ai-video-pipeline 渲染出片。

**赛道：** `multi-agent` · `video-generation`
**基座：** [AG2 Beta](https://github.com/ag2ai/ag2) (v0.12.2+)
**渲染引擎：** [ai-video-pipeline](https://github.com/Zian-anson/hermes-agent/tree/main)（HTML+Chrome→ffmpeg） + [ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills)（Puppeteer 渲染）

---

## 一句话定位

**输入：** 一个视频主题（如"AG2 多智能体介绍"）
**输出：** 完整 .mp4 视频（有画面 + 配音 + 字幕 + BGM）

多智能体协作生成内容 → ai-video-pipeline 渲染为视频 → Critic 审片循环迭代。

---

## 架构

```
用户输入 "做一段 3 分钟的产品介绍视频"
         │
         ▼
┌─────────────────────────────────────┐
│ 🎬 Director (DeepSeek)              │
│     拆解需求，生成场景分解           │
├─────────────────────────────────────┤
│ ✍️ ScriptWriter (DeepSeek)          │
│     写配音脚本 + 幻灯片大纲         │
├─────────────────────────────────────┤
│ 🎨 SlideDesigner (DeepSeek)         │
│     脚本 → 有效 pipeline JSON       │
├─────────────────────────────────────┤
│ 🎙 TTSDirector (DeepSeek)           │
│     选 voice/palette/字幕/帧率      │
├─────────────────────────────────────┤
│ 🎞 VideoProducer                    │
│     调 ai-video-pipeline 生成视频   │
│     (HTML+Puppeteer→截图→TTS→ffmpeg)│
├─────────────────────────────────────┤
│ 🔍 Critic (DeepSeek)                │
│     PASS/REVISE/FAIL 裁决           │
│     ↓ REVISE → 回到 ScriptWriter    │
└─────────────────────────────────────┘
```

### 修订循环

```
原版 → Critic 评审 → REVISE → ScriptWriter 修订 → SlideDesigner 修订 → 新版
     → Critic 再审 → REVISE → ... → 达最大轮次 or PASS → 交付
```

---

## 快速开始

### 环境要求

- Python 3.10+（推荐 3.12）
- Google Chrome（用于幻灯片截图）
- Google Chrome 已安装
- ffmpeg 8.1+（`brew install ffmpeg`）
- ComfyUI + SDXL（可选，用于 AI 背景图）
- Node.js（用于 ppt-agent-skills 的 Puppeteer 渲染）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/Zian-anson/c5-video-agents.git
cd c5-video-agents

# 2. Python 环境
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
pip install git+https://github.com/ag2ai/ag2.git

# 3. 配置 API 密钥
# 编辑 .env 填入：
# DEEPSEEK_API_KEY=sk-xxx
# SILICONFLOW_API_KEY=sk-xxx（用于 CosyVoice2 TTS）
# MINIMAX_CN_API_KEY=sk-xxx

# 4. 安装 Pipette（用于 ppt-agent-skills 渲染）
npm install puppeteer
```

### 运行

```bash
# 一键启动（激活 venv + 设置代理）
./run_video_studio.sh --topic "你的视频主题"

# 或手动
source .venv312/bin/activate
export SILICONFLOW_API_KEY=sk-xxx
python3 -m src.orchestrator --topic "AG2 多智能体介绍"
```

### 输出

视频文件在 `output/` 目录下：
```
output/ag2_video_你的主题/ag2_video_你的主题.mp4          # 原版
output/ag2_video_你的主题_rev1/ag2_video_你的主题_rev1.mp4  # 修订版 1
output/ag2_video_你的主题_rev2/ag2_video_你的主题_rev2.mp4  # 修订版 2（最终版）
```

---

## 多智能体架构

| 智能体 | 角色 | 模型 | 工具 |
|--------|------|------|------|
| 🎬 Director | 场景分解、创意策划 | DeepSeek | — |
| ✍️ ScriptWriter | 配音脚本、幻灯片大纲 | DeepSeek | — |
| 🎨 SlideDesigner | 脚本→有效 pipeline JSON | DeepSeek | — |
| 🎙 TTSDirector | TTS voice + 视觉参数选择 | DeepSeek | — |
| 🎞 VideoProducer | 调用渲染管线出片 | — | subprocess + pipeline_adapter |
| 🔍 Critic | 视频质量评审、修订裁决 | DeepSeek | — |

### 版本演进

| # | 日期 | 变更 | 验证 |
|---|------|------|------|
| 1 | 2026-05-05 | 基础 AG2 环境 + 5 agent（Director/StylistA/StylistB/Producer/Critic） | 完成 3 场景 3 轮互审 |
| 2 | 2026-05-06 | 代码重构：提取 helper 函数、并行化 Stylist A/B | Syntax OK |
| 3 | 2026-05-10 | **v2 重构**：改为 6 agent 全编排管线（ScriptWriter/SlideDesigner/TTSDirector/VideoProducer/CriticV2） | 完整出片 45-75s |
| 4 | 2026-05-10 | 集成 ppt-agent-skills 渲染（Puppeteer, 1280×720, 五层景深设计） | 55-103 色/页 |
| 5 | 2026-05-10 | 字幕改进：黑色描边 + Heiti SC 简体字体 | 中文标点正确 |
| 6 | 2026-05-10 | TTS 升级：Edge-TTS → SiliconFlow CosyVoice2 | 墙内直连稳定 |
| 7 | 2026-05-10 | 集成 BGM 环境音 | ffmpeg 合成 |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 多智能体框架 | AG2 Beta (`autogen.beta`) |
| LLM | DeepSeek Chat API |
| TTS | SiliconFlow CosyVoice2（主） / macOS say（降级） |
| 幻灯片渲染 | Puppeteer (Chromium) 1280×720 |
| 视频合成 | ffmpeg + OpenCV |
| 字幕 | Pillow 逐帧渲染 + 黑色描边 |
| CSS 设计系统 | ppt-agent-skills 暗黑科技主题 |
| AI 背景图 | ComfyUI + SDXL（可选） |

---

## 项目结构

```
c5-video-agents/
├── README.md
├── AI_LOG.md
├── LICENSE
├── .env                         # API 密钥
├── requirements.txt
├── run_video_studio.sh          # 一键入口
├── src/
│   ├── orchestrator.py          # 🎬 主编排循环
│   ├── pipeline_adapter.py      # 🔗 ai-video-pipeline 桥接
│   ├── config.py                # ⚙️ 双模型配置
│   ├── comfyui_client.py        # 🎨 ComfyUI REST 客户端
│   └── agents/
│       ├── director.py          # 🎬 导演 Agent
│       ├── script_writer.py     # ✍️ 编剧 Agent
│       ├── slide_designer.py    # 🎨 幻灯片设计 Agent
│       ├── tts_director.py      # 🎙 TTS 导演 Agent
│       ├── producer.py          # 💼 制片人 Agent（v1 兼容）
│       ├── stylist_a.py         # 🎨 风格师 A（v1 兼容）
│       ├── stylist_b.py         # 🎨 风格师 B（v1 兼容）
│       ├── critic.py            # 🔍 评审 Agent（v1 兼容）
│       └── critic_v2.py         # 🔍 增强评审 Agent
└── output/                      # 视频输出
```

---

## 常见问题

**Q: TTS 失败怎么办？**
A: 会自动降级到 macOS `say` 命令（离线、无网络依赖）。
建议配置 `SILICONFLOW_API_KEY` 使用 CosyVoice2。

**Q: ComfyUI 必须开吗？**
A: 不需要。SDXL 背景是可选项，默认使用 CSS 设计系统。

**Q: 字幕乱码/标点位置不对？**
A: 确保 `compose.py` 中 `ImageFont.truetype` 使用 `index=1`（Heiti SC 简体）。

**Q: 幻灯片纯黑？**
A: Chrome headless 截图需要 `--default-background-color=0B1120` 参数。

---

## License

MIT License. 见 `LICENSE`。
