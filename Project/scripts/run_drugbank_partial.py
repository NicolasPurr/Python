# scripts/run_drugbank_partial.py
import sys
import os
from lxml import etree

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drugbank.parsers import *
from drugbank.visualisers import *

relative_file_path = "data/drugbank_partial.xml"

if __name__ == "__main__":
    try:
        # Parse the input XML.
        tree = etree.parse(relative_file_path)
        root = tree.getroot()
    except etree.ParseError as e:
        print(f"Error parsing XML: {e}")
        exit(1)

    # Task 1
    print(f"Parsing drugs...")
    drugs = parse_drugs(root)
    print(drugs)

    # Task 2
    print(f"\nParsing synonyms...")
    synonyms = parse_synonyms(root)
    print(f"Generated example graphs for drugs: DB00001, DB00046, DB0098, DB0108")
    visualise_synonyms("DB00001", synonyms)
    visualise_synonyms("DB00046", synonyms)
    visualise_synonyms("DB00098", synonyms)
    visualise_synonyms("DB00108", synonyms)

    # Task 3
    print(f"\nParsing products...")
    products = parse_products(root)
    print(products)

    # Task 4
    print(f"\nParsing pathways...")
    pathways, drug_pathway_count = parse_pathways(root)
    print(f"Number of different pathways: {len(pathways)}")

    # Task 5
    visualise_drug_pathways(pathways)

    # Task 6
    for drug, count in drug_pathway_count.items():
        print(f"Drug: {drug}, Pathway Count: {count}")
    drug_pathways_histogram(drug_pathway_count)


    # Task 7
    print(f"\nParsing targets...")
    targets, cellular_locations = parse_targets(root)
    print(targets)
    print(f"Example target: Lepirudin")
    print(targets[targets["Drug"] == "Lepirudin"])

    # Task 8
    visualise_cellular_locations(cellular_locations)

    # Task 9
    print(f"\nParsing approval statuses...")
    status, approved_not_withdrawn, status_count = parse_approval_status(root)
    print(f"Number of drugs which have been approved and not withdrawn: {approved_not_withdrawn}")
    visualise_statuses(status_count)

    # Task 10
    print(f"\nParsing drug interactions...")
    drug_interactions = parse_drug_interactions(root)
    print(drug_interactions)

    # Task 11
    print(f"\nParsing gene interactions...")
    genes = parse_genes(root)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(genes)
    print(f"Example: F2")
    print(genes[genes["Gene"] == "F2"])

    print(f"Example graph: ICAM1. Open the generated image to view in full size:")
    visualise_genes(genes, "ICAM1")

    # Task 12
    if targets is not None:
        print(f"The targets have already been parsed. Reusing...")
    else:
        print(f"Parsing targets...")
        targets, cellular_locations = parse_targets(root)

    print(f"Example amino acid counts for DB00002:")
    aminos = get_target_amino_acid_count_for_drug("DB00002", targets)
    print(aminos)
    visualise_drug_target_amino(aminos, "DB00002")