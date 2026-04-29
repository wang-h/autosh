# AutoSH bash integration
# Source this file in your .bashrc: source ~/.autosh/autosh.bash
#
# Ctrl+G       : 极速 — 直接出命令，一步到位
# Ctrl+/       : 选择 — 弹出 3 个候选，带中文解释
# Ctrl+_       : 选择 — Ctrl+/ 的终端等价按键

_autosh_fast() {
    local buffer="$READLINE_LINE"
    if [[ -z "$buffer" ]]; then
        return
    fi
    local suggestion
    if [[ -n "$AUTOSH_DEBUG" ]]; then
        suggestion=$(autosh suggest "$buffer")
    else
        suggestion=$(autosh suggest "$buffer" 2>/dev/null)
    fi
    if [[ -n "$suggestion" && "$suggestion" != "$buffer" ]]; then
        READLINE_LINE="$suggestion"
        READLINE_POINT=${#READLINE_LINE}
    fi
}

_autosh_pick() {
    local buffer="$READLINE_LINE"
    if [[ -z "$buffer" ]]; then
        return
    fi

    printf "\n"
    local raw line cmd desc key
    local -a cmds
    local i=1
    if [[ -n "$AUTOSH_DEBUG" ]]; then
        mapfile -t raw < <(autosh suggest --multi "$buffer")
    else
        mapfile -t raw < <(autosh suggest --multi "$buffer" 2>/dev/null)
    fi

    if [[ ${#raw[@]} -eq 0 ]]; then
        return
    fi

    for line in "${raw[@]}"; do
        if [[ "$line" == *" | "* ]]; then
            cmd="${line%% | *}"
            desc="${line#* | }"
            cmds+=("$cmd")
            printf "  \033[1;33m[%d]\033[0m \033[1;32m%s\033[0m  \033[90m%s\033[0m\n" "$i" "$cmd" "$desc"
        elif [[ -n "$line" ]]; then
            cmds+=("$line")
            printf "  \033[1;33m[%d]\033[0m \033[1;32m%s\033[0m\n" "$i" "$line"
        fi
        ((i++))
    done

    printf "  Enter=1, 1-%d: " "${#cmds[@]}"
    IFS= read -rsn1 key
    printf "\n"

    if [[ -z "$key" || "$key" == "1" ]]; then
        READLINE_LINE="${cmds[0]}"
    elif [[ "$key" =~ ^[2-9]$ && "$key" -le ${#cmds[@]} ]]; then
        READLINE_LINE="${cmds[$((key - 1))]}"
    else
        return
    fi
    READLINE_POINT=${#READLINE_LINE}
}

bind -m emacs -x '"\C-g": _autosh_fast'
bind -m vi-insert -x '"\C-g": _autosh_fast'
bind -m vi-command -x '"\C-g": _autosh_fast'
bind -m emacs -x '"\C-_": _autosh_pick'
bind -m vi-insert -x '"\C-_": _autosh_pick'
bind -m vi-command -x '"\C-_": _autosh_pick'
