from fastapi.testclient import TestClient
from riskportalai.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_graph_endpoint_runs():
    # A minimal valid payload to ensure the endpoint runs
    payload = {
        "schemaVersion": "1.0",
        "nodes": [
            {"id": "revenue", "type": "parameter", "distribution": {"type": "constant", "parameters": {"value": 100}}},
            {"id": "final_revenue", "type": "result", "formula": "revenue", "is_result": True}
        ],
        "edges": []
    }
    r = client.post("/graph_simulate", json=payload)

    # Check that the request was successful and the response has the correct structure
    assert r.status_code == 200
    assert "results" in r.json()
    assert "metadata" in r.json()