# drugbank/parsers.py
import pandas as pd
from collections import defaultdict

ns = "{http://www.drugbank.ca}"

def parse_drugs(root):
    """Parses DrugBank XML and extracts drug details."""
    data = []

    # Only process top-level <drug> elements
    for drug in root.findall(f"{ns}drug"):
        try:
            # Get only the primary drugbank-id
            drug_id_element = drug.find(f"{ns}drugbank-id[@primary='true']")
            if drug_id_element is None:
                continue
            drug_id = drug_id_element.text if drug_id_element is not None else None

            name = drug.find(f"{ns}name").text \
                if drug.find(f"{ns}name") is not None else None
            drug_type = drug.get("type")
            description = drug.find(f"{ns}description").text \
                if drug.find(f"{ns}description") is not None else None
            dosage_form = drug.find(f"{ns}dosages/{ns}dosage/{ns}form").text \
                if drug.find(f"{ns}dosages/{ns}dosage/{ns}form") is not None else None
            indications = drug.find(f"{ns}indication").text \
                if drug.find(f"{ns}indication") is not None else None
            mechanism_of_action = drug.find(f"{ns}mechanism-of-action").text \
                if drug.find(f"{ns}mechanism-of-action") is not None else None

            food_interactions = [
                fi.text for fi in drug.findall(f".//{ns}food-interactions/{ns}food-interaction")
            ]
            food_interactions = "; ".join(food_interactions) \
                if food_interactions else None

            data.append({
                "DrugBank_ID": drug_id,
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

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["DrugBank_ID"])

    return df


def parse_synonyms(root):
    """
    Extracts drug synonyms from XML.

    Returns: a dataframe with columns ["DrugBank_ID", "Synonyms"], where "Synonyms" is a list of synonyms.
    """
    data = []

    # Only process top-level <drug> elements
    for drug in root.findall(f"{ns}drug"):
        primary_id = drug.find(f"{ns}drugbank-id[@primary='true']")
        synonyms = drug.findall(f"{ns}synonyms/{ns}synonym")

        if primary_id is not None:
            drug_id = primary_id.text
            synonym_list = [syn.text for syn in synonyms] if synonyms else []
            data.append({"DrugBank_ID": drug_id, "Synonyms": synonym_list})

    return pd.DataFrame(data)


def parse_products(root):
    """Extracts product information from XML."""
    data = []

    for drug in root.findall(f"{ns}drug"):
        primary_id = drug.find(f"{ns}drugbank-id[@primary='true']")
        products = drug.findall(f"{ns}products/{ns}product")

        if primary_id is not None:
            drug_id = primary_id.text
            product_list = []

            for product in products:
                product_name = product.find(f"{ns}name")
                manufacturer = product.find(f"{ns}manufacturer")
                ndc_code = product.find(f"{ns}ndc-id")
                form = product.find(f"{ns}dosage-form")
                route = product.find(f"{ns}route")
                strength = product.find(f"{ns}strength")
                country = product.find(f"{ns}country")
                agency = product.find(f"{ns}approval-agency")

                product_dict = {
                    "Product Name": product_name.text if product_name is not None else None,
                    "Manufacturer": manufacturer.text if manufacturer is not None else None,
                    "NDC Code": ndc_code.text if ndc_code is not None else None,
                    "Form": form.text if form is not None else None,
                    "Route": route.text if route is not None else None,
                    "Strength": strength.text if strength is not None else None,
                    "Country": country.text if country is not None else None,
                    "Approval Agency": agency.text if agency is not None else None
                }

                # Append the product to the list for this drug
                product_list.append(product_dict)

            product_list = pd.DataFrame(product_list).drop_duplicates().to_dict(orient="records")

            # Append the drug_id and its associated product list
            data.append({"DrugBank_ID": drug_id, "Products": product_list})

    df = pd.DataFrame(data)

    if not df.empty:
        df.set_index("DrugBank_ID", inplace=True)

    return df


def parse_pathways(root):
    """
    Parses DrugBank XML and creates edges from each pathway to each drug
    found under the pathway's <drugs> element. The drug node will be represented
    by its DrugBank ID.

    Returns:
        df: A DataFrame with columns ["DrugBank_ID", "Pathway"] where each
            row represents an edge between a pathway and a drug (by its ID).
        drug_pathway_counts: A defaultdict(int) counting the number of pathway connections
            per drug ID.
    """
    data = []
    drug_pathway_counts = defaultdict(int)

    # Find all pathway elements anywhere in the XML
    for pathway in root.findall(f".//{ns}pathway"):
        pathway_name_el = pathway.find(f"{ns}name")
        if pathway_name_el is None:
            continue
        pathway_name = pathway_name_el.text

        # Look for a <drugs> element within the pathway
        drugs_element = pathway.find(f"{ns}drugs")
        if drugs_element is None:
            continue

        # For each inner drug listed under <drugs>, extract its DrugBank ID from the element text.
        for inner_drug in drugs_element.findall(f"{ns}drug"):
            drug_id = inner_drug.find(f"{ns}drugbank-id")
            if drug_id is None:
                continue
            drug_id = drug_id.text.strip()

            data.append([drug_id, pathway_name])
            drug_pathway_counts[drug_id] += 1

    df = pd.DataFrame(data, columns=["DrugBank_ID", "Pathway"])
    return df, drug_pathway_counts


def parse_polypeptide(polypeptide):
    """Helper function to extract polypeptide information."""
    source = polypeptide.get("source", "Unknown")
    ext_id = polypeptide.get("id", "Unknown")
    polypeptide_name = polypeptide.find(f"{ns}name").text if polypeptide.find(f"{ns}name") is not None else "Unknown"
    gene_name = polypeptide.find(f"{ns}gene-name").text if polypeptide.find(f"{ns}gene-name") is not None else "Unknown"
    chromosome = polypeptide.find(f"{ns}chromosome-location").text if polypeptide.find(
        f"{ns}chromosome-location") is not None else "Unknown"
    cellular_location = polypeptide.find(f"{ns}cellular-location").text if polypeptide.find(
        f"{ns}cellular-location") is not None else "Unknown"

    return source, ext_id, polypeptide_name, gene_name, chromosome, cellular_location


def parse_genatlas_id(polypeptide):
    """Helper function to extract GenAtlas ID from the external-identifier tags under polypeptide."""
    genatlas_id = "Unknown"
    external_identifiers = polypeptide.findall(f".//{ns}external-identifier")

    for ext_id in external_identifiers:
        resource = ext_id.find(f"{ns}resource").text if ext_id.find(f"{ns}resource") is not None else ""
        if resource == "GenAtlas":
            genatlas_id = ext_id.find(f"{ns}identifier").text if ext_id.find(
                f"{ns}identifier") is not None else "Unknown"
            break
    return genatlas_id


def parse_targets(root):
    """Parses DrugBank XML and targets."""
    target_data = []
    cellular_locations = defaultdict(int)

    for drug in root.findall(f".//{ns}drug"):
        drug_name = drug.find(f"{ns}name").text
        targets = drug.findall(f".//{ns}target")

        for target in targets:
            target_id = target.find(f"{ns}id").text

            polypeptide = target.find(f"{ns}polypeptide")
            if polypeptide is not None:
                source, ext_id, polypeptide_name, gene_name, chromosome, cellular_location = parse_polypeptide(
                    polypeptide)

                genatlas_id = parse_genatlas_id(polypeptide)

                target_data.append(
                    [drug_name, target_id, source, ext_id, polypeptide_name, gene_name, genatlas_id, chromosome,
                     cellular_location]
                )
                cellular_locations[cellular_location] += 1

    df = pd.DataFrame(target_data,
                      columns=["Drug", "Target_ID", "Source", "External_ID", "Polypeptide_Name", "Gene_Name",
                               "GenAtlas_ID", "Chromosome", "Cellular_Location"])

    df.sort_values(by=["Drug"], inplace=True)

    return df, cellular_locations


def parse_approval_status(root):
    """Parses DrugBank XML and extracts information on drugs' approval statuses."""
    status_counts = defaultdict(int)
    approved_not_withdrawn = 0

    for drug in root.findall(f".//{ns}drug"):
        groups = [group.text for group in drug.findall(f".//{ns}group")]

        if "approved" in groups:
            status_counts["Approved"] += 1
            if "withdrawn" not in groups:
                approved_not_withdrawn += 1
        if "withdrawn" in groups:
            status_counts["Withdrawn"] += 1
        if "experimental" in groups or "investigational" in groups:
            status_counts["Experimental/Investigational"] += 1
        if "veterinary" in groups:
            status_counts["Veterinary"] += 1

    df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])

    return df, approved_not_withdrawn, status_counts


