# AutoSH zsh integration
# Source this file in your .zshrc: source ~/.autosh/autosh.zsh
#
# Ctrl+G       : 极速 — 直接出命令，一步到位
# Ctrl+/       : 选择 — 弹出 3 个候选，带中文解释
# Ctrl+_       : 选择 — Ctrl+/ 的终端等价按键

_autosh_fast() {
    local buffer="$BUFFER"
    if [[ -z "$buffer" ]]; then
        return
    fi
    local result
    if [[ -n "$AUTOSH_DEBUG" ]]; then
        result=$(autosh suggest "$buffer")
    else
        result=$(autosh suggest "$buffer" 2>/dev/null)
    fi
    if [[ -n "$result" && "$result" != "$buffer" ]]; then
        BUFFER="$result"
        zle end-of-line
    fi
}

_autosh_pick() {
    local buffer="$BUFFER"
    if [[ -z "$buffer" ]]; then
        return
    fi

    echo
    local IFS=$'\n'
    local raw
    if [[ -n "$AUTOSH_DEBUG" ]]; then
        raw=(${(f)"$(autosh suggest --multi "$buffer")"})
    else
        raw=(${(f)"$(autosh suggest --multi "$buffer" 2>/dev/null)"})
    fi

    if [[ ${#raw} -eq 0 ]]; then
        zle reset-prompt
        return
    fi

    local -a cmds
    local i=1
    for line in "${raw[@]}"; do
        if [[ "$line" == *" | "* ]]; then
            local cmd="${line%% | *}"
            local desc="${line#* | }"
            cmds+=("$cmd")
            printf "  \033[1;33m[%d]\033[0m \033[1;32m%s\033[0m  \033[90m%s\033[0m\n" "$i" "$cmd" "$desc"
        elif [[ -n "$line" ]]; then
            cmds+=("$line")
            printf "  \033[1;33m[%d]\033[0m \033[1;32m%s\033[0m\n" "$i" "$line"
        fi
        ((i++))
    done

    echo -n "  Enter=1, 1-${#cmds}: "
    local key
    read -k key
    echo

    # Enter defaults to [1]
    if [[ "$key" == $'\r' || "$key" == "1" ]]; then
        BUFFER="${cmds[1]}"
        zle end-of-line
    elif [[ "$key" -ge 2 && "$key" -le ${#cmds} ]]; then
        BUFFER="${cmds[$key]}"
        zle end-of-line
    fi
    zle reset-prompt
}

zle -N autosh-fast _autosh_fast
zle -N autosh-pick _autosh_pick

bindkey -M main '^G' autosh-fast
bindkey -M emacs '^G' autosh-fast
bindkey -M viins '^G' autosh-fast
bindkey -M vicmd '^G' autosh-fast
bindkey -M main '^_' autosh-pick
bindkey -M emacs '^_' autosh-pick
bindkey -M viins '^_' autosh-pick
bindkey -M vicmd '^_' autosh-pick
