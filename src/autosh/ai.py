"""AI client — supports Anthropic and OpenAI-compatible APIs."""

import httpx

from autosh.config import provider_format


class AIError(Exception):
    pass


def ask(prompt: str, system: str, config, client: httpx.Client | None = None) -> str:
    fmt = provider_format(config.get("provider"))
    if fmt == "anthropic":
        return _ask_anthropic(prompt, system, config, client)
    return _ask_openai(prompt, system, config, client)


def _ask_anthropic(prompt: str, system: str, config, client: httpx.Client | None = None) -> str:
    url = f"{config.get('base_url').rstrip('/')}/v1/messages"
    headers = {
        "x-api-key": config.get("api_key"),
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    body = {
        "model": config.get("model"),
        "max_tokens": 200,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "thinking": {"type": "disabled"},
    }

    transport = client or httpx
    resp = transport.post(url, json=body, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    for block in data["content"]:
        if block.get("type") == "text":
            return block["text"].strip()
    return ""


def _ask_openai(prompt: str, system: str, config, client: httpx.Client | None = None) -> str:
    url = f"{config.get('base_url').rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.get('api_key')}",
        "Content-Type": "application/json",
    }

    body = {
        "model": config.get("model"),
        "max_tokens": 200,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    transport = client or httpx
    resp = transport.post(url, json=body, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
