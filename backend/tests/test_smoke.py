from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_admet():
    response = client.post("/predict/admet", json={"smiles": "CCO"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "logp" in data


def test_rag():
    response = client.post("/rag/query", json={"query": "protein language models", "top_k": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2
