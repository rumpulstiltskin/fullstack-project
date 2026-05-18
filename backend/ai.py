import json
import os
import re

import httpx

from models import AIResponse, BoardData, ChatMessage

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


def _build_system_prompt(board: BoardData) -> str:
    board_json = board.model_dump_json(indent=2)
    return f"""You are a Kanban board assistant helping the user manage their tasks.

Current board state:
{board_json}

IMPORTANT: Respond ONLY with a valid JSON object. No preamble, no markdown, no text outside the JSON.

Response format when the board does not change:
{{"message": "Your helpful response", "board_update": null}}

Response format when the board should change:
{{"message": "Confirmation of the change", "board_update": {{"columns": [{{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-abc123"]}}], "cards": {{"card-abc123": {{"id": "card-abc123", "title": "Card title", "details": "Details"}}}}}}}}

Rules for board_update:
- Include ALL columns and ALL cards, even unchanged ones
- Preserve existing column IDs and card IDs exactly
- New cards need a unique ID like "card-" followed by 6 random alphanumeric characters
- Set board_update to null for questions or anything that does not change the board"""


def _extract_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        return match.group(1)
    return text.strip()


def call_ai_structured(board: BoardData, messages: list[ChatMessage]) -> AIResponse:
    system_prompt = _build_system_prompt(board)
    all_messages: list[dict] = [{"role": "system", "content": system_prompt}]
    all_messages += [{"role": m.role, "content": m.content} for m in messages]

    raw = call_ai(all_messages)
    try:
        data = json.loads(_extract_json(raw))
        return AIResponse(**data)
    except (json.JSONDecodeError, Exception) as e:
        raise RuntimeError(f"AI returned invalid response: {e}\n\nRaw: {raw}")
