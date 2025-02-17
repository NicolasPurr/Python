# drugbank/iter_parsers.py

# The default namespace URL.
NS_URL = "{http://www.drugbank.ca}"


def parse_drug(drug):
    """Parse a single <drug> element and return a dict of its details."""
    try:
        drug_id_element = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
        if drug_id_element is None:
            return None
        drug_id = drug_id_element.text
        name = drug.find(f"{NS_URL}name").text if drug.find(f"{NS_URL}name") is not None else None
        drug_type = drug.get("type")
        description = drug.find(f"{NS_URL}description").text if drug.find(f"{NS_URL}description") is not None else None
        dosage_form = (
            drug.find(f"{NS_URL}dosages/{NS_URL}dosage/{NS_URL}form").text
            if drug.find(f"{NS_URL}dosages/{NS_URL}dosage/{NS_URL}form") is not None
            else None
        )
        indications = (
            drug.find(f"{NS_URL}indication").text
            if drug.find(f"{NS_URL}indication") is not None
            else None
        )
        mechanism_of_action = (
            drug.find(f"{NS_URL}mechanism-of-action").text
            if drug.find(f"{NS_URL}mechanism-of-action") is not None
            else None
        )
        food_interactions = [
            fi.text for fi in drug.findall(f".//{NS_URL}food-interactions/{NS_URL}food-interaction")
        ]
        food_interactions = "; ".join(food_interactions) if food_interactions else None

        return {
            "DrugBank_ID": drug_id,
            "Name": name,
            "Type": drug_type,
            "Description": description,
            "Dosage Form": dosage_form,
            "Indications": indications,
            "Mechanism of Action": mechanism_of_action,
            "Food Interactions": food_interactions,
        }
    except Exception as e:
        print(f"Error processing drug element: {e}")
        return None


def parse_synonyms_for_drug(drug):
    """Parse synonyms from a single <drug> element."""
    primary_id = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
    if primary_id is None:
        return None

    drug_id = primary_id.text
    synonyms = drug.findall(f"{NS_URL}synonyms/{NS_URL}synonym")
    synonym_list = [syn.text for syn in synonyms] if synonyms else []
    return {"DrugBank_ID": drug_id, "Synonyms": synonym_list}


def parse_products_for_drug(drug):
    """Parse product information from a single <drug> element."""
    primary_id = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
    if primary_id is None:
        return None

    drug_id = primary_id.text
    products = drug.findall(f"{NS_URL}products/{NS_URL}product")
    product_list = []

    for product in products:
        product_name = product.find(f"{NS_URL}name")
        manufacturer = product.find(f"{NS_URL}manufacturer")
        ndc_code = product.find(f"{NS_URL}ndc-id")
        form = product.find(f"{NS_URL}dosage-form")
        route = product.find(f"{NS_URL}route")
        strength = product.find(f"{NS_URL}strength")
        country = product.find(f"{NS_URL}country")
        agency = product.find(f"{NS_URL}approval-agency")
        product_dict = {
            "Product Name": product_name.text if product_name is not None else None,
            "Manufacturer": manufacturer.text if manufacturer is not None else None,
            "NDC Code": ndc_code.text if ndc_code is not None else None,
            "Form": form.text if form is not None else None,
            "Route": route.text if route is not None else None,
            "Strength": strength.text if strength is not None else None,
            "Country": country.text if country is not None else None,
            "Approval Agency": agency.text if agency is not None else None,
        }
        product_list.append(product_dict)

    return {"DrugBank_ID": drug_id, "Products": product_list}


def parse_polypeptide(polypeptide):
    """Helper function to extract polypeptide information."""
    source = polypeptide.get("source", "Unknown")
    ext_id = polypeptide.get("id", "Unknown")
    polypeptide_name = polypeptide.find(f"{NS_URL}name").text if polypeptide.find(f"{NS_URL}name") is not None else "Unknown"
    gene_name = polypeptide.find(f"{NS_URL}gene-name").text if polypeptide.find(f"{NS_URL}gene-name") is not None else "Unknown"
    chromosome = polypeptide.find(f"{NS_URL}chromosome-location").text if polypeptide.find(
        f"{NS_URL}chromosome-location") is not None else "Unknown"
    cellular_location = polypeptide.find(f"{NS_URL}cellular-location").text if polypeptide.find(
        f"{NS_URL}cellular-location") is not None else "Unknown"

    return source, ext_id, polypeptide_name, gene_name, chromosome, cellular_location


