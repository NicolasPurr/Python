# tests/test_parsers.py
import pytest
from drugbank.parsers import *

@pytest.fixture
def empty_xml():
    return """<drugbank xmlns="http://www.drugbank.ca">
              </drugbank>"""

@pytest.fixture
def single_drug_xml():
    return """<drugbank xmlns="http://www.drugbank.ca">
                <drug>
                    <drugbank-id primary="true">DB00001</drugbank-id>
                    <name>Aspirin</name>
                    <synonyms>
                        <synonym>Acetylsalicylic Acid</synonym>
                        <synonym>ASA</synonym>
                    </synonyms>
                    <products>
                        <product>
                            <name>Aspirin 100mg</name>
                            <manufacturer>Bayer</manufacturer>
                        </product>
                    </products>
                    <pathways>
                        <pathway>
                            <name>Arachidonic Acid Pathway</name>
                            <category>Metabolic</category>
                        </pathway>
                    </pathways>
                    <targets>
                        <target>
                            <id>TRG0001</id>
                            <polypeptide source="SwissProt" id="P12345">
                                <name>Cyclooxygenase-1</name>
                                <gene-name>PTGS1</gene-name>
                            </polypeptide>
                        </target>
                    </targets>
                    <drug-interactions>
                        <drug-interaction>
                            <drugbank-id>DB00002</drugbank-id>
                            <name>Warfarin</name>
                            <description>Increases risk of bleeding.</description>
                        </drug-interaction>
                    </drug-interactions>
                    <groups>
                        <group>approved</group>
                    </groups>
                </drug>
              </drugbank>"""

@pytest.fixture
def multiple_drugs_xml():
    return """<drugbank xmlns="http://www.drugbank.ca">
                <drug>
                    <drugbank-id primary="true">DB00001</drugbank-id>
                    <name>Aspirin</name>
                    <description>Pain reliever</description>
                </drug>
                <drug>
                    <drugbank-id primary="true">DB00002</drugbank-id>
                    <name>Ibuprofen</name>
                    <description>Anti-inflammatory</description>
                </drug>
              </drugbank>"""

@pytest.fixture
def missing_elements_xml():
    return """<drugbank xmlns="http://www.drugbank.ca">
                <drug>
                    <drugbank-id primary="true">DB00003</drugbank-id>
                </drug>
              </drugbank>"""

@pytest.fixture
def invalid_xml():
    return """<drugbank xmlns="http://www.drugbank.ca">
                <drug>
                    <drugbank-id primary="true">DB00004</drugbank-id>
                    <name>Paracetamol</name>
              """  # Missing closing tags

def test_parse_multiple_drugs(multiple_drugs_xml):
    df = parse_drugs(multiple_drugs_xml)
    assert len(df) == 2
    assert df.iloc[0]["DrugBank_ID"] == "DB00001"
    assert df.iloc[1]["DrugBank_ID"] == "DB00002"

def test_parse_missing_elements(missing_elements_xml):
    df = parse_drugs(missing_elements_xml)
    assert len(df) == 1
    assert df.iloc[0]["Name"] is None  # Name is missing

def test_parse_invalid_xml(capfd, invalid_xml):
    df = parse_drugs(invalid_xml)
    captured = capfd.readouterr()
    assert "Error parsing XML" in captured.out
    assert df.empty  # Should return an empty DataFrame

def test_parse_drugs(empty_xml, single_drug_xml):
    df_empty = parse_drugs(empty_xml)
    assert df_empty.empty

    df = parse_drugs(single_drug_xml)
    assert len(df) == 1
    assert df.iloc[0]["DrugBank_ID"] == "DB00001"
    assert df.iloc[0]["Name"] == "Aspirin"

def test_parse_synonyms(empty_xml, single_drug_xml):
    df_empty = parse_synonyms(empty_xml)
    assert df_empty.empty

    df = parse_synonyms(single_drug_xml)
    assert len(df) == 1
    assert df.iloc[0]["DrugBank_ID"] == "DB00001"
    assert "Acetylsalicylic Acid" in df.iloc[0]["Synonyms"]
    assert "ASA" in df.iloc[0]["Synonyms"]

def test_parse_products(empty_xml, single_drug_xml):
    df_empty = parse_products(empty_xml)
    assert df_empty.empty

    df = parse_products(single_drug_xml)
    assert len(df) == 1
    assert df.iloc[0]["Products"][0]["Product Name"] == "Aspirin 100mg"
    assert df.iloc[0]["Products"][0]["Manufacturer"] == "Bayer"

def test_parse_pathways(empty_xml, single_drug_xml):
    df_empty, _ = parse_pathways(empty_xml)
    assert df_empty.empty

    df, counts = parse_pathways(single_drug_xml)
    assert len(df) == 1
    assert df.iloc[0]["DrugBank_ID"] == "DB00001"
    assert df.iloc[0]["Pathway"] == "Arachidonic Acid Pathway"
    assert counts["DB00001"] == 1

def test_parse_targets(empty_xml, single_drug_xml):
    df_empty, _ = parse_targets(empty_xml)
    assert df_empty.empty

    df, _ = parse_targets(single_drug_xml)
    assert len(df) == 1
    assert df.iloc[0]["Target_ID"] == "TRG0001"
    assert df.iloc[0]["Gene_Name"] == "PTGS1"
    assert df.iloc[0]["Polypeptide_Name"] == "Cyclooxygenase-1"

def test_parse_drug_interactions(empty_xml, single_drug_xml):
    df_empty = parse_drug_interactions(empty_xml)
    assert df_empty.empty

    df = parse_drug_interactions(single_drug_xml)
    assert len(df) == 1
    assert df.iloc[0]["Interacting_Drug_ID"] == "DB00002"
    assert df.iloc[0]["Interacting_Drug"] == "Warfarin"
    assert "Increases risk of bleeding." in df.iloc[0]["Description"]

def test_parse_approval_status(empty_xml, single_drug_xml):
    df_empty, _, _ = parse_approval_status(empty_xml)
    assert df_empty.empty

    df, approved_not_withdrawn, status_counts = parse_approval_status(single_drug_xml)
    assert len(df) == 1
    assert status_counts["Approved"] == 1
    assert approved_not_withdrawn == 1
