# test/test_api.py
from fastapi.testclient import TestClient
from drugbank.api import app

client = TestClient(app)

def test_get_pathway_count_success():
    payload = {"drug_id": "DB00001"}
    response = client.post("/get_pathway_count/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["drug_id"] == payload["drug_id"]
    assert "pathway_count" in data

def test_get_pathway_count_not_found():
    payload = {"drug_id": "non_existing_drug"}
    response = client.post("/get_pathway_count/", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Drug not found"