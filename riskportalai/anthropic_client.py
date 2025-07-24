"""
anthropic_client.py
Async helper to call Anthropic Claude with tool-calling.
"""

from __future__ import annotations
import os, json, httpx
from typing import List, Dict, Any

_MODEL = "claude-sonnet-4-20250514"
_API_URL = "https://api.anthropic.com/v1/messages"

# tool schema: run_simulation
_TOOL_SCHEMA = {
    "name": "run_simulation",
    "description": "Execute Monte-Carlo on a graph scenario",
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
    """Return Claude JSON or raise RuntimeError."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("API key missing")

    payload = {
        "model": _MODEL,
        "max_tokens": 1500,
        "system": SYSTEM_PROMPT,
        "messages": history,
        "tools": [_TOOL_SCHEMA]
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "tools-2024-05-14"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()
