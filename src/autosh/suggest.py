"""Prompt builder and suggest engine."""

import platform

import httpx

from autosh.ai import ask
from autosh.config import Config

SYSTEM_PROMPT = """\
You are a shell command generator. Convert Chinese descriptions into correct CLI commands.

CRITICAL RULES:
- Output exactly 3 lines in this format: COMMAND | 中文说明
- NO markdown, NO code fences, NO ```, NO explanations before or after.
- Each line must start with a runnable shell command, then " | ", then a short (≤15 Chinese chars) description.

TOOL-SPECIFIC:
- gh + "换账户/切换账号" → gh auth switch, gh auth login, gh auth status
- gh + "发PR/提PR" → gh pr create
- git + "回退/撤销" → git reset, git revert
- git + "暂存/先存起来" → git stash
- docker + "清理" → docker system prune, docker rm
- docker + "看日志" → docker logs -f
- npm/pnpm + "换源" → npm config set registry

Safety:
- Never generate destructive commands (rm -rf /, dd, fork bombs, etc.).
- Prefer concise one-liners.
- Use flags appropriate for the detected OS.

Examples:
输入: 列出当前目录
ls -la | 详细列表显示所有文件
ls -G | 彩色显示文件列表
pwd | 显示当前目录路径

输入: gh 换账户
gh auth switch | 交互式切换 GitHub 账户
gh auth login | 重新登录新 GitHub 账户
gh auth status | 查看当前登录的账户
"""

OS_HINTS = {
    "Darwin": "The user is on macOS. Use macOS-compatible flags (e.g., ls -G for color, sed -i '' for in-place).",
    "Linux": "The user is on Linux. Use GNU-style flags (e.g., ls --color, sed -i for in-place).",
}


def suggest_multi(query: str, config: Config, client: httpx.Client | None = None) -> list[dict]:
    """Return a list of {cmd, desc} dicts."""
    if not query or not query.strip():
        return []

    os_name = platform.system()
    os_hint = OS_HINTS.get(os_name, "")
    system = SYSTEM_PROMPT
    if os_hint:
        system += f"\n\n{os_hint}"

    result = ask(query, system, config, client)
    items = []
    for line in result.split("\n"):
        line = line.strip()
        if not line or line.startswith("```") or line.startswith("Here"):
            continue
        if " | " in line:
            cmd, desc = line.split(" | ", 1)
            items.append({"cmd": cmd.strip(), "desc": desc.strip()})
        elif line and len(line) > 2:
            items.append({"cmd": line.strip(), "desc": ""})

    return items


def suggest(query: str, config: Config, client: httpx.Client | None = None) -> str:
    """Return a single shell command suggestion (first option)."""
    options = suggest_multi(query, config, client)
    return options[0]["cmd"] if options else ""
