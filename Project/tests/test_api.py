import pytest
from fastapi.testclient import TestClient
from drugbank.api import app
from drugbank.parsers import parse_pathways
import pandas as pd

@pytest.fixture
def mock_parse_pathways(monkeypatch):
    mock_data = {
        "DrugBank_ID": ["DB001", "DB002", "DB003"],
        "Drug": ["Aspirin", "Ibuprofen", "Metformin"],
        "Pathway": ["Pain Relief", "Anti-inflammatory", "Diabetes"],
        "Type": ["Small Molecule", "Small Molecule", "Small Molecule"]
    }
    mock_drug_pathway_counts = {
        "DB001": 2,
        "DB002": 2,
        "DB003": 1
    }

    def mock_function(xml_content):
        return pd.DataFrame(mock_data), mock_drug_pathway_counts

    monkeypatch.setattr("drugbank.parsers.parse_pathways", mock_function)

    yield

@pytest.fixture
def client(mock_parse_pathways):
    return TestClient(app)


# Test case for /get_pathway_count endpoint
def test_get_pathway_count(client, mock_parse_pathways):
    # Valid request for DB001
    response = client.post("/get_pathway_count/", json={"drug_id": "DB001"})
    assert response.status_code == 200
    assert response.json() == {"drug_id": "DB001", "pathway_count": 2}

    # Valid request for DB002
    response = client.post("/get_pathway_count/", json={"drug_id": "DB002"})
    assert response.status_code == 200
    assert response.json() == {"drug_id": "DB002", "pathway_count": 2}

    # Invalid request for DB999
    response = client.post("/get_pathway_count/", json={"drug_id": "DB999"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Drug not found"}
