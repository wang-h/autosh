"""Config file management for ~/.autosh/config.yaml"""

from pathlib import Path

import yaml

PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/anthropic",
        "model": "deepseek-v4-flash",
        "format": "anthropic",
    },
    "minimax": {
        "name": "MiniMax",
        "base_url": "https://api.minimax.chat/v1",
        "model": "abab7-chat",
        "format": "openai",
    },
    "kimi": {
        "name": "Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
        "format": "openai",
    },
    "qwen": {
        "name": "Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "format": "openai",
    },
    "glm": {
        "name": "GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "format": "openai",
    },
}

DEFAULT_PROVIDER = "deepseek"

DEFAULT_CONFIG = {
    "provider": DEFAULT_PROVIDER,
    "model": PROVIDERS[DEFAULT_PROVIDER]["model"],
    "base_url": PROVIDERS[DEFAULT_PROVIDER]["base_url"],
    "api_key": "",
}


def _config_dir() -> Path:
    return Path.home() / ".autosh"


def _config_path() -> Path:
    return _config_dir() / "config.yaml"


def provider_format(provider: str) -> str:
    return PROVIDERS.get(provider, {}).get("format", "openai")


class Config:
    def __init__(self, path: Path | None = None):
        self.path = path or _config_path()
        self.data: dict = {}
        self.load()

    def load(self):
        if self.path.exists():
            with open(self.path) as f:
                self.data = yaml.safe_load(f) or {}
        for k, v in DEFAULT_CONFIG.items():
            self.data.setdefault(k, v)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            yaml.dump(self.data, f, allow_unicode=True, default_flow_style=False)

    def get(self, key: str) -> str:
        return str(self.data.get(key, DEFAULT_CONFIG.get(key, "")))

    def set(self, key: str, value: str):
        if key == "provider" and value in PROVIDERS:
            preset = PROVIDERS[value]
            self.data["provider"] = value
            self.data["model"] = preset["model"]
            self.data["base_url"] = preset["base_url"]
        else:
            self.data[key] = value
        self.save()

    def display(self) -> str:
        lines = []
        for k in DEFAULT_CONFIG:
            v = self.data.get(k, DEFAULT_CONFIG[k])
            if k == "api_key":
                v = _mask(v)
            lines.append(f"{k} = {v}")
        return "\n".join(lines)


def _mask(value: str) -> str:
    if not value:
        return "(not set)"
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "*" * (len(value) - 8) + value[-4:]
