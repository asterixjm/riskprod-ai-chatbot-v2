from fastapi import FastAPI
from .graph_simulate import simulate_graph  # placeholder

app = FastAPI(title="RiskPortal-AI (Graph Monte-Carlo Prototype)",
              version="0.0.1")

@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version}

@app.post("/graph_simulate")
async def graph_simulate_endpoint(payload: dict):
    """
    Stub endpoint – accepts graph JSON, echoes back.
    Real simulation arrives in Day-3/4 commit.
    """
    return {"received": payload, "note": "simulation engine not implemented yet"}
