"""Doctor: diagnostic checks for AutoSH setup."""

import sys
import termios
import tty
from pathlib import Path

import httpx

from autosh.config import Config


EXPECTED_KEYS = {
    "Ctrl+G (fast)": [b"\x07"],
    "Ctrl+/ or Ctrl+_ (pick)": [b"\x1f"],
}


def run(keys: bool = False):
    print("AutoSH Doctor")
    print("==============")
    if keys:
        _run_key_test()
        print("")

    ok = 0
    warn = 0
    fail = 0

    def check(label: str, condition: bool, detail: str = "") -> bool:
        nonlocal ok, warn, fail
        if condition:
            ok += 1
            print(f"  ✓ {label}")
        else:
            fail += 1
            print(f"  ✗ {label}")
            if detail:
                print(f"    → {detail}")
        return condition

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    check(f"Python {py_ver} (>= 3.11 required)", py_ok,
          "Python 3.11 or later is required. Install from https://www.python.org/")

    # Config file
    config_path = Path.home() / ".autosh" / "config.yaml"
    config_exists = config_path.exists()
    check(f"Config file: {config_path}", config_exists,
          "Run `autosh init zsh` or `autosh init bash` to create it.")

    if not config_exists:
        print(f"\n  Result: {ok} OK, {fail} failed")
        return

    config = Config()

    # API key
    api_key = config.get("api_key")
    has_key = bool(api_key)
    check("API key configured", has_key,
          "Run `autosh config set api_key <your-key>`")

    # Connectivity
    if has_key:
        base = config.get("base_url").rstrip("/")
        try:
            resp = httpx.post(
                f"{base}/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": config.get("model"),
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "."}],
                },
                timeout=10,
            )
            alive = resp.status_code in (200, 401, 403)
            check(f"API reachable: {base}", alive,
                  f"HTTP {resp.status_code}")
        except Exception as e:
            check(f"API reachable: {base}", False, str(e))
    else:
        base = config.get("base_url").rstrip("/")
        print(f"  ? API connectivity: skipped (no api_key)")

    # Shell integration
    zsh_script = Path.home() / ".autosh" / "autosh.zsh"
    bash_script = Path.home() / ".autosh" / "autosh.bash"
    if zsh_script.exists():
        check(f"Zsh integration: {zsh_script}", True)
    else:
        print(f"  ? Zsh integration: not installed (run `autosh init zsh`)")
    if bash_script.exists():
        check(f"Bash integration: {bash_script}", True)
    else:
        print(f"  ? Bash integration: not installed (run `autosh init bash`)")

    print(f"\n  Result: {ok} OK, {fail} failed")
    if fail > 0:
        print("  Run `autosh init <shell>` to create config and shell scripts.")


def _run_key_test():
    if not sys.stdin.isatty():
        print("  ? Key test: skipped (stdin is not a TTY)")
        return

    print("  Key test")
    print("  --------")
    print("  Press the requested shortcut when prompted. Press Esc to skip.")
    for label, expected in EXPECTED_KEYS.items():
        data = _read_key(f"  {label}: ")
        display = _format_bytes(data)
        matched = data in expected
        status = "OK" if matched else "not matched"
        print(f"    received: {display} ({status})")
        if not matched:
            expected_display = " or ".join(_format_bytes(item) for item in expected)
            print(f"    expected: {expected_display}")


def _read_key(prompt: str) -> bytes:
    print(prompt, end="", flush=True)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        data = bytes([sys.stdin.buffer.read(1)[0]])
        # Alt/meta and enhanced keyboard sequences arrive as ESC-prefixed bytes.
        if data == b"\x1b":
            while True:
                rlist, _, _ = __import__("select").select([sys.stdin], [], [], 0.08)
                if not rlist:
                    break
                chunk = sys.stdin.buffer.read(1)
                if not chunk:
                    break
                data += chunk
        return data
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        print("")


def _format_bytes(data: bytes) -> str:
    if not data:
        return "(none)"
    parts = []
    for b in data:
        if b == 0x1B:
            parts.append("Esc")
        elif b < 0x20:
            parts.append("^" + chr(b + 0x40))
        elif b == 0x7F:
            parts.append("^?")
        else:
            parts.append(chr(b))
    hexed = " ".join(f"{b:02x}" for b in data)
    return f"{''.join(parts)} [{hexed}]"
