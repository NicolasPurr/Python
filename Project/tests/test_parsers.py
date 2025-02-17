# tests/test_parsers.py
import pytest
from lxml import etree

from drugbank.parsers import (
    parse_polypeptide,
    parse_targets,
    parse_products,
    parse_pathways,
    parse_synonyms,
    parse_genatlas_id,
    parse_drugs,
    parse_approval_status,
    parse_drug_interactions,
    get_target_amino_acid_count_for_drug,
    get_amino_acid_count_from_html,
    get_amino_acid_count_for_target,
    pd
)


@pytest.fixture
def empty_xml():
    xml = """<drugbank xmlns="http://www.drugbank.ca">
              </drugbank>"""
    return etree.fromstring(xml)


@pytest.fixture
def single_drug_xml():
    xml = """<drugbank xmlns="http://www.drugbank.ca">
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
                            <drugs>
                                <drug>
                                  <drugbank-id>DB00001</drugbank-id>
                                  <name>Lepirudin</name>
                                </drug>
                            </drugs>
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
    return etree.fromstring(xml)


@pytest.fixture
def multiple_drugs_xml():
    xml = """<drugbank xmlns="http://www.drugbank.ca">
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
    return etree.fromstring(xml)


@pytest.fixture
def missing_elements_xml():
    xml = """<drugbank xmlns="http://www.drugbank.ca">
                <drug>
                    <drugbank-id primary="true">DB00003</drugbank-id>
                </drug>
              </drugbank>"""
    return etree.fromstring(xml)


def test_parse_multiple_drugs(multiple_drugs_xml):
    df = parse_drugs(multiple_drugs_xml)
    assert len(df) == 2
    assert df.iloc[0]["DrugBank_ID"] == "DB00001"
    assert df.iloc[1]["DrugBank_ID"] == "DB00002"


def test_parse_missing_elements(missing_elements_xml):
    df = parse_drugs(missing_elements_xml)
    assert len(df) == 1
    assert df.iloc[0]["Name"] is None  # Name is missing


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


def test_parse_polypeptide():
    # Construct a small XML fragment representing a polypeptide.
    xml_str = """
    <polypeptide xmlns="http://www.drugbank.ca" source="SwissProt" id="P12345">
        <name>Cyclooxygenase-1</name>
        <gene-name>PTGS1</gene-name>
        <chromosome-location>7q22</chromosome-location>
        <cellular-location>Plasma membrane</cellular-location>
    </polypeptide>
    """
    elem = etree.fromstring(xml_str)
    source, ext_id, poly_name, gene_name, chromosome, cell_loc = parse_polypeptide(elem)
    assert source == "SwissProt"
    assert ext_id == "P12345"
    assert poly_name == "Cyclooxygenase-1"
    assert gene_name == "PTGS1"
    assert chromosome == "7q22"
    assert cell_loc == "Plasma membrane"


def test_parse_genatlas_id():
    xml_str = """
    <polypeptide xmlns="http://www.drugbank.ca">
        <external-identifier>
            <resource>GenAtlas</resource>
            <identifier>GA1234</identifier>
        </external-identifier>
    </polypeptide>
    """
    elem = etree.fromstring(xml_str)
    ga_id = parse_genatlas_id(elem)
    assert ga_id == "GA1234"


def test_get_amino_acid_count_from_html():
    # Dummy HTML representing a UniProt card.
    html_good = """
    <html>
      <body>
        <section class="card">
          <h2 class="small">P02745 · C1QA_HUMAN</h2>
            <div class="card__container">
                <div class="card__header">
                    Complement C1q subcomponent subunit A · Gene: C1QA · Homo sapiens (Human) · 245 amino acids · Evidence...
                </div>
                <div class="card__content">
                    Complement C1q subcomponent subunit A · Gene: C1QA · 
                    <a title="Homo sapiens (Human), taxon ID 9606" translate="no" href="/taxonomy/9606">Homo sapiens (Human)</a>
                     · 245 amino acids · Evidence...
                </div>
            </div>
        </section>
      </body>
    </html>
    """
    aa_count = get_amino_acid_count_from_html(html_good, "Complement C1q subcomponent subunit A")
    assert aa_count == 245

    html_bad = """
        <html>
          <body>
            <section class="card">
              <h2 class="small">P02745 · C1QA_HUMAN</h2>
                <div class="card__container">
                    <div class="card__header">
                        Complement C1q subcomponent subunit A · Gene: C1QA · Homo sapiens (Human) · 245 amino acids · Evidence...
                    </div>
                    <div class="card__content">
                        Complement C1q subcomponent subunit A · Gene: C1QA · Homo sapiens (Human) · 245 amino acids · Evidence...
                    </div>
                </div>
            </section>
          </body>
        </html>
        """
    aa_count = get_amino_acid_count_from_html(html_bad, "Complement C1q subcomponent subunit A")
    assert aa_count is None


def test_get_amino_acid_count_for_target(monkeypatch):
    # Create a fake function that returns our dummy HTML
    def fake_get_uniprot_cards_page(query, sleep_time=2):
        return """
        <html>
          <body>
            <section class="card">
              <h2 class="small">P02745 · C1QA_HUMAN</h2>
                <div class="card__container">
                    <div class="card__header">
                        Complement C1q subcomponent subunit A · Gene: C1QA · Homo sapiens (Human) · 245 amino acids · Evidence...
                    </div>
                    <div class="card__content">
                        Complement C1q subcomponent subunit A · Gene: C1QA · 
                        <a title="Homo sapiens (Human), taxon ID 9606" translate="no" href="/taxonomy/9606">Homo sapiens (Human)</a>
                         · 245 amino acids · Evidence...
                    </div>
                </div>
            </section>
          </body>
        </html>
    """
    monkeypatch.setattr("drugbank.parsers.get_uniprot_cards_page", fake_get_uniprot_cards_page)
    aa_count = get_amino_acid_count_for_target("C1QA")
    assert aa_count == 245


def test_get_target_amino_acid_count_for_drug(monkeypatch):
    df_targets = pd.DataFrame({
        "DrugBank_ID": ["DB00001", "DB00001"],
        "Target_Name": ["C1QA", "EGFR"]
    })

    # Patch get_amino_acid_count_for_target to return fixed values.
    def fake_get_amino_acid_count_for_target(target_name):
        return 245 if target_name == "C1QA" else 1210
    monkeypatch.setattr("drugbank.parsers.get_amino_acid_count_for_target", fake_get_amino_acid_count_for_target)
    result_df = get_target_amino_acid_count_for_drug("DB00001", df_targets)
    assert result_df.loc[result_df["Target_Name"] == "C1QA", "Amino_Acid_Count"].iloc[0] == 245
    assert result_df.loc[result_df["Target_Name"] == "EGFR", "Amino_Acid_Count"].iloc[0] == 1210
