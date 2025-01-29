import pandas as pd
import networkx as nx
from adjustText import adjust_text

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


########
# Task 1
########
def parse_drugs(xml_content):
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()

    ns = {"db": "http://www.drugbank.ca"}
    data = []

    # Only process top-level <drug> elements
    for drug in root.findall("db:drug", ns):
        try:
            # Get only the primary drugbank-id
            drug_id_element = drug.find("db:drugbank-id[@primary='true']", ns)
            drug_id = drug_id_element.text if drug_id_element is not None else None

            name = drug.find("db:name", ns).text \
                if drug.find("db:name", ns) is not None else None
            drug_type = drug.get("type")
            description = drug.find("db:description", ns).text \
                if drug.find("db:description", ns) is not None else None
            dosage_form = drug.find("db:dosages/db:dosage/db:form", ns).text \
                if drug.find("db:dosages/db:dosage/db:form", ns) is not None else None
            indications = drug.find("db:indication", ns).text \
                if drug.find("db:indication", ns) is not None else None
            mechanism_of_action = drug.find("db:mechanism-of-action", ns).text \
                if drug.find("db:mechanism-of-action", ns) is not None else None

            food_interactions = [
                fi.text for fi in drug.findall(".//db:food-interactions/db:food-interaction", ns)
            ]
            food_interactions = "; ".join(food_interactions) \
                if food_interactions else None

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

    # Convert to DataFrame and remove duplicate rows
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["DrugBank ID", "Name"])  # Ensure unique entries

    return df

########
# Task 2
########
def parse_synonyms(xml_content):
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()

    ns = {"db": "http://www.drugbank.ca"}
    data = []

    # Only process top-level <drug> elements
    for drug in root.findall("db:drug", ns):
        primary_id = drug.find("db:drugbank-id[@primary='true']", ns)
        synonyms = drug.findall("db:synonyms/db:synonym", ns)

        if primary_id is not None:
            drug_id = primary_id.text
            synonym_list = [syn.text for syn in synonyms] if synonyms else []
            data.append({"DrugBank_ID": drug_id, "Synonyms": synonym_list})

    return pd.DataFrame(data)

def draw_synonym_graph(drug_id, df, max_label_width=15):
    """ Creates and draws a graph of synonyms for a given DrugBank ID """
    synonyms = df.loc[df["DrugBank_ID"] == drug_id, "Synonyms"].values

    graph = nx.Graph()
    graph.add_node(drug_id, color='#FFD700', size=800)  # Root node

    for synonym in synonyms[0]:
        graph.add_node(synonym, color='#ADD8E6', size=500)
        graph.add_edge(drug_id, synonym)

    pos = nx.spring_layout(graph, seed=42, k=0.1)
    colors = [graph.nodes[n]["color"] for n in graph.nodes]
    sizes = [graph.nodes[n]["size"] for n in graph.nodes]

    # Calculate the bounds based on node positions (as before)
    x_values = [pos[node][0] for node in pos]
    y_values = [pos[node][1] for node in pos]
    x_range = max(x_values) - min(x_values)
    y_range = max(y_values) - min(y_values)

    plt.figure(figsize=(max(8, x_range + 2), max(6, y_range + 2)))

    nx.draw(graph, pos, with_labels=False, node_color=colors, node_size=sizes, edge_color="gray", font_size=10)

    # Get label positions
    synonyms = {node: node for node in graph.nodes if node != drug_id}

    label_texts = []
    max_label_width_actual = 0
    max_label_height = 0

    # Draw labels and calculate their bounding box size
    for label, position in pos.items():
        colour = 'black'
        if label not in synonyms:
            colour = 'gold'

        text = plt.text(position[0], position[1], label, fontsize=7, fontweight="bold",
                            ha='center', va='center', color=colour,
                            bbox=dict(facecolor="white", edgecolor=colour, boxstyle="round,pad=0.3"))
        label_texts.append(text)

        # Calculate the bounding box of the label
        bbox = text.get_window_extent()
        max_label_width_actual = max(max_label_width_actual, bbox.width)
        max_label_height = max(max_label_height, bbox.height)

    # Dynamically adjust the figure size based on the label sizes
    padding_factor = 3
    figsize_x = max(8, x_range + max_label_width_actual / 100 + padding_factor)
    figsize_y = max(6, y_range + max_label_height / 100 + padding_factor)
    plt.gcf().set_size_inches(figsize_x, figsize_y)

    adjust_text(label_texts, only_move={'points': 'y', 'text': 'xy'}, arrowprops=dict(arrowstyle="->", color='red'))

    plt.margins(0.1)
    plt.axis("off")
    plt.title(f"Synonym graph for {drug_id}", fontsize=12, fontweight="bold")

    plt.tight_layout()

    plt.show()


######
# Main
######
def main():
    with open("drugbank_partial.xml", "r", encoding="utf-8") as file:
        xml_content = file.read()

    df = parse_drugs(xml_content)
    print(df)

    df = parse_synonyms(xml_content)

    for drugbank_id in ["DB00016", "DB00025", "DB00030", "DB00058", "DB00098", "DB00108"]:
        print(f"Drawing graph for {drugbank_id}...")
        draw_synonym_graph(drugbank_id, df)

if __name__ == "__main__":
    main()