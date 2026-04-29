#!/usr/bin/env bash
set -e

# AutoSH one-line installer
# curl -fsSL https://wang-h.github.io/autosh/install.sh | bash

GREEN='\033[1;32m'
CYAN='\033[1;36m'
NC='\033[0m'

echo -e "${GREEN}"
echo "   ▄▄▄      █    █▄▄▄▄ ▄▄▄▄▄"
echo "  █   █    █ █   █  ▄▄ █     "
echo "  █▀▀▀█   █   █  █▄▄█  █▄▄▄▄ "
echo "  █   █  █     █ █         █"
echo "  █   █  █▄▄▄▄▄█ █▄▄▄▄ █▄▄▄█"
echo -e "${NC}"
echo "  AutoSH — 一句中文，秒出命令"
echo

# Check Python
if command -v python3 &>/dev/null; then
    PY=$(python3 -c 'import sys; print("ok") if sys.version_info >= (3,11) else sys.exit(1)' 2>/dev/null && echo "python3" || echo "")
elif command -v python &>/dev/null; then
    PY=$(python -c 'import sys; print("ok") if sys.version_info >= (3,11) else sys.exit(1)' 2>/dev/null && echo "python" || echo "")
fi

if [[ -z "$PY" ]]; then
    echo "AutoSH 需要 Python 3.11+，请先安装: https://www.python.org"
    exit 1
fi

echo -e "${CYAN}→ 安装 autosh...${NC}"

if command -v uv &>/dev/null; then
    uv tool install autosh
elif command -v pip3 &>/dev/null; then
    pip3 install autosh
else
    $PY -m pip install autosh
fi

echo -e "${CYAN}→ 初始化...${NC}"

if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *zsh* ]]; then
    ah init zsh
elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *bash* ]]; then
    ah init bash
else
    ah init zsh
fi

echo
echo -e "${GREEN}搞定了！${NC}"
echo
echo "  1. 配 API Key:   ah config set api_key <你的key>"
echo "  2. 选模型:       ah config set provider deepseek"
echo "  3. 重载 shell:   source ~/.zshrc"
echo
echo "  Ctrl+/       → 极速出命令"
echo "  Ctrl+Shift+/ → 三选一"
echo
