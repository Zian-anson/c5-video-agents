# 星尘视频工坊 · Stardust Video Studio

> 5 个 AG2 Beta 智能体协作生成 AI 视频提示词，双模型对抗 + 3 轮互审循环。

**赛道：** `multi-agent`
**基座 / Fork 来源：** [Mesh Shield](https://github.com/roshaninfordham/meshshieldai) — 参考其 AG2 Beta adapter 和流水线架构
**AG2 版本：** `ag2 ==0.12.2` (Beta · `autogen.beta`)

---

## 一句话定位

**输入：** 一个视频创意描述（如"赛博朋克城市夜景"）
**输出：** 3 个场景的 AI 视频生成提示词 + Critic 评分意见

**核心创新：** 让两个使用**不同大模型**的 Prompt Engineer 智能体（DeepSeek 电影感 vs MiniMax 极简风）互相审查、迭代 3 轮，由 Producer 智能体拍板，最后 Critic 评审质量。这模拟了真实视频制作中的"创意分歧 → 制片人决策"流程。

---

## 5 分钟跑起来

```bash
# 1. 克隆
git clone https://github.com/Zian-anson/c5-video-agents.git
cd c5-video-agents

# 2. Python 环境（需要 Python 3.10+）
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install git+https://github.com/ag2ai/ag2.git   # AG2 Beta (main 分支)

# 3. 配置 API 密钥
# 编辑 .env 填入以下内容：
# DEEPSEEK_API_KEY=sk-xxx
# DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
# MINIMAX_CN_API_KEY=sk-xxx
# MINIMAX_CN_BASE_URL=https://api.minimaxi.com/v1

# 4. 运行
source .venv/bin/activate
python3 main.py
```

首次运行预期输出：
```
🎬 Multi-Agent Video Studio
   A team of AI agents collaborating on video generation

ComfyUI: ✅ Running / ⏹️ Not running (will simulate)

🎥 What video do you want to create? > 一段15秒赛博朋克城市夜景预告片
...
✅ Created 3 scene prompts
✅ 3 rounds of A↔B mutual review per scene
✅ 3 video prompts ready for generation
```

---

## 多智能体架构

```
用户输入
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 🎬 导演 (Director)                                    │
│  DeepSeek · 拆解需求为 2-3 个场景                       │
└──────────────────────┬───────────────────────────────┘
                       ▼
    对每个场景执行 3 轮对抗审查：
     ┌──────────────────────┐
     │  Round 1: A写 → B写  │
     │  → Producer评估+反馈  │
     ├──────────────────────┤
     │  Round 2: A修改→B修改 │
     │  → Producer再评估     │
     ├──────────────────────┤
     │  Round 3: 终版       │
     │  → Producer宣布胜者   │
     └──────────┬───────────┘
                ▼
┌──────────────────────────────────────────────────────┐
│ 🎥 ComfyUI (localhost:8188)                           │
│   Kling / Minimax / Wan API 视频生成                  │
└──────────────────────┬───────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│ 🔍 评审 (Critic)                                      │
│   DeepSeek · 打分0-10 · PASS/REVISE/FAIL              │
└──────────────────────────────────────────────────────┘
```

| 智能体 | 角色 | 模型 | 工具 |
|--------|------|------|------|
| 🎬 导演 Director | 拆解视频需求为场景 | DeepSeek | — |
| 🎨 风格师A Stylist A | 电影感/戏剧化提示词 | **DeepSeek** | — |
| 🎨 风格师B Stylist B | 极简/现代提示词 | **MiniMax M2.7** | — |
| 💼 制片人 Producer | 评估双方、给反馈、选胜者 | DeepSeek | — |
| 🔍 评审 Critic | 终审质量、打分 | DeepSeek | — |
| 🎥 ComfyUI | 视频生成引擎 | — | REST API |

---

## 现场演示

- **Demo:** 本地运行 `python3 main.py`
- **视频:** [待录制] 60-90 秒 demo
- **缩略图:** [待添加]

---

## 项目结构

```
c5-video-agents/
├── README.md                    # 本文件
├── AI_LOG.md                    # AI 迭代记录（8轮）✅
├── ATTRIBUTION.md               # 拿来主义声明 ✅
├── LICENSE                      # MIT ✅
├── .env                         # API 密钥（不上传）
├── .gitignore                   # ✅
├── requirements.txt             # ✅
├── main.py                      # 🎬 主入口
├── src/
│   ├── config.py                # 双模型配置
│   ├── comfyui_client.py        # ComfyUI REST 客户端
│   └── agents/
│       ├── director.py          # 导演智能体
│       ├── stylist_a.py         # 电影感风格师 (DeepSeek)
│       ├── stylist_b.py         # 极简风风格师 (MiniMax)
│       ├── producer.py          # 制片人智能体
│       └── critic.py            # 评审智能体
└── test_*.py                    # 3 个连通性测试
```

---

## 技术栈

- **AG2 Beta** (`autogen.beta`) — 多智能体框架
- **Python 3.10+** (3.12 推荐)
- **DeepSeek API** — Stylist A / Director / Producer / Critic
- **MiniMax API** — Stylist B（不同模型保证观点多样性）
- **ComfyUI** — 视频生成引擎（localhost:8188, 可选）

---

## 测试

```bash
# 环境连通性
python3 test_ag2_beta.py      # DeepSeek + AG2 Beta
python3 test_minimax.py       # MiniMax + AG2 Beta
python3 test_multiagent.py    # 双模型 agent-as-tool

# 完整流水线
python3 main.py
```

---

## 常见问题

- **`ModuleNotFoundError: No module named 'autogen.beta'`** — 需要从 GitHub main 分支安装：`pip install git+https://github.com/ag2ai/ag2.git`（Python ≥ 3.10）
- **MiniMax 输出包含 `<think>` 标签** — 这是正常现象，代码会自动剥离。不影响最终输出
- **没有 ComfyUI** — 流水线仍可运行（simulate 模式），会展示完整的多智能体协作流程但跳过实际视频生成
- **API 密钥错误** — 检查 `.env` 中的 `DEEPSEEK_API_KEY` 和 `MINIMAX_CN_API_KEY`

---

## License

MIT License. 见 `LICENSE`。

## 致谢

- AG2 团队 (Qingyun Wu, Vasiliy Radostev)
- Mesh Shield 项目 (roshaninfordham/meshshieldai) — AG2 Beta 架构参考
- Elite20 C5-AG2 挑战框架
