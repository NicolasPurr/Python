# scripts/run_drugbank_partial_generated.py
import sys
import os

# Add the project root to sys.path so that we can import our modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lxml import etree
import pandas as pd

from drugbank.iter_parsers import (
    parse_drug,
    parse_synonyms_for_drug,
    parse_products_for_drug,
    parse_targets_for_drug,
    parse_approval_status_for_drug,
    parse_drug_interactions_for_drug,
)
from drugbank.visualisers import (
    visualise_synonyms,
    visualise_cellular_locations,
    visualise_statuses,
)

# Global accumulators for parsed data.
drugs_data = []             # List of drug details dictionaries.
synonyms_data = {}          # {drug_id: [synonym, ...]}
products_data = {}          # {drug_id: [product, ...]}
pathways_data = []          # List of tuples: (drug_id, pathway)
drug_pathway_count = {}     # {drug_id: count}
targets_data = []           # List of target dictionaries.
cellular_locations = {}     # {cellular_location: count}
approval_status_count = {}  # {status: count}
drug_interactions = []      # List of interaction dictionaries.
genes_data = []             # List of gene dictionaries.

relative_file_path = "data/drugbank_partial_generated.xml"


def main():
    absolute_path = os.path.abspath(relative_file_path)
    if not os.path.exists(absolute_path):
        print(f"File not found: {absolute_path}")
        sys.exit(1)

    print("Processing the XML file with iterparse...")

    ns = "http://www.drugbank.ca"
    context = etree.iterparse(absolute_path, events=("end",), tag=f"{{{ns}}}drug")
    approved_not_withdrawn_count = 0

    for event, drug_elem in context:
        # Task 1: Drug details.
        details = parse_drug(drug_elem)
        if details:
            drugs_data.append(details)

        # Task 2: Synonyms.
        syn = parse_synonyms_for_drug(drug_elem)
        if syn:
            drug_id = syn["DrugBank_ID"]
            if drug_id in synonyms_data:
                synonyms_data[drug_id] = list(set(synonyms_data[drug_id] + syn["Synonyms"]))
            else:
                synonyms_data[drug_id] = syn["Synonyms"]

        # Task 3: Products.
        prod = parse_products_for_drug(drug_elem)
        if prod:
            products_data[prod["DrugBank_ID"]] = prod["Products"]

        # Task 7 & 8: Targets and cellular locations.
        targs = parse_targets_for_drug(drug_elem)
        if targs:
            targets_data.extend(targs["Targets"])
            for target in targs["Targets"]:
                cl = target.get("Cellular_Location", "Unknown")
                cellular_locations[cl] = cellular_locations.get(cl, 0) + 1

        # Task 9: Approval statuses.
        app = parse_approval_status_for_drug(drug_elem)
        if app:
            for status, count in app["Status"].items():
                approval_status_count[status] = approval_status_count.get(status, 0) + count
            if "Approved" in app["Status"] and "Withdrawn" not in app["Status"]:
                approved_not_withdrawn_count += 1

        # Task 10: Drug interactions.
        inter = parse_drug_interactions_for_drug(drug_elem)
        if inter:
            drug_interactions.extend(inter["Interactions"])

        # Clear element from memory.
        drug_elem.clear()
        while drug_elem.getprevious() is not None:
            del drug_elem.getparent()[0]

    print("Parsing complete.")
    print(f"Parsed {len(drugs_data)} drugs.")

    # Task 1: Drug Details.
    print("\nDrug Details:")
    df_drugs = pd.DataFrame(drugs_data)
    print(df_drugs)

    # Task 2: Synonyms.
    print("\nSynonyms:")
    df_syn = pd.DataFrame([{"DrugBank_ID": k, "Synonyms": v} for k, v in synonyms_data.items()])
    print(df_syn)
    for drug_id in ["DB00001", "DB00046", "DB00098", "DB00108"]:
        if drug_id in synonyms_data:
            print(f"Visualising synonyms for {drug_id}...")
            visualise_synonyms(drug_id, df_syn)
        else:
            print(f"No synonyms found for {drug_id}.")

    # Task 3: Products.
    print("\nProducts:")
    df_products = pd.DataFrame(
        [{"DrugBank_ID": did, "Products": prods} for did, prods in products_data.items()]
    )
    print(df_products)

    # Task 7 & 8: Targets and cellular locations.
    print("\nTargets:")
    df_targets = pd.DataFrame(targets_data)
    print(df_targets)
    print("\nExample target: Lepirudin")
    if "Drug" in df_targets.columns:
        print(df_targets[df_targets["Drug"] == "Lepirudin"])
    else:
        print("No 'Drug' column in targets DataFrame.")
    visualise_cellular_locations(cellular_locations)

    # Task 9: Approval statuses.
    print("\nApproval Statuses:")
    print(f"Number of drugs approved and not withdrawn: {approved_not_withdrawn_count}")
    visualise_statuses(approval_status_count)

    # Task 10: Drug Interactions.
    print("\nDrug Interactions:")
    df_interactions = pd.DataFrame(drug_interactions)
    print(df_interactions)


if __name__ == "__main__":
    main()
