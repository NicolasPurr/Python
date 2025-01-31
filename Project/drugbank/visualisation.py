# drugbank/visualisation.py
import networkx as nx
from adjustText import adjust_text
import matplotlib.pyplot as plt


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

    plt.show()


def draw_bipartite_graph(df):
    """Draws a bipartite graph from a data frame with improved layout, labels, and edges."""
    B = nx.Graph()

    B.add_nodes_from(df["Drug"].unique(), bipartite=0)  # Drugs as part of bipartite set 0
    B.add_nodes_from(df["Pathway"].unique(), bipartite=1)  # Pathways as part of bipartite set 1
    B.add_edges_from([(row["Drug"], row["Pathway"]) for _, row in df.iterrows()])

    # Create the bipartite layout for visualization
    plt.figure(figsize=(12, 8))
    pos = nx.bipartite_layout(B, df["Drug"].unique())  # Positions of drugs and pathways

    nx.draw_networkx_edges(B, pos, alpha=0.5, edge_color='gray', width=1.5, style='solid')

    # Get labels, sizes, and colors for nodes
    node_labels = {node: node for node in B.nodes()}
    node_sizes = [800 if node in df["Drug"].unique() else 500 for node in B.nodes()]
    node_colors = ['gold' if node in df["Drug"].unique() else 'lightblue' for node in B.nodes()]

    nx.draw_networkx_nodes(B, pos, node_size=node_sizes, node_color=node_colors, edgecolors='black')

    label_texts = [
        plt.text(pos[node][0], pos[node][1], node_labels[node], fontsize=8, fontweight="bold", ha='center', va='center',
                 bbox=dict(facecolor="white", edgecolor='black', boxstyle="round,pad=0.3")) for node in B.nodes()]
    adjust_text(label_texts, only_move={'points': 'y', 'text': 'xy'}, arrowprops=dict(arrowstyle="->", color='red'))

    plt.title("Drug-Pathway Interaction Graph", fontsize=12, fontweight="bold")
    plt.margins(0.1)
    plt.axis("off")
    plt.show()


def plot_histogram(drug_pathway_counts):
    """Plots histogram of drugs and their interactions."""
    plt.figure(figsize=(10, 6))
    plt.hist(drug_pathway_counts.values(), bins=20, align='mid', edgecolor='black')
    plt.xlabel("Liczba Szlaków")
    plt.ylabel("Liczba Leków")
    plt.title("Dystrybucja Interakcji pomiędzy Szlakami a Lekami")
    plt.show()


def plot_circular(cellular_locations):
    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(
        cellular_locations.values(),
        labels=cellular_locations.keys(),
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.cm.Paired.colors,
        pctdistance=0.85
    )

    # Improve label placement
    for text, autotext in zip(texts, autotexts):
        text.set_fontsize(10)
        autotext.set_fontsize(8)
        text.set_bbox(dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.3'))
        autotext.set_bbox(dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.3'))

    plt.title("Percentage Distribution of Target Proteins in Cellular Locations")
    plt.tight_layout()
    plt.show()


def plot_status(status_counts):
    plt.figure(figsize=(10, 6))
    plt.pie(
        status_counts.values(),
        labels=status_counts.keys(),
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.cm.Paired.colors
    )
    plt.title("Distribution of Drug Approval Statuses")
    plt.show()

