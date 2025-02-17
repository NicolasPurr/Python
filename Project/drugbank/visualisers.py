# drugbank/visualisers.py
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import igraph as ig
from adjustText import adjust_text
import matplotlib.cm as cm


def visualise_synonyms(drug_id, df):
    """ Creates and draws a graph of synonyms for a given DrugBank ID """
    synonyms = df.loc[df["DrugBank_ID"] == drug_id, "Synonyms"].values
    filename = f"data/{drug_id}_synonym_graph.png"

    graph = nx.Graph()
    graph.add_node(drug_id, color='#FFD700', size=800)  # Root node

    for synonym in synonyms[0]:
        graph.add_node(synonym, color='#ADD8E6', size=500)
        graph.add_edge(drug_id, synonym)

    pos = nx.spring_layout(graph, seed=42, k=0.1)
    colors = [graph.nodes[n]["color"] for n in graph.nodes]
    sizes = [graph.nodes[n]["size"] for n in graph.nodes]

    # Calculate the bounds based on node positions
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

    # Draw labels and calculate their bounding box sizes
    for label, position in pos.items():
        colour = 'black'
        if label not in synonyms:
            colour = 'gold'

        text = plt.text(position[0], position[1], label, fontsize=7, fontweight="bold",
                            ha='center', va='center', color='black',
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
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Pathway graph saved as {filename}. Please open the file manually if the image does not display correctly.")


def visualise_drug_pathways(df, filename="data/pathway_graph.png"):
    """Draws a bipartite graph, where:
       - each drug (DrugBank_ID) node is assigned a unique color,
       - all edges from a drug node are colored with that same unique color,
       - all pathway nodes are a single solid color.
    """
    graph = nx.Graph()

    # Extract unique drugs and pathways
    drugs = df["DrugBank_ID"].unique()
    pathways = df["Pathway"].unique()
    drug_set = set(drugs)

    graph.add_nodes_from(drugs, bipartite=0)  # Drug nodes
    graph.add_nodes_from(pathways, bipartite=1)  # Pathway nodes

    pathway_color = "lightblue"

    # Use a colormap which can produce 20 distinct colors
    cmap = plt.get_cmap('tab20', len(drugs))
    drug_colors = {drug: cmap(i / (len(drugs) - 1)) for i, drug in enumerate(drugs)}

    # Build edges
    for _, row in df.iterrows():
        drug, pathway = row["DrugBank_ID"], row["Pathway"]
        graph.add_edge(drug, pathway)

    # Now compute edge colors by looking at each edge and choosing the color of the drug node.
    edge_colors = []
    for edge in graph.edges():
        if edge[0] in drug_set:
            edge_colors.append(drug_colors[edge[0]])
        elif edge[1] in drug_set:
            edge_colors.append(drug_colors[edge[1]])
        else:
            edge_colors.append("gray")

    plt.figure(figsize=(12, 8))
    pos = nx.bipartite_layout(graph, drugs)

    node_sizes = [800 if node in drug_set else 500 for node in graph.nodes()]
    node_colors = [drug_colors[node] if node in drug_set else pathway_color for node in graph.nodes()]

    nx.draw_networkx_nodes(graph, pos, node_size=node_sizes, node_color=node_colors, edgecolors='black')
    nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, width=1.5, alpha=0.7)

    # Add labels and adjust them to prevent overlap
    label_texts = [
        plt.text(pos[node][0], pos[node][1], node, fontsize=8, fontweight="bold", ha='center', va='center',
                 bbox=dict(facecolor="white", edgecolor='black', boxstyle="round,pad=0.3"))
        for node in graph.nodes()
    ]
    adjust_text(label_texts, only_move={'points': 'y', 'text': 'xy'},
                arrowprops=dict(arrowstyle="->", color='red'))

    # Final touches
    plt.title("Drug-Pathway Interaction Graph", fontsize=12, fontweight="bold")
    plt.margins(0.1)
    plt.axis("off")
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Pathway graph saved as {filename}. Please open the file manually if the image does not display correctly.")


def drug_pathways_histogram(drug_pathway_counts, filename="data/drug_pathway_histogram.png"):
    """Plots a histogram of drugs and their pathways."""
    plt.figure(figsize=(10, 6))
    plt.hist(drug_pathway_counts.values(), bins=20, align='mid', edgecolor='black')
    plt.xlabel("Number of Pathways")
    plt.ylabel("Number of Drugs")
    plt.title("Distribution of Interactions between Pathways and Drugs")
    plt.savefig(filename, dpi=300)
    plt.show()

    print(f"Pathway graph saved as {filename}. Please open the file manually if the image does not display correctly.")


