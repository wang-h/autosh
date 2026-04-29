"""Local AutoSH daemon used to keep suggestion code warm."""

from __future__ import annotations

import json
import os
import signal
import socket
import socketserver
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SOCKET_NAME = "daemon.sock"
PID_NAME = "daemon.pid"
LOG_NAME = "daemon.log"
_HTTP_CLIENT = None


class DaemonError(Exception):
    pass


class DaemonResponseError(DaemonError):
    pass


def autosh_dir() -> Path:
    return Path.home() / ".autosh"


def socket_path() -> Path:
    return autosh_dir() / SOCKET_NAME


def pid_path() -> Path:
    return autosh_dir() / PID_NAME


def log_path() -> Path:
    return autosh_dir() / LOG_NAME


def request(payload: dict[str, Any], timeout: float = 35.0, autostart: bool = True) -> dict[str, Any]:
    if autostart:
        ensure_running()

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect(str(socket_path()))
            data = json.dumps(payload, ensure_ascii=False).encode() + b"\n"
            sock.sendall(data)
            return _read_response(sock)
    except OSError as exc:
        raise DaemonError(str(exc)) from exc


def suggest(query: str, multi: bool) -> list[dict[str, str]]:
    resp = request({"op": "suggest", "query": query, "multi": multi})
    if not resp.get("ok"):
        raise DaemonResponseError(str(resp.get("error") or "daemon request failed"))
    items = resp.get("items") or []
    return [{"cmd": str(i.get("cmd", "")), "desc": str(i.get("desc", ""))} for i in items]


def ensure_running() -> None:
    if is_running():
        return
    start()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        if is_running():
            return
        time.sleep(0.05)
    raise DaemonError(f"daemon did not start; see {log_path()}")


def is_running() -> bool:
    path = socket_path()
    if not path.exists():
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            sock.connect(str(path))
            sock.sendall(b'{"op":"ping"}\n')
            resp = _read_response(sock)
            return bool(resp.get("ok"))
    except (OSError, DaemonError, json.JSONDecodeError):
        return False


def start() -> None:
    autosh_dir().mkdir(parents=True, exist_ok=True)
    if socket_path().exists() and not is_running():
        socket_path().unlink()

    with open(log_path(), "ab") as log:
        subprocess.Popen(
            [sys.executable, "-m", "autosh.daemon", "serve"],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )


def stop() -> bool:
    pid_file = pid_path()
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, signal.SIGTERM)
    except (OSError, ValueError):
        return False
    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        if not is_running():
            break
        time.sleep(0.05)
    for p in (socket_path(), pid_file):
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    return True


def serve() -> None:
    autosh_dir().mkdir(parents=True, exist_ok=True)
    path = socket_path()
    if path.exists():
        path.unlink()
    pid_path().write_text(str(os.getpid()))

    class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
        daemon_threads = True
        allow_reuse_address = True

    server = Server(str(path), _Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        for p in (path, pid_path()):
            try:
                p.unlink()
            except FileNotFoundError:
                pass


class _Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        line = self.rfile.readline(65536)
        try:
            payload = json.loads(line.decode())
            response = _handle_payload(payload)
        except Exception as exc:
            response = {"ok": False, "error": str(exc)}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode() + b"\n")


def _handle_payload(payload: dict[str, Any]) -> dict[str, Any]:
    op = payload.get("op")
    if op == "ping":
        return {"ok": True}
    if op != "suggest":
        return {"ok": False, "error": f"unknown op: {op}"}

    query = str(payload.get("query") or "")
    multi = bool(payload.get("multi"))
    if not query.strip():
        return {"ok": True, "items": []}

    import httpx

    from autosh.config import Config
    from autosh.suggest import suggest, suggest_multi

    config = Config()
    api_key = config.get("api_key")
    if not api_key:
        return {"ok": False, "error": "no API key configured"}

    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        _HTTP_CLIENT = httpx.Client()
    if multi:
        items = suggest_multi(query, config, _HTTP_CLIENT)
    else:
        cmd = suggest(query, config, _HTTP_CLIENT)
        items = [{"cmd": cmd, "desc": ""}] if cmd else []
    return {"ok": True, "items": items}


def _read_response(sock: socket.socket) -> dict[str, Any]:
    chunks = []
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
        if b"\n" in chunk:
            break
    if not chunks:
        raise DaemonError("empty daemon response")
    return json.loads(b"".join(chunks).split(b"\n", 1)[0].decode())


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
        return
    print("usage: python -m autosh.daemon serve", file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