def parse_drug_interactions(root):
    """Parses DrugBank XML and extracts information on drugs' interactions with other drugs."""
    interaction_data = []

    for drug in root.findall(f".//{ns}drug"):
        drug_name = drug.find(f"{ns}name").text
        interactions = drug.findall(f".//{ns}drug-interaction")

        for interaction in interactions:
            interacting_drug_id = interaction.find(f"{ns}drugbank-id").text
            interacting_drug_name = interaction.find(f"{ns}name").text
            interaction_desc = interaction.find(f"{ns}description").text

            interaction_data.append([drug_name, interacting_drug_id, interacting_drug_name, interaction_desc])

    df = pd.DataFrame(interaction_data,
                                   columns=["Drug", "Interacting_Drug_ID", "Interacting_Drug", "Description"])

    return df


def parse_genes(root):
    """Extracts drug-gene interactions and their related drug products from XML."""
    data = []

    drug_products_dict = {}

    # First, collect all drugs and their associated products into a dictionary
    for drug in root.findall(f"{ns}drug"):
        drug_id = drug.find(f"{ns}drugbank-id[@primary='true']").text

        products = []
        for product in drug.findall(f"{ns}products/{ns}product"):
            product_name = product.find(f"{ns}name").text

            product_id = None
            product_id_type = None

            if product.find(f"{ns}ndc-id") is not None and product.find(f"{ns}ndc-id").text:
                product_id = product.find(f"{ns}ndc-id").text
                product_id_type = "ndc-id"
            elif product.find(f"{ns}ndc-product-code") is not None and product.find(
                    f"{ns}ndc-product-code").text:
                product_id = product.find(f"{ns}ndc-product-code").text
                product_id_type = "ndc-product-code"
            elif product.find(f"{ns}dpd-id") is not None and product.find(f"{ns}dpd-id").text:
                product_id = product.find(f"{ns}dpd-id").text
                product_id_type = "dpd-id"
            elif product.find(f"{ns}ema-ma-number") is not None and product.find(
                    f"{ns}ema-ma-number").text:
                product_id = product.find(f"{ns}ema-ma-number").text
                product_id_type = "ema-ma-number"

            if product_id:
                products.append((product_name, product_id, product_id_type))

        drug_products_dict[drug_id] = products

    for drug in root.findall(f"{ns}drug"):
        drug_name = drug.find(f"{ns}name").text

        # Extract interacting genes
        for target in drug.findall(f"{ns}targets/{ns}target"):
            gene_name_tag = target.find(f"{ns}polypeptide/{ns}gene-name")
            if gene_name_tag is not None:
                gene_name = gene_name_tag.text

                # Extract interacting drugs
                interactions = [interaction.find(f"{ns}name").text for interaction in
                                drug.findall(f"{ns}drug-interactions/{ns}drug-interaction")]
                interaction_ids = [interaction.find(f"{ns}drugbank-id").text for interaction in
                                   drug.findall(f"{ns}drug-interactions/{ns}drug-interaction")]

                # Extract products for each interaction drug
                for interaction, interaction_id in zip(interactions, interaction_ids):
                    if interaction_id in drug_products_dict:
                        products = drug_products_dict[interaction_id]
                        for product_name, product_id, product_id_type in products:
                            data.append((gene_name, drug_name, interaction, product_name, product_id, product_id_type))

    df = pd.DataFrame(data,
                      columns=["Gene", "Drug", "Interacting_Drug", "Product_Name", "Product_ID", "Product_ID_Type"])

    return df.drop_duplicates()