def parse_genatlas_id(polypeptide):
    """Helper function to extract GenAtlas ID from the external-identifier tags under polypeptide."""
    genatlas_id = "Unknown"
    external_identifiers = polypeptide.findall(f".//{NS_URL}external-identifier")

    for ext_id in external_identifiers:
        resource = ext_id.find(f"{NS_URL}resource").text if ext_id.find(f"{NS_URL}resource") is not None else ""
        if resource == "GenAtlas":
            genatlas_id = ext_id.find(f"{NS_URL}identifier").text if ext_id.find(
                f"{NS_URL}identifier") is not None else "Unknown"
            break
    return genatlas_id


def parse_targets_for_drug(drug):
    """Extract target details from a single <drug> element."""
    target_data = []
    for target in drug.findall(f".//{NS_URL}target"):
        target_id = target.find(f"{NS_URL}id")
        target_name = target.find(f"{NS_URL}name")
        if target_id is None or target_name is None:
            continue
        t_id = target_id.text if target_id.text is not None else ""
        t_name = target_name.text if target_name.text is not None else ""

        polypeptide = target.find(f"{NS_URL}polypeptide")
        if polypeptide is not None:
            source, ext_id, poly_name, gene_name, chromosome, cellular_location = parse_polypeptide(polypeptide)
            genatlas_id = parse_genatlas_id(polypeptide)
            target_data.append({
                "Target_ID": t_id,
                "Target_Name": t_name,
                "Source": source,
                "External_ID": ext_id,
                "Polypeptide_Name": poly_name,
                "Gene_Name": gene_name,
                "GenAtlas_ID": genatlas_id,
                "Chromosome": chromosome,
                "Cellular_Location": cellular_location
            })
    drug_id_elem = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
    if drug_id_elem is None or drug_id_elem.text is None:
        return None

    drug_id = drug_id_elem.text
    return {"DrugBank_ID": drug_id, "Drug": drug.find(f"{NS_URL}name").text
            if drug.find(f"{NS_URL}name") is not None else None, "Targets": target_data}


def parse_approval_status_for_drug(drug):
    """Extract approval status information from a single <drug> element."""
    groups = [group.text for group in drug.findall(f".//{NS_URL}group")]
    status = {}
    if "approved" in groups:
        status["Approved"] = 1
    if "withdrawn" in groups:
        status["Withdrawn"] = 1
    if "experimental" in groups or "investigational" in groups:
        status["Experimental/Investigational"] = 1
    if "veterinary" in groups:
        status["Veterinary"] = 1

    drug_id_elem = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
    if drug_id_elem is None or drug_id_elem.text is None:
        return None
    drug_id = drug_id_elem.text

    return {"DrugBank_ID": drug_id, "Status": status}


def parse_drug_interactions_for_drug(drug):
    """Extract drug interaction information from a single <drug> element."""
    interactions = []
    drug_name_el = drug.find(f"{NS_URL}name")
    drug_name = drug_name_el.text if drug_name_el is not None else None

    for interaction in drug.findall(f".//{NS_URL}drug-interaction"):
        interacting_drug_id = interaction.find(f"{NS_URL}drugbank-id")
        interacting_drug_name = interaction.find(f"{NS_URL}name")
        interaction_desc = interaction.find(f"{NS_URL}description")
        interactions.append({
            "Drug": drug_name,
            "Interacting_Drug_ID": interacting_drug_id.text if interacting_drug_id is not None else None,
            "Interacting_Drug": interacting_drug_name.text if interacting_drug_name is not None else None,
            "Description": interaction_desc.text if interaction_desc is not None else None,
        })

    drug_id_elem = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
    if drug_id_elem is None or drug_id_elem.text is None:
        return None
    drug_id = drug_id_elem.text

    return {"DrugBank_ID": drug_id, "Interactions": interactions}

