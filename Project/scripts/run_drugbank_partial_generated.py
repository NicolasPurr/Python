# scripts/run_drugbank_partial.py
import sys
import os
import random
from lxml import etree

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drugbank.parsers import *
from drugbank.visualisers import *

relative_file_path = "data/drugbank_partial_generated.xml"
TOTAL_CONSECUTIVE_IDS=19900

# Task 13
if __name__ == "__main__":
    try:
        # Parse the input XML.
        tree = etree.parse(relative_file_path)
        root = tree.getroot()
    except etree.ParseError as e:
        print(f"Error parsing XML: {e}")
        exit(1)

    # Task 13.1
    print(f"Parsing drugs...")
    drugs = parse_drugs(root)
    print(drugs)

    # Task 13.2
    print(f"\nParsing synonyms...")
    synonyms = parse_synonyms(root)
    i = random.randint(1, TOTAL_CONSECUTIVE_IDS)
    j = random.randint(1, TOTAL_CONSECUTIVE_IDS)
    print(f"Generated example graphs for drug IDs: {i}, {j}")
    visualise_synonyms(f"{i}", synonyms)
    visualise_synonyms(f"{j}", synonyms)

    # Task 13.3
    print(f"\nParsing products...")
    products = parse_products(root)
    print(products)

    # Task 13.4
    print(f"\nParsing pathways...")
    pathways, drug_pathway_count = parse_pathways(root)
    print(f"Number of different pathways: {len(pathways)}")

    # Task 13.5
    visualise_drug_pathways(pathways)

    # Task 13.6
    for drug, count in drug_pathway_count.items():
        print(f"Drug: {drug}, Pathway Count: {count}")
    drug_pathways_histogram(drug_pathway_count)

    # Task 13.7
    print(f"\nParsing targets...")
    targets, cellular_locations = parse_targets(root)
    print(targets)
    print(f"Example target: Lepirudin")
    print(targets[targets["Drug"] == "Lepirudin"])

    # Task 13.8
    visualise_cellular_locations(cellular_locations)

    # Task 13.9
    print(f"\nParsing approval statuses...")
    status, approved_not_withdrawn, status_count = parse_approval_status(root)
    print(f"Number of drugs which have been approved and not withdrawn: {approved_not_withdrawn}")
    visualise_statuses(status_count)

    # Task 13.10
    print(f"\nParsing drug interactions...")
    drug_interactions = parse_drug_interactions(root)
    print(drug_interactions)

    # Task 13.11
    print(f"\nParsing gene interactions...")
    genes = parse_genes(root)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(genes)
    print(f"\nExample: F2")
    print(genes[genes["Gene"] == "F2"])

    print(f"\nExample graph: ICAM1. Open the generated image to view in full size")
    visualise_genes(genes, "ICAM1")

    # Task 13.12
    i = random.randint(1, TOTAL_CONSECUTIVE_IDS)
    if targets is not None:
        print(f"The targets have already been parsed. Reusing...")
    else:
        print(f"Parsing targets...")
        targets, cellular_locations = parse_targets(root)

    print(f"Example amino acid counts for DB00002:")
    aminos = get_target_amino_acid_count_for_drug(i, targets)
    visualise_drug_target_amino(aminos, i)