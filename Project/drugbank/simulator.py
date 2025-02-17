import random
from datetime import date
from lxml import etree

# The default namespace URL.
NS_URL = "http://www.drugbank.ca"


def aggregate_drug_data(drug, leaf_values, repeat_counts):
    """
    Recursively traverse one <drug> element and update:
      - leaf_values: mapping from a relative path (e.g. "synonyms/synonym") to a list of text values.
      - repeat_counts: mapping from a relative path (for repeating children) to a list of counts observed.
    """

    def recurse(elem, path):
        # Get only element children.
        children = [child for child in elem if isinstance(child.tag, str)]
        if not children:
            text = elem.text.strip() if elem.text and elem.text.strip() else ""
            leaf_values.setdefault(path, []).append(text)
        else:
            # Group children by their local name (ignoring the namespace).
            groups = {}
            for child in children:
                tag = etree.QName(child).localname
                groups.setdefault(tag, []).append(child)
            for tag, child_list in groups.items():
                child_path = f"{path}/{tag}" if path else tag
                if len(child_list) > 1:
                    repeat_counts.setdefault(child_path, []).append(len(child_list))
                for child in child_list:
                    recurse(child, child_path)

    recurse(drug, "")


def generate_element(template_elem, path, leaf_values, repeat_counts):
    """
    Recursively generate a new element based on the template element.
    For leaf nodes, set the text to a random value chosen from the aggregated leaf_values.
    For container elements, if its children are meant to be repeating (i.e. the path exists in repeat_counts),
    then choose a random count and generate that many children.
    """
    # Create new element with the same tag (ensuring it is in the default namespace).
    local_name = etree.QName(template_elem).localname
    new_elem = etree.Element(f"{{{NS_URL}}}{local_name}")

    # Copy attributes from the template element if desired.
    for attr, value in template_elem.attrib.items():
        new_elem.attrib[attr] = value

    children = [child for child in template_elem if isinstance(child.tag, str)]
    if not children:
        possible_values = leaf_values.get(path, [""])
        new_elem.text = random.choice(possible_values)
    else:
        groups = {}
        for child in children:
            tag = etree.QName(child).localname
            groups.setdefault(tag, []).append(child)
        for tag, templates in groups.items():
            child_path = f"{path}/{tag}" if path else tag
            count = random.choice(repeat_counts[child_path]) if child_path in repeat_counts else len(templates)
            for _ in range(count):
                new_child = generate_element(templates[0], child_path, leaf_values, repeat_counts)
                new_elem.append(new_child)
    return new_elem


def set_primary_drugbank_id(drug, primary_value=None):
    """
    Finds all <drugbank-id> elements (ignoring namespace) in the given drug element.
    Sets the first one to have primary="true".
    If primary_value is provided, that value (as text) is used for the primary id.
    Any additional <drugbank-id> elements have the primary attribute removed.
    """
    # Use XPath with local-name() so we don't worry about namespaces.
    ids = drug.xpath(".//*[local-name()='drugbank-id']")
    if ids:
        # If a primary_value is provided, override the text with that value.
        if primary_value is not None:
            ids[0].text = str(primary_value)
        ids[0].attrib["primary"] = "true"
        # Remove 'primary' attribute from any others.
        for other in ids[1:]:
            if "primary" in other.attrib:
                del other.attrib["primary"]


def main(total_drugs, total_consecutive_ids):
    input_file = "data/drugbank_partial.xml"
    output_file = "data/drugbank_partial_generated.xml"

    tree = etree.parse(input_file)
    root = tree.getroot()

    # Use the namespace mapping to find all <drug> elements.
    ns = {"db": NS_URL}
    drugs = root.findall(".//db:drug", namespaces=ns)
    if not drugs:
        print("No <drug> elements found in the input file.")
        return

    # Aggregate values and counts from each drug.
    leaf_values = {}  # Mapping: relative path -> list of text values.
    repeat_counts = {}  # Mapping: relative path -> list of counts observed.
    for drug in drugs:
        aggregate_drug_data(drug, leaf_values, repeat_counts)

    # Use the first drug as a structure template.
    template_drug = drugs[0]

    print("Generating fake drugs...")
    fake_drugs = []
    for i in range(total_drugs):
        new_drug = generate_element(template_drug, "", leaf_values, repeat_counts)
        if i < total_consecutive_ids:
            set_primary_drugbank_id(new_drug, primary_value=i + 1)
        else:
            set_primary_drugbank_id(new_drug)  # Use the generated/random primary id.
        fake_drugs.append(new_drug)
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/20000")

    # Create a root element for the output.
    nsmap = {None: NS_URL, "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    new_root = etree.Element(f"{{{NS_URL}}}drugbank", nsmap=nsmap)
    new_root.attrib["version"] = "5.1"
    new_root.attrib["exported-on"] = date.today().isoformat()  # e.g., "2024-03-14"
    new_root.attrib[
        "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
    ] = f"{NS_URL} {NS_URL}/docs/drugbank.xsd"

    i = 0
    print("Appending...")
    for drug in fake_drugs:
        new_root.append(drug)
        i = i + 1
        if i % 100 == 0:
            print(f"Appended {i}/20000")

    print("Writing...")
    new_tree = etree.ElementTree(new_root)
    new_tree.write(output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Generated {len(fake_drugs)} fake drugs in '{output_file}'.")
    return
