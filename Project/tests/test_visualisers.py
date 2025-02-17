import pytest
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from unittest.mock import patch
from drugbank.visualisers import (
    visualise_synonyms,
    visualise_drug_pathways,
    drug_pathways_histogram,
    visualise_cellular_locations,
    visualise_statuses,
    visualise_genes,
    visualise_drug_target_amino
)


# Fixtures for common mock data
@pytest.fixture
def mock_df():
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
        "Type": ["Small Molecule"] * 6
    })


@pytest.fixture
def mock_genes():
    return pd.DataFrame({
        "Gene": ["F2", "F2", "F2", "F2"],
        "Drug": ["Lepirudin"] * 4,
        "Interacting_Drug": ["Urokinase", "Urokinase", "Tositumomab", "Cyclosporine"],
        "Product_Name": ["Kinlytic", "Kinlytic (for injection)", "Bexxar", "Bexxar Dosimetric"],
        "Product_ID": ["24430-1003", "00743242", "008483243", "110342423"],
        "Product_ID_Type": ["ndc-product", "dpd-id", "dpd-id", "dpd-id"]
    })


# A simple empty dataframe for edge case tests.
@pytest.fixture
def empty_df():
    return pd.DataFrame()


# -------------------------------
# Improved Tests for Each Function
# -------------------------------

@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_synonyms(mock_savefig, mock_show, mock_df, capsys):
    drug_id = 'DB001'
    expected_filename = f"data/{drug_id}_synonym_graph.png"
    visualise_synonyms(drug_id, mock_df)

    # Check that plt.savefig was called with the expected filename
    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()

    # Check that the print message contains the filename.
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_drug_pathways(mock_savefig, mock_show, mock_graph, capsys):
    expected_filename = "data/pathway_graph.png"
    visualise_drug_pathways(mock_graph)

    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_drug_pathways_histogram(mock_savefig, mock_show, capsys):
    mock_counts = {'drug1': 5, 'drug2': 10, 'drug3': 7}
    expected_filename = "data/drug_pathway_histogram.png"
    drug_pathways_histogram(mock_counts)

    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_cellular_locations(mock_savefig, mock_show, capsys):
    mock_data = {'Location1': 50, 'Location2': 30, 'Location3': 20}
    expected_filename = "data/cellular_locations.png"
    visualise_cellular_locations(mock_data)

    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_statuses(mock_savefig, mock_show, capsys):
    mock_status = {'Approved': 15, 'Clinical Trials': 8, 'Withdrawn': 3}
    expected_filename = "data/approval_statuses.png"
    visualise_statuses(mock_status)

    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_genes_valid(mock_savefig, mock_show, mock_genes, capsys):
    gene = "F2"
    expected_filename = "data/gene_tree.png"
    visualise_genes(mock_genes, gene)

    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_genes_not_found(mock_savefig, mock_show, mock_genes, capsys):
    gene = "NonExistentGene"
    visualise_genes(mock_genes, gene)

    mock_savefig.assert_not_called()
    mock_show.assert_not_called()
    captured = capsys.readouterr().out
    assert f"No data found for gene {gene}" in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_drug_target_amino_valid(mock_savefig, mock_show, capsys):
    plt.close('all')
    matplotlib.use("Agg")
    df = pd.DataFrame({
        "DrugBank_ID": ["DB001", "DB001"],
        "Target_Name": ["Target1", "Target2"],
        "Amino_Acid_Count": [200, 150]
    })
    expected_filename = "data/drug_target_tree.png"
    visualise_drug_target_amino(df, "DB001")

    mock_savefig.assert_called_with(expected_filename, dpi=300)
    mock_show.assert_called_once()
    captured = capsys.readouterr().out
    assert expected_filename in captured


@patch("drugbank.visualisers.plt.show")
@patch("drugbank.visualisers.plt.savefig")
def test_visualise_drug_target_amino_empty(mock_savefig, mock_show, capsys, empty_df):
    drug_id = "DB999"
    visualise_drug_target_amino(empty_df, drug_id)

    # Expect the function to print a message and return early.
    mock_savefig.assert_not_called()
    mock_show.assert_not_called()
    captured = capsys.readouterr().out
    assert f"No data found for DrugBank_ID {drug_id}" in captured
