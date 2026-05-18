import os

import httpx

_URL = "https://openrouter.ai/api/v1/chat/completions"
_MODEL = "openai/gpt-oss-120b:free"


def call_ai(messages: list[dict]) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    response = httpx.post(
        _URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": _MODEL, "messages": messages},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
