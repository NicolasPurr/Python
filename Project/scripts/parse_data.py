# scripts/parse_data.py

from Project.drugbank import *
from parsers import parse_pathways, parse_targets, parse_approval_status, parse_drug_interactions

if __name__ == "__main__":
    with open("../data/drugbank_partial.xml", "r", encoding="utf-8") as file:
        xml_content = file.read()

    # Task 1
    print(f"Parsing drugs...")
    drugs = parse_drugs(xml_content)
    print(drugs)

    # Task 2
    print(f"Parsing synonyms...")
    synonyms = parse_synonyms(xml_content)
    print(f"\tExample graphs: DB00001, DB00046, DB0098, DB0108")
    draw_synonym_graph("DB00001", synonyms)
    draw_synonym_graph("DB00046", synonyms)
    draw_synonym_graph("DB00098", synonyms)
    draw_synonym_graph("DB00108", synonyms)

    # Task 3
    print(f"Parsing products...")
    products = parse_products(xml_content)

    # Task 4
    print(f"Parsing pathways...")
    pathways, drug_pathway_count = parse_pathways(xml_content)
    print(f"\tNumber of different pathways: {len(pathways)}")

    # Task 5
    draw_bipartite_graph(pathways)

    # Task 6
    plot_histogram(drug_pathway_count)

    # Task 7
    print(f"Parsing targets...")
    targets, cellular_locations = parse_targets(xml_content)
    print(targets)
    print(f"\tExample target: Lepirudin")
    print(targets[targets["Drug"] == "Lepirudin"])

    # Task 8
    plot_circular(cellular_locations)

    # Task 9
    print(f"Parsing approval statuses...")
    status, approved_not_withdrawn, status_count = parse_approval_status(xml_content)
    print(f"\tNumber of drugs which have been approved and not withdrawn: {approved_not_withdrawn}")
    plot_status(status_count)

    # Task 10
    print(f"Parsing drug interactions...")
    drug_interactions = parse_drug_interactions(xml_content)
    print(drug_interactions)

    # Task 11

    # Task 12