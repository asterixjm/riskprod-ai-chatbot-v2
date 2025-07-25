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

# ───────────────────────────────────────────────────────────────
# Enhanced validation function
# ───────────────────────────────────────────────────────────────
def validate_scenario_enhanced(scenario: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Enhanced validation with specific edge targeting checks."""
    errors = []

    # Extract node info
    nodes = {n["id"]: n for n in scenario.get("nodes", [])}
    parameter_ids = {nid for nid, node in nodes.items() if node.get("type") == "parameter"}
    expression_ids = {nid for nid, node in nodes.items() if node.get("type") in ("expression", "result")}

    # Validate edges target parameters only
    for edge in scenario.get("edges", []):
        target = edge.get("target")
        if not target:
            errors.append("Edge missing 'target' field")
            continue

        if target not in nodes:
            errors.append(f"Edge targets non-existent node '{target}'")
            continue

        # CRITICAL CHECK: Edge must target parameter only
        if target in expression_ids:
            node_type = nodes[target].get("type", "unknown")
            errors.append(
                f"Edge '{edge.get('id', 'unnamed')}' targets {node_type} node '{target}'. "
                f"Edges can only target parameter nodes. "
                f"Consider creating a base parameter and targeting that instead."
            )
            continue

        if target not in parameter_ids:
            errors.append(f"Edge targets '{target}' which is not a parameter node")

    # Validate distributions have proper parameters wrapper
    for node in scenario.get("nodes", []):
        if node.get("type") == "parameter":
            dist = node.get("distribution", {})
            if "parameters" not in dist:
                errors.append(f"Parameter '{node['id']}' distribution missing 'parameters' field")

    # Validate edge distributions
    for edge in scenario.get("edges", []):
        dist = edge.get("distribution", {})
        if "parameters" not in dist:
            errors.append(f"Edge '{edge.get('id', 'unnamed')}' distribution missing 'parameters' field")

    return len(errors) == 0, errors

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
        return simulate_graph(payload)  # Use function default iterations
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
    print(f"🟢 CHAT ENDPOINT: Received payload: {payload}")
    print(f"🟢 CHAT ENDPOINT: History length: {len(payload.history)}")
    for i, msg in enumerate(payload.history):
        print(f"🟢 CHAT ENDPOINT: Message {i}: {msg.role} = '{msg.content[:100]}...'")

    if "ANTHROPIC_API_KEY" not in os.environ:
        # stub response so you can develop without a key
        last_user = next((m.content for m in reversed(payload.history)
                          if m.role == "user"), "")
        print(f"🟡 CHAT ENDPOINT: Using stub mode")
        return {"type": "text",
                "content": f"(stub) You said: {last_user}. "
                           "Add ANTHROPIC_API_KEY to .env for live Claude."}

    try:
        print(f"🟢 CHAT ENDPOINT: Calling Claude...")
        claude_json = await call_claude([m.model_dump() for m in payload.history])
        print(f"🟡 CHAT ENDPOINT: Claude raw response: {claude_json}")

        # Extract tool_use content correctly from Claude's response
        content_items = claude_json.get("content", [])
        print(f"🟡 CHAT ENDPOINT: Content items: {content_items}")

        # Look for tool_use in all content items
        tool_content = None
        text_content = None

        for item in content_items:
            if item.get("type") == "tool_use":
                tool_content = item
                print(f"🟢 CHAT ENDPOINT: Found tool_use: {tool_content}")
            elif item.get("type") == "text":
                text_content = item
                print(f"🟡 CHAT ENDPOINT: Found text: {text_content}")

        # Handle tool use with enhanced validation
        if tool_content:
            print(f"🟢 CHAT ENDPOINT: Tool use detected!")
            print(f"🟢 CHAT ENDPOINT: Tool name: {tool_content.get('name')}")
            print(f"🟢 CHAT ENDPOINT: Tool input: {tool_content.get('input')}")

            scenario = tool_content["input"]

            # Enhanced validation with specific error messages
            try:
                valid, errors = validate_scenario_enhanced(scenario)
                if not valid:
                    # Return detailed error message for Claude to fix
                    error_msg = "I found issues with the model:\n" + "\n".join(f"- {err}" for err in errors[:3])
                    error_msg += "\n\nLet me revise this with the correct structure."
                    print(f"🔴 CHAT ENDPOINT: Validation failed: {error_msg}")
                    response = {"type": "text", "content": error_msg}
                    print(f"🟡 CHAT ENDPOINT: Returning validation error for Claude to fix")
                    return response
            except Exception as exc:
                error_msg = f"Model validation failed: {str(exc)}. Let me try a different approach."
                print(f"🔴 CHAT ENDPOINT: Validation exception: {exc}")
                return {"type": "text", "content": error_msg}

            # If validation passes, return schema for frontend
            response = {"type": "json", "content": scenario}
            print(f"🟢 CHAT ENDPOINT: Validation passed, returning schema for frontend simulation")
            return response

        # If no tool use, return text response
        if text_content:
            text_response = text_content.get("text", "")
            print(f"🟢 CHAT ENDPOINT: Text response: '{text_response}'")
            response = {"type": "text", "content": text_response}
            print(f"🟢 CHAT ENDPOINT: Returning text response: {response}")
            return response

        # Fallback if neither found
        print(f"🔴 CHAT ENDPOINT: No tool_use or text content found")
        return {"type": "text", "content": "I apologize, but I couldn't process that request properly."}

    except Exception as exc:
        print(f"🔴 CHAT ENDPOINT: Exception: {exc}")
        print(f"🔴 CHAT ENDPOINT: Exception type: {type(exc)}")
        import traceback
        print(f"🔴 CHAT ENDPOINT: Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=str(exc))

# ───────────────────  STATIC FILES (MOVED TO END)  ─────────────
# Serve static frontend  (index.html, styles.css)  →  http://localhost:8000/
static_dir = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
