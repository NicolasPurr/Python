# drugbank/parsers.py
import re
import time
import pandas as pd
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# The default namespace URL.
NS_URL = "{http://www.drugbank.ca}"


def parse_drugs(root):
    """Parses DrugBank XML and extracts drug details."""
    data = []

    # Only process top-level <drug> elements
    for drug in root.findall(f"{NS_URL}drug"):
        try:
            # Get only the primary drugbank-id
            drug_id_element = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
            if drug_id_element is None:
                continue
            drug_id = drug_id_element.text if drug_id_element is not None else None

            name = drug.find(f"{NS_URL}name").text \
                if drug.find(f"{NS_URL}name") is not None else None
            drug_type = drug.get("type")
            state = drug.find(f"{NS_URL}state").text \
                if drug.find(f"{NS_URL}state") is not None else None
            description = drug.find(f"{NS_URL}description").text \
                if drug.find(f"{NS_URL}description") is not None else None
            dosage_form = drug.find(f"{NS_URL}dosages/{NS_URL}dosage/{NS_URL}form").text \
                if drug.find(f"{NS_URL}dosages/{NS_URL}dosage/{NS_URL}form") is not None else None
            indications = drug.find(f"{NS_URL}indication").text \
                if drug.find(f"{NS_URL}indication") is not None else None
            mechanism_of_action = drug.find(f"{NS_URL}mechanism-of-action").text \
                if drug.find(f"{NS_URL}mechanism-of-action") is not None else None

            food_interactions = [
                fi.text for fi in drug.findall(f".//{NS_URL}food-interactions/{NS_URL}food-interaction")
            ]
            food_interactions = "; ".join(food_interactions) \
                if food_interactions else None

            data.append({
                "DrugBank_ID": drug_id,
                "Name": name,
                "Type": drug_type,
                "State": state,
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
    for drug in root.findall(f"{NS_URL}drug"):
        primary_id = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
        synonyms = drug.findall(f"{NS_URL}synonyms/{NS_URL}synonym")

        if primary_id is not None:
            drug_id = primary_id.text
            synonym_list = [syn.text for syn in synonyms] if synonyms else []
            data.append({"DrugBank_ID": drug_id, "Synonyms": synonym_list})

    return pd.DataFrame(data)


def parse_products(root):
    """Extracts product information from XML."""
    data = []

    for drug in root.findall(f"{NS_URL}drug"):
        primary_id = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
        products = drug.findall(f"{NS_URL}products/{NS_URL}product")

        if primary_id is not None:
            drug_id = primary_id.text
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
    seen_pairs = set()  # Set to keep track of already seen drug-pathway pairs

    # Find all pathway elements anywhere in the XML
    for pathway in root.findall(f".//{NS_URL}pathway"):
        pathway_name_el = pathway.find(f"{NS_URL}name")
        if pathway_name_el is None:
            continue
        pathway_name = pathway_name_el.text

        # Look for a <drugs> element within the pathway
        drugs_element = pathway.find(f"{NS_URL}drugs")
        if drugs_element is None:
            continue

        # For each inner drug listed under <drugs>, extract its DrugBank ID from the element text.
        for inner_drug in drugs_element.findall(f"{NS_URL}drug"):
            drug_id = inner_drug.find(f"{NS_URL}drugbank-id")
            if drug_id is None:
                continue
            drug_id = drug_id.text.strip()

            # Check if this (drug_id, pathway_name) pair has been seen before
            pair = (drug_id, pathway_name)
            if pair not in seen_pairs:
                data.append([drug_id, pathway_name])
                drug_pathway_counts[drug_id] += 1
                seen_pairs.add(pair)

    df = pd.DataFrame(data, columns=["DrugBank_ID", "Pathway"])
    return df, drug_pathway_counts


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


def parse_targets(root):
    """Parses DrugBank XML and targets."""
    target_data = []
    cellular_locations = defaultdict(int)

    for drug in root.findall(f".//{NS_URL}drug"):
        drug_id_element = drug.find(f"{NS_URL}drugbank-id[@primary='true']")
        if drug_id_element is None:
            continue
        drug_id = drug_id_element.text if drug_id_element is not None else None
        drug_name = drug.find(f"{NS_URL}name").text if drug.find(f"{NS_URL}name") is not None else None
        targets = drug.findall(f".//{NS_URL}target")

        for target in targets:
            target_id = target.find(f"{NS_URL}id").text if target.find(f"{NS_URL}id") is not None else None
            target_name = target.find(f"{NS_URL}name").text if target.find(f"{NS_URL}name") is not None else None

            polypeptide = target.find(f"{NS_URL}polypeptide")
            if polypeptide is not None:
                source, ext_id, polypeptide_name, gene_name, chromosome, cellular_location = parse_polypeptide(
                    polypeptide)

                genatlas_id = parse_genatlas_id(polypeptide)

                target_data.append(
                    [drug_id, drug_name, target_id, target_name, source, ext_id, polypeptide_name, gene_name, genatlas_id,
                     chromosome, cellular_location]
                )
                cellular_locations[cellular_location] += 1

    df = pd.DataFrame(target_data,
                      columns=["DrugBank_ID", "Drug", "Target_ID", "Target_Name", "Source", "External_ID",
                               "Polypeptide_Name", "Gene_Name", "GenAtlas_ID", "Chromosome", "Cellular_Location"])

    df.sort_values(by=["DrugBank_ID"], inplace=True)

    return df, cellular_locations


def parse_approval_status(root):
    """Parses DrugBank XML and extracts information on drugs' approval statuses."""
    status_counts = defaultdict(int)
    approved_not_withdrawn = 0

    for drug in root.findall(f".//{NS_URL}drug"):
        groups = [group.text for group in drug.findall(f".//{NS_URL}group")]

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

    for drug in root.findall(f".//{NS_URL}drug"):
        drug_name = drug.find(f"{NS_URL}name").text
        interactions = drug.findall(f".//{NS_URL}drug-interaction")

        for interaction in interactions:
            interacting_drug_id = interaction.find(f"{NS_URL}drugbank-id").text
            interacting_drug_name = interaction.find(f"{NS_URL}name").text
            interaction_desc = interaction.find(f"{NS_URL}description").text

            interaction_data.append([drug_name, interacting_drug_id, interacting_drug_name, interaction_desc])

    df = pd.DataFrame(interaction_data,
                                   columns=["Drug", "Interacting_Drug_ID", "Interacting_Drug", "Description"])

    return df

def parse_genes(root):
    """Extracts drug-gene interactions and their related drug products from XML."""
    data = []

    drug_products_dict = {}

    # First, collect all drugs and their associated products into a dictionary
    for drug in root.findall(f"{NS_URL}drug"):
        drug_id = drug.find(f"{NS_URL}drugbank-id[@primary='true']").text

        products = []
        for product in drug.findall(f"{NS_URL}products/{NS_URL}product"):
            product_name = product.find(f"{NS_URL}name").text

            product_id = None
            product_id_type = None

            if product.find(f"{NS_URL}ndc-id") is not None and product.find(f"{NS_URL}ndc-id").text:
                product_id = product.find(f"{NS_URL}ndc-id").text
                product_id_type = "ndc-id"
            elif product.find(f"{NS_URL}ndc-product-code") is not None and product.find(
                    f"{NS_URL}ndc-product-code").text:
                product_id = product.find(f"{NS_URL}ndc-product-code").text
                product_id_type = "ndc-product-code"
            elif product.find(f"{NS_URL}dpd-id") is not None and product.find(f"{NS_URL}dpd-id").text:
                product_id = product.find(f"{NS_URL}dpd-id").text
                product_id_type = "dpd-id"
            elif product.find(f"{NS_URL}ema-ma-number") is not None and product.find(
                    f"{NS_URL}ema-ma-number").text:
                product_id = product.find(f"{NS_URL}ema-ma-number").text
                product_id_type = "ema-ma-number"

            if product_id:
                products.append((product_name, product_id, product_id_type))

        drug_products_dict[drug_id] = products

    for drug in root.findall(f"{NS_URL}drug"):
        drug_name = drug.find(f"{NS_URL}name").text

        # Extract interacting genes
        for target in drug.findall(f"{NS_URL}targets/{NS_URL}target"):
            gene_name_tag = target.find(f"{NS_URL}polypeptide/{NS_URL}gene-name")
            if gene_name_tag is not None:
                gene_name = gene_name_tag.text

                # Extract interacting drugs
                interactions = [interaction.find(f"{NS_URL}name").text for interaction in
                                drug.findall(f"{NS_URL}drug-interactions/{NS_URL}drug-interaction")]
                interaction_ids = [interaction.find(f"{NS_URL}drugbank-id").text for interaction in
                                   drug.findall(f"{NS_URL}drug-interactions/{NS_URL}drug-interaction")]

                # Extract products for each interaction drug
                for interaction, interaction_id in zip(interactions, interaction_ids):
                    if interaction_id in drug_products_dict:
                        products = drug_products_dict[interaction_id]
                        for product_name, product_id, product_id_type in products:
                            data.append((gene_name, drug_name, interaction, product_name, product_id, product_id_type))

    df = pd.DataFrame(data,
                      columns=["Gene", "Drug", "Interacting_Drug", "Product_Name", "Product_ID", "Product_ID_Type"])

    return df.drop_duplicates()


def get_uniprot_cards_page(query, sleep_time=2):
    """
    Opens UniProt search results for the given query, switches to the "Cards" view
    by clicking the radio button, clicks the "View results" button, and returns the rendered HTML.
    """
    options = webdriver.ChromeOptions()
    # Uncomment the next line to run headless:
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                              options=options)

    url = f"https://www.uniprot.org/uniprotkb?query={query.replace(' ', '+')}"
    driver.get(url)
    time.sleep(sleep_time)

    try:
        # Click on the "Cards" radio button.
        cards_radio = driver.find_element(
            By.XPATH,
            "//span[@role='radiogroup']//label[span[normalize-space()='Cards']]//input[@type='radio']"
        )
        if not cards_radio.is_selected():
            cards_radio.click()
    except Exception as e:
        print("Could not switch to Cards view:", e)

    try:
        # Click the "View results" button.
        view_results_btn = driver.find_element(
            By.XPATH,
            "//button[contains(@class, 'button') and contains(@class, 'primary') and @type='submit' and normalize-space()='View results']"
        )
        view_results_btn.click()
        time.sleep(sleep_time)
    except Exception as e:
        print("Could not click 'View results' button:", e)

    html = driver.page_source
    driver.quit()
    return html


def get_amino_acid_count_from_html(html, target_name):
    """
    Parse the provided HTML using BeautifulSoup to search for a UniProt card matching target_name
    and extract the amino acid count.

    Returns:
        aa_count (int): The amino acid count for the given target_name.
    """
    soup = BeautifulSoup(html, "html.parser")
    # UniProt cards are contained in <section class="card"> elements.
    cards = soup.find_all("section", class_="card")
    if not cards:
        print("No cards found on the page. The layout may have changed.")
        return None

    for card in cards:
        # Extract entry title from the header
        header = card.find("h2", class_="small")
        if not header:
            continue

        # Extract full card content (where the full protein name appears)
        card_content = card.find("div", class_="card__content")
        card_text = card_content.get_text(" ", strip=True) if card_content else ""

        if target_name.lower() not in card_text.lower():
            continue  # Skip this entry if the name is not found in card content

        # Ensure the organism is Homo sapiens
        organism_tag = card.find("a", title=re.compile("Homo sapiens", re.IGNORECASE))
        if organism_tag is None:
            continue

        # Extract amino acid count
        match = re.search(r"(\d+)\s+amino\s+acids", card_text, re.IGNORECASE)
        if match:
            aa_count = int(match.group(1))
            print(f"Found target '{target_name}' with {aa_count} amino acids.")
            return aa_count

    print(f"No matching UniProt entry found for target '{target_name}'.")
    return None


def get_amino_acid_count_for_target(target_name):
    """
    Combines the functionality: queries UniProt for the target name, clicks the "Cards" radio button,
    then clicks the "View results" button, and returns the amino acid count.

    Returns:
        aa_count (int): The amino acid count for the given target_name.
    """
    html = get_uniprot_cards_page(target_name)
    aa_count = get_amino_acid_count_from_html(html, target_name)
    return aa_count


def get_target_amino_acid_count_for_drug(drug_id, targets):
    """
    Gets amino acid count for each target for a given drug and records in a data frame.

    Returns:
        DataFrame["DrugBank_ID", "Target_Name", "Amino_Acid_count"]
    """
    if targets.empty:
        print(f"Cannot get amino acid count for no targets!")
        return None

    print(f"Finding amino acid counts for targets for DrugBank_ID {drug_id}:")
    data = []
    for target_name in targets.loc[targets["DrugBank_ID"] == drug_id, "Target_Name"].values:
        aa_count = get_amino_acid_count_for_target(target_name)
        data.append((drug_id, target_name, aa_count))

    return pd.DataFrame(data, columns=["DrugBank_ID", "Target_Name", "Amino_Acid_Count"])
