"""
riskportalai.main
Single-process FastAPI server:
• Serves the frontend (index.html, styles.css) from /frontend
• /health  – health check
• /graph_simulate – run Monte-Carlo
• /chat   – forwards to Claude Sonnet-4 (tool-calling) or stub if key missing
"""

from __future__ import annotations
import os, pathlib, dotenv
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .graph_simulate import simulate_graph
from .anthropic_client import call_claude

# ───────────────────────────────────────────────────────────────
# Load .env (ANTHROPIC_API_KEY) at startup
# ───────────────────────────────────────────────────────────────
dotenv.load_dotenv()

# ───────────────────────────────────────────────────────────────
# FastAPI app
# ───────────────────────────────────────────────────────────────
app = FastAPI(title="RiskPortal-AI", version="0.0.1")

# Serve static frontend  (index.html, styles.css)  →  http://localhost:8000/
static_dir = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

# ───────────────────  /health  ─────────────────────────────────
@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "version": app.version}

# ───────────────────  /graph_simulate  ─────────────────────────
@app.post("/graph_simulate")
async def graph_simulate_endpoint(payload: Dict[str, Any]):
    """
    Accepts graph JSON and returns Monte-Carlo statistics.
    """
    try:
        return simulate_graph(payload, iterations=10_000)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

# ───────────────────  /chat  ───────────────────────────────────
class ChatMsg(BaseModel):
    role: str          # "user" | "assistant"
    content: str

class ChatPayload(BaseModel):
    history: List[ChatMsg]

@app.post("/chat")
async def chat_endpoint(payload: ChatPayload):
    """
    Forwards message history to Claude Sonnet-4 with tool-calling.
    Falls back to a stub reply if ANTHROPIC_API_KEY is missing.
    """
    if "ANTHROPIC_API_KEY" not in os.environ:
        # stub response so you can develop without a key
        last_user = next((m.content for m in reversed(payload.history)
                          if m.role == "user"), "")
        return {"type": "text",
                "content": f"(stub) You said: {last_user}. "
                           "Add ANTHROPIC_API_KEY to .env for live Claude."}

    try:
        claude_json = await call_claude([m.model_dump() for m in payload.history])
        content = claude_json.get("content", [{}])[0]

        # If Claude invoked the run_simulation tool
        if content.get("type") == "tool_use":
            scenario = content["input"]
            sim_out = simulate_graph(scenario, iterations=10_000)
            return {"type": "json", "content": sim_out}

        # Otherwise plain text answer
        return {"type": "text", "content": content.get("text", "")}

    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
