# AutoSH bash integration
# Source this file in your .bashrc: source ~/.autosh/autosh.bash

_autosh_suggest() {
    local buffer="$READLINE_LINE"
    if [[ -z "$buffer" ]]; then
        return
    fi
    local suggestion
    suggestion=$(autosh suggest "$buffer" 2>/dev/null)
    if [[ -n "$suggestion" && "$suggestion" != "$buffer" ]]; then
        READLINE_LINE="$suggestion"
        READLINE_POINT=${#READLINE_LINE}
    fi
}

# Ctrl+/: trigger AutoSH suggestion
bind -x '"\C-_": _autosh_suggest'
