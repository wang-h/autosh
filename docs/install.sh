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

# Detect shell
if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *zsh* ]]; then
    SHELL_TYPE="zsh"
    RC_FILE="$HOME/.zshrc"
    SOURCE_LINE="source ~/.autosh/autosh.zsh  # AutoSH"
elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *bash* ]]; then
    SHELL_TYPE="bash"
    RC_FILE="$HOME/.bashrc"
    SOURCE_LINE="source ~/.autosh/autosh.bash  # AutoSH"
else
    SHELL_TYPE="zsh"
    RC_FILE="$HOME/.zshrc"
    SOURCE_LINE="source ~/.autosh/autosh.zsh  # AutoSH"
fi

echo -e "${CYAN}→ 初始化 ${SHELL_TYPE}...${NC}"
ah init "$SHELL_TYPE"

# Auto-append source line to rc file
if ! grep -qF "$SOURCE_LINE" "$RC_FILE" 2>/dev/null; then
    echo "$SOURCE_LINE" >> "$RC_FILE"
    echo -e "${CYAN}→ 已追加到 ${RC_FILE}${NC}"
else
    echo -e "${CYAN}→ ${RC_FILE} 已有 AutoSH，跳过${NC}"
fi

# Source it right now
if [[ "$SHELL_TYPE" == "zsh" ]]; then
    source ~/.autosh/autosh.zsh 2>/dev/null || true
else
    source ~/.autosh/autosh.bash 2>/dev/null || true
fi

echo
echo -e "${GREEN}搞定了！${NC}"
echo
echo "  配 Key 选模型:   ah config set api_key <你的key>"
echo "                   ah config set provider deepseek"
echo
echo "  Ctrl+/       → 极速出命令"
echo "  Ctrl+Shift+/ → 三选一"
echo
echo -e "${CYAN}觉得好用？点个 Star ⭐ 支持一下${NC}"
echo -n "  (Y/n) "
read -r ans
if [[ "$ans" != "n" && "$ans" != "N" ]]; then
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        gh api -X PUT user/starred/wang-h/autosh 2>/dev/null && echo -e "  ${GREEN}已 Star！感谢 🎉${NC}" || echo "  已打开: https://github.com/wang-h/autosh"
    elif command -v open &>/dev/null; then
        open "https://github.com/wang-h/autosh"
    else
        echo "  https://github.com/wang-h/autosh"
    fi
fi
echo
