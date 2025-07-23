from fastapi.testclient import TestClient
from riskportalai.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_graph_stub():
    payload = {"schemaVersion": "1.0", "nodes": [], "edges": []}
    r = client.post("/graph_simulate", json=payload)
    assert r.status_code == 200
    assert r.json()["note"].startswith("simulation engine")
