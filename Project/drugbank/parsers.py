# drugbank/parsers.py
import pandas as pd
import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_drugs(xml_content):
    """Parses DrugBank XML and extracts drug details."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()   # Return an empty DataFrame in case of XML parsing error

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    ns = {"db": "http://www.drugbank.ca"}
    data = []

    # Only process top-level <drug> elements
    for drug in root.findall("db:drug", ns):
        try:
            # Get only the primary drugbank-id
            drug_id_element = drug.find("db:drugbank-id[@primary='true']", ns)
            #if drug_id_element is None:
            #    continue
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

    # Convert to DataFrame and remove duplicate rows
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["DrugBank_ID"])  # Ensure unique entries

    return df


def parse_synonyms(xml_content):
    """Extracts drug synonyms from XML."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

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


def parse_products(xml_content):
    """Extracts product information from XML."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    ns = {"db": "http://www.drugbank.ca"}
    data = []

    # Process top-level <drug> elements
    for drug in root.findall("db:drug", ns):
        primary_id = drug.find("db:drugbank-id[@primary='true']", ns)
        products = drug.findall("db:products/db:product", ns)

        if primary_id is not None:
            drug_id = primary_id.text
            product_list = []

            for product in products:
                product_name = product.find("db:name", ns)
                manufacturer = product.find("db:manufacturer", ns)
                ndc_code = product.find("db:ndc-id", ns)
                form = product.find("db:dosage-form", ns)
                route = product.find("db:route", ns)
                strength = product.find("db:strength", ns)
                country = product.find("db:country", ns)
                agency = product.find("db:approval-agency", ns)

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


def parse_pathways(xml_content):
    """Parses DrugBank XML and extracts drug details."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    ns = "{http://www.drugbank.ca}"

    data = []
    drug_pathway_counts = defaultdict(int)

    for drug in root.findall(f".//{ns}drug"):
        drug_id = drug.find(f"{ns}drugbank-id").text
        drug_name = drug.find(f"{ns}name").text
        pathways = drug.findall(f".//{ns}pathway")

        for pathway in pathways:
            pathway_name = pathway.find(f"{ns}name").text
            pathway_type = pathway.find(f"{ns}category").text
            data.append([drug_id, drug_name, pathway_name, pathway_type])
            drug_pathway_counts[drug_id] += 1

    df = pd.DataFrame(data, columns=["DrugBank_ID", "Drug", "Pathway", "Type"])
    return df, drug_pathway_counts


def parse_polypeptide(polypeptide, ns):
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


def parse_genatlas_id(polypeptide, ns):
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


def parse_targets(xml_content):
    """Parses DrugBank XML and targets."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame(), defaultdict(int)

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame(), defaultdict(int)

    ns = "{http://www.drugbank.ca}"

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
                    polypeptide, ns)

                genatlas_id = parse_genatlas_id(polypeptide, ns)

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

def parse_approval_status(xml_content):
    """Parses DrugBank XML and extracts information on drugs' approval statuses."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    ns = "{http://www.drugbank.ca}"

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


def parse_drug_interactions(xml_content):
    """Parses DrugBank XML and extracts information on drugs' interactions with other drugs."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of XML parsing error

    ns = "{http://www.drugbank.ca}"
    
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


def parse_genes(xml_content):
    """Extracts drug-gene interactions and their related drug products from XML."""
    if not xml_content.strip():
        print("Warning: The provided XML content is empty.")
        return pd.DataFrame()  # Return an empty DataFrame if the XML is empty

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if XML parsing fails

    namespace = "{http://www.drugbank.ca}"
    data = []

    drug_products_dict = {}

    # First, collect all drugs and their associated products into a dictionary
    for drug in root.findall(f"{namespace}drug"):
        drug_id = drug.find(f"{namespace}drugbank-id[@primary='true']").text

        products = []
        for product in drug.findall(f"{namespace}products/{namespace}product"):
            product_name = product.find(f"{namespace}name").text

            product_id = None
            product_id_type = None

            if product.find(f"{namespace}ndc-id") is not None and product.find(f"{namespace}ndc-id").text:
                product_id = product.find(f"{namespace}ndc-id").text
                product_id_type = "ndc-id"
            elif product.find(f"{namespace}ndc-product-code") is not None and product.find(
                    f"{namespace}ndc-product-code").text:
                product_id = product.find(f"{namespace}ndc-product-code").text
                product_id_type = "ndc-product-code"
            elif product.find(f"{namespace}dpd-id") is not None and product.find(f"{namespace}dpd-id").text:
                product_id = product.find(f"{namespace}dpd-id").text
                product_id_type = "dpd-id"
            elif product.find(f"{namespace}ema-ma-number") is not None and product.find(
                    f"{namespace}ema-ma-number").text:
                product_id = product.find(f"{namespace}ema-ma-number").text
                product_id_type = "ema-ma-number"

            if product_id:
                products.append((product_name, product_id, product_id_type))

        drug_products_dict[drug_id] = products

    for drug in root.findall(f"{namespace}drug"):
        drug_name = drug.find(f"{namespace}name").text

        # Extract interacting genes
        for target in drug.findall(f"{namespace}targets/{namespace}target"):
            gene_name_tag = target.find(f"{namespace}polypeptide/{namespace}gene-name")
            if gene_name_tag is not None:
                gene_name = gene_name_tag.text

                # Extract interacting drugs
                interactions = [interaction.find(f"{namespace}name").text for interaction in
                                drug.findall(f"{namespace}drug-interactions/{namespace}drug-interaction")]
                interaction_ids = [interaction.find(f"{namespace}drugbank-id").text for interaction in
                                   drug.findall(f"{namespace}drug-interactions/{namespace}drug-interaction")]

                # Extract products for each interaction drug
                for interaction, interaction_id in zip(interactions, interaction_ids):
                    if interaction_id in drug_products_dict:
                        products = drug_products_dict[interaction_id]
                        for product_name, product_id, product_id_type in products:
                            data.append((gene_name, drug_name, interaction, product_name, product_id, product_id_type))

    df = pd.DataFrame(data,
                      columns=["Gene", "Drug", "Interacting_Drug", "Product_Name", "Product_ID", "Product_ID_Type"])

    # Drop duplicates
    return df.drop_duplicates()