def visualise_cellular_locations(cellular_locations, filename="data/cellular_locations.png"):
    """Draws a pie chart showing the frequency of targets existing in given cellular locations."""
    # Filter out entries where the value is None, empty, or 0
    filtered_cellular_locations = {key: value for key, value in cellular_locations.items() if value not in [None, "", 0]}

    # Replace empty keys or ones with "None" with "Unknown"
    filtered_cellular_locations = {
        ("Unknown" if (key == "" or key is None) else key): value
        for key, value in filtered_cellular_locations.items()
    }

    # Ensure there is still valid data to plot
    if not filtered_cellular_locations:
        print("No valid data to display.")
        return

    plt.figure(figsize=(20, 8))
    color_palette = cm.tab20.colors

    if len(filtered_cellular_locations) <= len(color_palette):
        colors = color_palette[:len(filtered_cellular_locations)]
    else:
        colors = cm.Paired.colors * (len(filtered_cellular_locations) // len(cm.Paired.colors) + 1)
        colors = colors[:len(filtered_cellular_locations)]

    # Compose the plot
    wedges = plt.pie(
        filtered_cellular_locations.values(),
        startangle=140,
        colors=colors,
        pctdistance=0.85,
        wedgeprops={"edgecolor": "black"}
    )[0]

    # Add a legend positioned to the left of the pie chart
    plt.legend(
        wedges,
        filtered_cellular_locations.keys(),
        title="Cellular Location",
        loc="center left",
        bbox_to_anchor=(-0.1, 0.5),  # Adjusts legend position to be left of the chart
        fontsize=9
    )

    plt.title("Cellular Locations of Targets", fontsize=16)
    plt.axis("equal")
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Pathway graph saved as {filename}. Please open the file manually if the image does not display correctly.")


def visualise_statuses(status_counts, filename="data/approval_statuses.png"):
    """Draws a pie chart showing the distribution of drug approval statuses."""
    plt.figure(figsize=(10, 6))
    plt.pie(
        status_counts.values(),
        labels=status_counts.keys(),
        autopct='%1.1f%%',
        startangle=140,
        colors=plt.cm.Paired.colors
    )
    plt.title("Distribution of Drug Approval Statuses")
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Pathway graph saved as {filename}. Please open the file manually if the image does not display correctly.")


def visualise_genes(df, gene, filename="data/gene_tree.png"):
    """Draws a graph showing interacting drugs for a given gene and the number of products containing that drug."""
    # Filter the DataFrame for the specified gene.
    gene_df = df[df["Gene"] == gene]
    if gene_df.empty:
        print(f"No data found for gene {gene}")
        return

    # --- Compute aggregated counts ---
    # For each interacting drug, count how many products it is involved in.
    drug_counts = gene_df["Interacting_Drug"].value_counts().to_dict()

    # --- Create a graph (mainly for bookkeeping) ---
    g = ig.Graph(directed=True)
    node_indices = {}

    # Add the central gene node.
    gene_color = "#d62728"  # red
    gene_vertex = g.add_vertex(name=gene, label=gene, type="gene", color=gene_color)
    gene_idx = gene_vertex.index
    node_indices[gene] = gene_idx

    # --- Set up a palette for interacting drugs ---
    drug_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    drug_color_mapping = {}
    drug_color_counter = 0

    # This dictionary will store, for each interacting drug, the aggregated node index.
    drug_to_aggregated = {}

    # For each interacting drug, add a drug node and its aggregated product node.
    for drug, count in drug_counts.items():
        # Assign a color (cycling through the palette).
        if drug not in drug_color_mapping:
            color = drug_colors[drug_color_counter % len(drug_colors)]
            drug_color_mapping[drug] = color
            drug_color_counter += 1
        else:
            color = drug_color_mapping[drug]

        # Add interacting drug node.
        drug_vertex = g.add_vertex(name=drug, label=drug, type="drug", color=color)
        drug_idx = drug_vertex.index
        node_indices[drug] = drug_idx

        # Edge from gene to drug.
        g.add_edge(gene_idx, drug_idx)

        # Create an aggregated product node, with label as the count.
        agg_node_name = f"{drug}_products"
        agg_label = str(count)
        agg_vertex = g.add_vertex(name=agg_node_name, label=agg_label, type="agg", color=color)
        agg_idx = agg_vertex.index
        drug_to_aggregated[drug] = agg_idx

        g.add_edge(drug_idx, agg_idx)

    # --- Compute custom layout ---
    # We'll compute positions (x,y) for each node.
    pos = {gene_idx: (0, 0)}

    # (CENTRE) Place the gene at the center.

    # (I LAYER) Place interacting drug nodes on a circle around the gene.
    radius = 300
    drug_nodes = [v for v in g.vs if v["type"] == "drug"]
    n_drugs = len(drug_nodes)

    for i, v in enumerate(drug_nodes):
        angle = 2 * np.pi * i / n_drugs
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        pos[v.index] = (x, y)

    # (II LAYER) Place aggregated product nodes (the outer layer) on another circle.
    radius_agg = 500  # radius for aggregated nodes (second layer)
    for drug, agg_idx in drug_to_aggregated.items():
        # Get the angle from the corresponding drug node.
        drug_idx = node_indices[drug]
        x_drug, y_drug = pos[drug_idx]
        angle = np.arctan2(y_drug, x_drug)
        pos[agg_idx] = (radius_agg * np.cos(angle), radius_agg * np.sin(angle))

    # --- Plot the graph ---
    fig, ax = plt.subplots(figsize=(20, 20))
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw edges.
    for edge in g.es:
        src, tgt = edge.tuple
        x1, y1 = pos[src]
        x2, y2 = pos[tgt]
        # Use the drug node's color.
        if g.vs[src]["type"] == "drug" and g.vs[tgt]["type"] == "agg":
            edge_color = g.vs[src]["color"]
        else:
            edge_color = "gray"
        ax.plot([x1, x2], [y1, y2], color=edge_color, zorder=1)

    # --- Determine scale factor for aggregated nodes ---
    agg_counts = [int(v["label"]) for v in g.vs if v["type"] == "agg"]
    max_count = max(agg_counts) if agg_counts else 1
    max_allowed_radius = 50  # maximum allowed radius for an aggregated node.
    scale_factor = max_allowed_radius / max_count

    # --- Draw nodes ---
    for v in g.vs:
        x, y = pos[v.index]
        node_type = v["type"]
        node_color = v["color"]
        if node_type in ["gene", "drug"]:
            # For drug nodes, adjust the text rotation so that the text aligns with the edge from the center.
            if node_type == "drug":
                # Compute the angle of the edge from the center (gene at (0,0)) to the drug node.
                angle = np.degrees(np.arctan2(y, x))
                # Adjust the angle to avoid upside-down text.
                if angle > 90 or angle < -90:
                    angle += 180
            else:
                angle = 0
            # Truncate long labels
            max_label_length = 400
            label_text = v["label"]
            if len(label_text) > max_label_length:
                label_text = label_text[:max_label_length] + "..."

            ax.text(
                x, y, label_text,  # Use truncated label
                ha="center", va="center",
                fontsize=14, zorder=2,
                rotation=angle,
                bbox=dict(facecolor="white", edgecolor=node_color, boxstyle="round,pad=0.3")
            )

        elif node_type == "agg":
            # For aggregated nodes, draw a circle whose size is based on the product count.
            count = int(v["label"])
            radius = count * scale_factor
            circle = plt.Circle((x, y), radius, color=node_color, zorder=2, alpha=0.3)
            ax.add_patch(circle)
            # Now overlay a text box with the product count. The text box border will be the same color as the drug.
            ax.text(
                x, y, v["label"],
                ha="center", va="center",
                fontsize=12, zorder=3,
                bbox=dict(facecolor="white", edgecolor=node_color, boxstyle="round,pad=0.3")
            )

    plt.title(f"Drugs interacting with gene {gene}, and the number of products containing the genes")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Graph saved as {filename}. Please open the file manually if the image does not display correctly.")


def visualise_drug_target_amino(df, drug_id, filename="data/drug_target_tree.png"):
    """
    Draws a graph showing targets for a given drug and their corresponding amino acid counts.

    Parameters:
    - df: DataFrame containing "DrugBank_ID", "Target_Name", and "Amino_Acid_Count".
    - drug_id: The DrugBank ID of the drug to visualize.
    - filename: Path to save the generated graph image.
    """
    if df.empty:
        print(f"No data found for DrugBank_ID {drug_id}")
        return

    # Filter the DataFrame for the specified drug.
    drug_df = df[df["DrugBank_ID"] == drug_id]
    if drug_df.empty:
        print(f"No data found for DrugBank_ID {drug_id}")
        return

    # --- Compute aggregated counts ---
    # Each target has one corresponding amino acid count.
    target_counts = drug_df.set_index("Target_Name")["Amino_Acid_Count"].to_dict()

    # --- Create a graph ---
    g = ig.Graph(directed=True)
    node_indices = {}

    # Add the central drug node.
    drug_color = "#d62728"  # Red
    drug_vertex = g.add_vertex(name=drug_id, label=drug_id, type="drug", color=drug_color)
    drug_idx = drug_vertex.index
    node_indices[drug_id] = drug_idx

    # --- Set up colors for targets ---
    target_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    target_color_mapping = {}
    color_counter = 0

    # This dictionary will store, for each target, the amino acid count node index.
    target_to_aa = {}

    # For each target, add a target node and its amino acid count node.
    for target, aa_count in target_counts.items():
        # Assign a color (cycling through the palette).
        if target not in target_color_mapping:
            color = target_colors[color_counter % len(target_colors)]
            target_color_mapping[target] = color
            color_counter += 1
        else:
            color = target_color_mapping[target]

        # Add target node.
        target_vertex = g.add_vertex(name=target, label=target, type="target", color=color)
        target_idx = target_vertex.index
        node_indices[target] = target_idx

        # Edge from drug to target.
        g.add_edge(drug_idx, target_idx)

        # Create an amino acid count node.
        aa_node_name = f"{target}_AA"
        aa_label = f"{aa_count} AA"
        aa_vertex = g.add_vertex(name=aa_node_name, label=aa_label, type="aa", color=color)
        aa_idx = aa_vertex.index
        target_to_aa[target] = aa_idx

        # Edge from target to amino acid count.
        g.add_edge(target_idx, aa_idx)

    # --- Compute custom layout ---
    pos = {drug_idx: (0, 0)}

    # (CENTRE) Place the drug at the center.

    # (I LAYER) Place targets on a circle around the drug.
    radius = 300
    target_nodes = [v for v in g.vs if v["type"] == "target"]
    n_targets = len(target_nodes)

    for i, v in enumerate(target_nodes):
        angle = 2 * np.pi * i / max(n_targets, 1)  # Avoid division by zero
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        pos[v.index] = (x, y)

    # (II LAYER) Place amino acid count nodes (outer layer) around targets.
    radius_aa = 500
    for target, aa_idx in target_to_aa.items():
        # Get the angle from the corresponding target node.
        target_idx = node_indices[target]
        x_target, y_target = pos[target_idx]
        angle = np.arctan2(y_target, x_target)
        pos[aa_idx] = (radius_aa * np.cos(angle), radius_aa * np.sin(angle))

    # --- Plot the graph ---
    fig, ax = plt.subplots(figsize=(20, 20))
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw edges.
    for edge in g.es:
        src, tgt = edge.tuple
        x1, y1 = pos[src]
        x2, y2 = pos[tgt]
        # Use the target node's color.
        if g.vs[src]["type"] == "target" and g.vs[tgt]["type"] == "aa":
            edge_color = g.vs[src]["color"]
        else:
            edge_color = "gray"
        ax.plot([x1, x2], [y1, y2], color=edge_color, zorder=1)

    # --- Draw nodes ---
    for v in g.vs:
        x, y = pos[v.index]
        node_type = v["type"]
        node_color = v["color"]
        if node_type in ["drug", "target"]:
            # Compute the angle to avoid upside-down text.
            angle = np.degrees(np.arctan2(y, x))
            if angle > 90 or angle < -90:
                angle += 180

            ax.text(
                x, y, v["label"],
                ha="center", va="center",
                fontsize=14, zorder=2,
                rotation=angle,
                bbox=dict(facecolor="white", edgecolor=node_color, boxstyle="round,pad=0.3")
            )

        elif node_type == "aa":
            # Draw a text label for the amino acid count.
            ax.text(
                x, y, v["label"],
                ha="center", va="center",
                fontsize=12, zorder=3,
                bbox=dict(facecolor="white", edgecolor=node_color, boxstyle="round,pad=0.3")
            )

    plt.title(f"Targets of drug {drug_id} and their amino acid counts")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Graph saved as {filename}. Please open the file manually if the image does not display correctly.")

