import xml.etree.ElementTree as ET
import pandas as pd

########
# Task 1
########
def t1_parse_drugbank_to_dataframe(xml_content):
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()

    ns = {"db": "http://www.drugbank.ca"}
    data = []

    for drug in root.findall(".//db:drug", ns):

        if 'http://www.drugbank.ca' not in drug.tag:
            continue

        try:
            drug_id = drug.find("db:drugbank-id[@primary='true']", ns).text if drug.find("db:drugbank-id[@primary='true']", ns) is not None else None
            name = drug.find("db:name", ns).text if drug.find("db:name", ns) is not None else None
            drug_type = drug.get("type")  # Type is an attribute of <drug>
            description = drug.find("db:description", ns).text if drug.find("db:description", ns) is not None else None
            dosage_form = drug.find("db:dosages/db:dosage/db:form", ns).text if drug.find("db:dosages/db:dosage/db:form", ns) is not None else None
            indications = drug.find("db:indication", ns).text if drug.find("db:indication", ns) is not None else None
            mechanism_of_action = drug.find("db:mechanism-of-action", ns).text if drug.find("db:mechanism-of-action", ns) is not None else None
            food_interactions = [
                fi.text for fi in drug.findall(".//db:food-interactions/db:food-interaction", ns)
            ]
            food_interactions = "; ".join(food_interactions) if food_interactions else None

            data.append({
                "DrugBank ID": drug_id,
                "Name": name,
                "Type": drug_type,
                "Description": description,
                "Dosage Form": dosage_form,
                "Indications": indications,
                "Mechanism of Action": mechanism_of_action,
                "Food Interactions": food_interactions
            })
        except Exception as e:
            print(f"Error processing drug: {e}")
            continue

    if not data:
        print("No valid drug data found in the XML.")
    return pd.DataFrame(data)

########
# Task 2
########
import networkx as nx
import matplotlib.pyplot as plt


def plot_synonym_graph(df_synonyms, drugbank_id):
    synonyms = df_synonyms[df_synonyms["DrugBank ID"] == drugbank_id]["Synonym"].tolist()

    if not synonyms:
        print(f"No synonyms found for DrugBank ID: {drugbank_id}")
        return

    graph = nx.Graph()
    graph.add_node(drugbank_id, label="DrugBank ID")

    for synonym in synonyms:
        graph.add_node(synonym, label="Synonym")
        graph.add_edge(drugbank_id, synonym)

    pos = nx.spring_layout(graph)
    labels = nx.get_node_attributes(graph, 'label')

    plt.figure(figsize=(10, 6))
    nx.draw(
        graph, pos, with_labels=True, labels=labels,
        node_size=3000, node_color="lightgreen", font_size=10, font_color="black"
    )
    plt.title(f"Synonyms for DrugBank ID: {drugbank_id}")
    plt.show()

# Prezentacja
with open("drugbank_partial.xml", "r", encoding="utf-8") as file:
    xml_content = file.read()

# Task 1: Podstawowe parsowanie bazy danych
df = t1_parse_drugbank_to_dataframe(xml_content)

print(df)