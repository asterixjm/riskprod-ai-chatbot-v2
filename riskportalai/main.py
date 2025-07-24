from fastapi import FastAPI, HTTPException
from .graph_simulate import simulate_graph

# Initialize the FastAPI app
app = FastAPI(title="RiskPortal-AI", version="0.0.1")

@app.get("/health")
async def health():
    """A simple health check endpoint."""
    return {"status": "ok", "version": app.version}

@app.post("/graph_simulate")
async def graph_simulate_endpoint(payload: dict):
    """The main simulation endpoint."""
    try:
        out = simulate_graph(payload, iterations=10_000)
        return out
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))