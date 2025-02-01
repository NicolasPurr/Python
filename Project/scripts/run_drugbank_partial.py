# scripts/run_drugbank_partial.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drugbank.parsers import *
from drugbank.visualisers import *

if __name__ == "__main__":
    with open("data/drugbank_partial.xml", "r", encoding="utf-8") as file:
        xml_content = file.read()

    # Task 1
    print(f"Parsing drugs...")
    drugs = parse_drugs(xml_content)
    print(drugs)

    # Task 2
    print(f"\nParsing synonyms...")
    synonyms = parse_synonyms(xml_content)
    print(f"Generated example graphs for drugs: DB00001, DB00046, DB0098, DB0108")
    visualise_synonyms("DB00001", synonyms)
    visualise_synonyms("DB00046", synonyms)
    visualise_synonyms("DB00098", synonyms)
    visualise_synonyms("DB00108", synonyms)

    # Task 3
    print(f"\nParsing products...")
    products = parse_products(xml_content)
    print(products)

    # Task 4
    print(f"\nParsing pathways...")
    pathways, drug_pathway_count = parse_pathways(xml_content)
    print(f"Number of different pathways: {len(pathways)}")

    # Task 5
    visualise_drug_pathways(pathways)

    # Task 6
    for drug, count in drug_pathway_count.items():
        print(f"Drug: {drug}, Pathway Count: {count}")
    drug_pathways_histogram(drug_pathway_count)


    # Task 7
    print(f"\nParsing targets...")
    targets, cellular_locations = parse_targets(xml_content)
    print(targets)
    print(f"Example target: Lepirudin")
    print(targets[targets["Drug"] == "Lepirudin"])

    # Task 8
    visualise_cellular_locations(cellular_locations)

    # Task 9
    print(f"\nParsing approval statuses...")
    status, approved_not_withdrawn, status_count = parse_approval_status(xml_content)
    print(f"Number of drugs which have been approved and not withdrawn: {approved_not_withdrawn}")
    visualise_statuses(status_count)

    # Task 10
    print(f"\nParsing drug interactions...")
    drug_interactions = parse_drug_interactions(xml_content)
    print(drug_interactions)

    # Task 11
    print(f"\nParsing gene interactions...")
    genes = parse_genes(xml_content)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(genes)
    print(f"\nExample: F2")
    print(genes[genes["Gene"] == "F2"])

    print(f"\nExample graph: ICAM1. Open the generated image to view in full size")
    visualise_genes(genes, "ICAM1")

    # Task 12
