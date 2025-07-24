from riskportalai.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_chat_stub():
    payload = {"history": [{"role": "user", "content": "Hello"}]}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    assert "(stub)" in r.json()["content"]
