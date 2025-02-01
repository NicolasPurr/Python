import pytest
import pandas as pd
from unittest.mock import patch
from drugbank.visualisers import *

@pytest.fixture
def mock_df():
    """Mock dataframe with drug-related data."""
    return pd.DataFrame({
        'DrugBank_ID': ['DB001', 'DB002', 'DB001'],
        'Synonyms': [['Aspirin', 'Acetylsalicylic acid'], ['Ibuprofen'], ['Aspirin', 'Acetylsalicylic acid']]
    })

@pytest.fixture
def mock_graph():
    return pd.DataFrame({
        "DrugBank_ID": ["DB001", "DB001", "DB002", "DB002", "DB003", "DB004"],
        "Drug": ["Aspirin", "Aspirin", "Ibuprofen", "Ibuprofen", "Metformin", "Losartan"],
        "Pathway": ["Pain Relief", "Anti-inflammatory", "Pain Relief", "Anti-inflammatory", "Diabetes", "Hypertension"],
        "Type": ["Small Molecule", "Small Molecule", "Small Molecule", "Small Molecule", "Small Molecule",
                 "Small Molecule"]
    })

def mock_genes():
    return pd.DataFrame({
        "Gene" : ["F2", "F2", "F2", "F2"],
        "Drug" : ["Lepirudin", "Lepirudin", "Lepirudin", "Lepirudin"],
        "Interacting_Drug" : ["Urokinase", "Urokinase", "Tositumomab", "Cyclosporine"],
        "Product_Name" : ["Kinlytic", "Kinlytic (for injection)", "Bexxar", "Bexxar Dosimetric"],
        "Product_ID" : ["24430-1003", "00743242", "008483243", "110342423"],
        "Product_ID_Type" : ["ndc-product", "dpd-id", "dpd-id", "dpd-id"]
    })

# Test for draw_synonym_graph
@patch("drugbank.visualisers.plt.show")
def test_draw_synonym_graph(mock_show, mock_df):
    """Test that draw_synonym_graph does not raise an exception."""
    visualise_synonyms('DB001', mock_df)
    mock_show.assert_called_once()  # Ensure plt.show() was called

# Test for draw_bipartite_graph
@patch("drugbank.visualisers.plt.show")
def test_draw_bipartite_graph(mock_show, mock_graph):
    """Test that draw_bipartite_graph does not raise an exception."""
    visualise_drug_pathways(mock_graph)
    mock_show.assert_called_once()  # Ensure plt.show() was called

# Test for plot_histogram
@patch("drugbank.visualisers.plt.show")
def test_plot_histogram(mock_show):
    """Test that plot_histogram does not raise an exception."""
    mock_counts = {'drug1': 5, 'drug2': 10, 'drug3': 7}
    drug_pathways_histogram(mock_counts)
    mock_show.assert_called_once()  # Ensure plt.show() was called

# Test for plot_circular
@patch("drugbank.visualisers.plt.show")
def test_plot_circular(mock_show):
    """Test that plot_circular does not raise an exception."""
    mock_data = {'Location1': 50, 'Location2': 30, 'Location3': 20}
    visualise_cellular_locations(mock_data)
    mock_show.assert_called_once()  # Ensure plt.show() was called

# Test for plot_status
@patch("drugbank.visualisers.plt.show")
def test_plot_status(mock_show):
    """Test that plot_status does not raise an exception."""
    mock_status = {'Approved': 15, 'Clinical Trials': 8, 'Withdrawn': 3}
    visualise_statuses(mock_status)
    mock_show.assert_called_once()  # Ensure plt.show() was called

# Test for plot_status
@patch("drugbank.visualisers.plt.show")
def test_gene_graph(mock_show):
    """Test that plot_status does not raise an exception."""
    visualise_genes(mock_genes(), "F2")
    mock_show.assert_called_once()  # Ensure plt.show() was called
