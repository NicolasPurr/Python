from lxml import etree

from drugbank.simulator import (
    aggregate_drug_data,
    generate_element,
    set_primary_drugbank_id,
    main,
    NS_URL
)


def test_aggregate_drug_data():
    xml = """
    <drug xmlns="http://www.drugbank.ca">
        <name>Aspirin</name>
        <synonyms>
            <synonym>Acetylsalicylic Acid</synonym>
            <synonym>ASA</synonym>
        </synonyms>
    </drug>
    """
    drug = etree.fromstring(xml)
    leaf_values = {}
    repeat_counts = {}

    aggregate_drug_data(drug, leaf_values, repeat_counts)

    assert leaf_values['name'] == ['Aspirin']
    assert 'synonyms/synonym' in leaf_values
    assert sorted(leaf_values['synonyms/synonym']) == ['ASA', 'Acetylsalicylic Acid']
    assert repeat_counts['synonyms/synonym'] == [2]


def test_generate_element():
    xml = """
    <drug xmlns="http://www.drugbank.ca">
        <name>Paracetamol</name>
        <synonyms>
            <synonym>Acetaminophen</synonym>
        </synonyms>
    </drug>
    """
    template = etree.fromstring(xml)
    leaf_values = {
        'name': ['Ibuprofen', 'Naproxen'],
        'synonyms/synonym': ['Advil', 'Aleve']
    }
    repeat_counts = {
        'synonyms/synonym': [1, 2]
    }

    new_elem = generate_element(template, '', leaf_values, repeat_counts)

    assert new_elem.tag.endswith('drug')
    assert new_elem.find(f'{{{NS_URL}}}name').text in leaf_values['name']
    synonyms = new_elem.find(f'{{{NS_URL}}}synonyms')
    assert len(synonyms.findall(f'{{{NS_URL}}}synonym')) in {1, 2}


def test_set_primary_drugbank_id():
    xml = """
    <drug xmlns="http://www.drugbank.ca">
        <drugbank-id>DB0001</drugbank-id>
        <drugbank-id>DB0002</drugbank-id>
    </drug>
    """
    drug = etree.fromstring(xml)
    set_primary_drugbank_id(drug, primary_value="DB1234")

    ids = drug.findall(f".//{{{NS_URL}}}drugbank-id")
    assert ids[0].text == "DB1234"
    assert ids[0].attrib.get('primary') == 'true'
    assert 'primary' not in ids[1].attrib
