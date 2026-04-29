#!/usr/bin/env bash
set -e

# AutoSH one-line installer
# curl -fsSL https://wang-h.github.io/autosh/install.sh | bash

GREEN='\033[1;32m'
CYAN='\033[1;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

printf '%b\n' "${GREEN}╭────────────────────────────╮${NC}"
printf '%b\n' "${GREEN}│${NC} ${BOLD}AutoSH${NC} ${DIM}/ ah${NC}                 ${GREEN}│${NC}"
printf '%b\n' "${GREEN}│${NC} ${CYAN}一句中文，秒出命令${NC}       ${GREEN}│${NC}"
printf '%b\n' "${GREEN}╰────────────────────────────╯${NC}"
printf '\n'

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

echo -e "${CYAN}→ 安装 autosh-ah...${NC}"

if command -v uv &>/dev/null; then
    uv tool install autosh-ah
elif command -v pip3 &>/dev/null; then
    pip3 install -i https://pypi.org/simple autosh-ah
else
    $PY -m pip install -i https://pypi.org/simple autosh-ah
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

prompt_tty() {
    local __name="$1"
    local __prompt="$2"
    local __secret="${3:-0}"
    local __value=""
    if [[ -e /dev/tty ]]; then
        printf '%s' "$__prompt" >/dev/tty
        if [[ "$__secret" == "1" ]]; then
            read -r -s __value </dev/tty || true
            printf '\n' >/dev/tty
        else
            read -r __value </dev/tty || true
            printf '\n' >/dev/tty
        fi
    fi
    printf -v "$__name" '%s' "$__value"
}

choose_provider() {
    local -a providers=("deepseek" "kimi" "minimax" "qwen" "glm")
    local -a labels=("deepseek (default)" "kimi" "minimax" "qwen" "glm")
    local choice=""
    local idx=0
    if [[ -e /dev/tty ]]; then
        printf '%b\n' "${CYAN}→ 先选模型，再配置 Key...${NC}" >/dev/tty
        local i
        for i in "${!labels[@]}"; do
            printf '  %1d) %s\n' "$((i + 1))" "${labels[$i]}" >/dev/tty
        done
        printf '\n' >/dev/tty
        printf '  请选择 [1-5, Enter=1]: ' >/dev/tty
        read -r choice </dev/tty || true
        printf '\n' >/dev/tty
    fi
    case "$choice" in
        2) idx=1 ;;
        3) idx=2 ;;
        4) idx=3 ;;
        5) idx=4 ;;
        *) idx=0 ;;
    esac
    printf '%s' "${providers[$idx]}"
}

PROVIDER="$(choose_provider)"
API_KEY=""
prompt_tty API_KEY "  API Key (Enter 跳过): " 1
if [[ -n "$PROVIDER" ]]; then
    ah config set provider "$PROVIDER" >/dev/null 2>&1 || true
fi
if [[ -n "$API_KEY" ]]; then
    ah config set api_key "$API_KEY" >/dev/null 2>&1 || true
fi

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
echo "  选择的模型:      $PROVIDER"
if [[ -n "$API_KEY" ]]; then
    echo "  API Key:         已配置"
else
    echo "  API Key:         跳过了"
fi
echo
echo "  Ctrl+G  → 极速出命令"
echo "  Ctrl+/  → 三选一（部分终端用 Ctrl+_）"
echo
echo -e "${CYAN}觉得好用？点个 Star ⭐ 支持一下${NC}"
STAR_ANS=""
prompt_tty STAR_ANS "  (Y/n) "
if [[ "$STAR_ANS" != "n" && "$STAR_ANS" != "N" ]]; then
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        gh api -X PUT user/starred/wang-h/autosh 2>/dev/null && echo -e "  ${GREEN}已 Star！感谢 🎉${NC}" || echo "  已打开: https://github.com/wang-h/autosh"
    elif command -v open &>/dev/null; then
        open "https://github.com/wang-h/autosh"
    else
        echo "  https://github.com/wang-h/autosh"
    fi
fi
echo
