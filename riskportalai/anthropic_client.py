"""
anthropic_client.py
Async helper to call Anthropic Claude with tool-calling.
"""

from __future__ import annotations
import os, json, httpx
from typing import List, Dict, Any

_MODEL = "claude-sonnet-4-20250514"
_API_URL = "https://api.anthropic.com/v1/messages"

# tool schema: run_simulation - SIMPLE ORIGINAL FORMAT
_TOOL_SCHEMA = {
    "name": "build_simulation_model",
    "description": "Generate graph schema for backend Monte-Carlo simulation",
    "input_schema": {
        "type": "object",
        "properties": {
            "schemaVersion": {"type": "string"},
            "nodes": {"type": "array"},
            "edges": {"type": "array"}
        },
        "required": ["schemaVersion", "nodes", "edges"]
    }
}

SYSTEM_PROMPT = open(
    os.path.join(os.path.dirname(__file__), "prompt_graph.md"),
    encoding="utf-8").read()

async def call_claude(history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Return Claude JSON or raise RuntimeError with detailed error."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("API key missing")

    # DEBUG: Log the API key being used (first 10 chars only)
    print(f"DEBUG: Using API key starting with: {api_key[:10]}...")

    payload = {
        "model": _MODEL,
        "max_tokens": 1500,
        "system": SYSTEM_PROMPT,
        "messages": history,
        "tools": [_TOOL_SCHEMA]
    }

    # No beta header - tools may be stable now
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(_API_URL, headers=headers, json=payload)

            # Better error handling - don't mask the real error
            if not resp.is_success:
                error_text = resp.text
                print(f"DETAILED ERROR: Status {resp.status_code}: {error_text}")
                raise RuntimeError(f"Anthropic API error {resp.status_code}: {error_text}")

            return resp.json()

    except httpx.RequestError as e:
        raise RuntimeError(f"Network error calling Anthropic: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error calling Anthropic: {str(e)}")
