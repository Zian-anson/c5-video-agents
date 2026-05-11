#!/usr/bin/env bash
# ═══════════════════════════════════════════════
# AG2 Multi-Agent Video Studio — 一键入口
# C5 AG2 + ai-video-pipeline 结合
# ═══════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Use the .venv312 (Python 3.12 + AG2 Beta)
VENV="$SCRIPT_DIR/.venv312"
if [ ! -f "$VENV/bin/python3" ]; then
    echo "❌ 未找到 .venv312 虚拟环境!"
    echo "   请先在 c5-video-agents 项目中创建:"
    echo "   python3.12 -m venv .venv312"
    echo "   source .venv312/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   pip install git+https://github.com/ag2ai/ag2.git"
    exit 1
fi

# Activate venv
source "$VENV/bin/activate"

# Set proxy
export https_proxy=http://127.0.0.1:7897

cd "$SCRIPT_DIR"

echo "🎬 AG2 Multi-Agent Video Studio"
echo "   Python: $(python3 --version)"
echo "   CWD: $SCRIPT_DIR"
echo ""

# Run orchestrator
exec python3 -m src.orchestrator "$@"
