# drugbank/simulator.py
import random
import pandas as pd
import lxml.etree as ET


# Function to parse the XML and extract drug data into separate DataFrames
def parse_drugbank_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {"db": "http://www.drugbank.ca"}

    drugs_data, groups_data, synonyms_data, products_data, categories_data = [], [], [], [], []
    references_data, synthesis_data, indications_data, pharmacodynamics_data = [], [], [], []
    prices_data, manufacturers_data, packagers_data = [], [], []
    affected_organisms_data, food_interactions_data, drug_interactions_data = [], [], []
    atc_codes_data, patents_data, sequences_data, experimental_properties_data = [], [], [], []
    external_identifiers_data, external_links_data, pathways_data, reactions_data = [], [], [], []

    for drug in root.findall("db:drug", ns):
        drug_info = {
            "id": [id_tag.text for id_tag in drug.findall("db:drugbank-id", ns)],
            "name": drug.find("db:name", ns).text if drug.find("db:name", ns) is not None else "Unknown",
            "cas": drug.find("db:cas-number", ns).text if drug.find("db:cas-number", ns) is not None else "Unknown",
            "state": drug.find("db:state", ns).text if drug.find("db:state", ns) is not None else "Unknown",
        }
        drugs_data.append(drug_info)

        for atc_code in drug.findall("db:atc-codes/db:atc-code", ns):
            code = atc_code.get("code")
            for level in atc_code.findall("db:level", ns):
                atc_codes_data.append({"drug_id": drug_info["id"][0], "code": code, "level_code": level.get("code"),
                                       "level_name": level.text})

        for patent in drug.findall("db:patents/db:patent", ns):
            patents_data.append({
                "drug_id": drug_info["id"][0],
                "number": patent.find("db:number", ns).text,
                "country": patent.find("db:country", ns).text,
                "approved": patent.find("db:approved", ns).text,
                "expires": patent.find("db:expires", ns).text,
                "pediatric_extension": patent.find("db:pediatric-extension", ns).text,
            })

        for sequence in drug.findall("db:sequences/db:sequence", ns):
            sequences_data.append({"drug_id": drug_info["id"][0], "sequence": sequence.text})

        for property in drug.findall("db:experimental-properties/db:property", ns):
            experimental_properties_data.append({
                "drug_id": drug_info["id"][0],
                "kind": property.find("db:kind", ns).text,
                "value": property.find("db:value", ns).text,
            })

        for identifier in drug.findall("db:external-identifiers/db:external-identifier", ns):
            external_identifiers_data.append({
                "drug_id": drug_info["id"][0],
                "resource": identifier.find("db:resource", ns).text,
                "identifier": identifier.find("db:identifier", ns).text,
            })

        for link in drug.findall("db:external-links/db:external-link", ns):
            external_links_data.append({
                "drug_id": drug_info["id"][0],
                "resource": link.find("db:resource", ns).text,
                "url": link.find("db:url", ns).text,
            })

        for pathway in drug.findall("db:pathways/db:pathway", ns):
            pathways_data.append({
                "drug_id": drug_info["id"][0],
                "smpdb_id": pathway.find("db:smpdb-id", ns).text,
                "name": pathway.find("db:name", ns).text,
                "category": pathway.find("db:category", ns).text,
            })

        for reaction in drug.findall("db:reactions/db:reaction", ns):
            reactions_data.append({
                "drug_id": drug_info["id"][0],
                "sequence": reaction.find("db:sequence", ns).text,
                "left_element": reaction.find("db:left-element/db:name", ns).text,
                "right_element": reaction.find("db:right-element/db:name", ns).text,
            })

    return (
        pd.DataFrame(drugs_data),
        pd.DataFrame(groups_data),
        pd.DataFrame(synonyms_data),
        pd.DataFrame(products_data),
        pd.DataFrame(categories_data),
        pd.DataFrame(references_data),
        pd.DataFrame(synthesis_data),
        pd.DataFrame(indications_data),
        pd.DataFrame(pharmacodynamics_data),
        pd.DataFrame(prices_data),
        pd.DataFrame(manufacturers_data),
        pd.DataFrame(packagers_data),
        pd.DataFrame(affected_organisms_data),
        pd.DataFrame(food_interactions_data),
        pd.DataFrame(drug_interactions_data),
        pd.DataFrame(atc_codes_data),
        pd.DataFrame(patents_data),
        pd.DataFrame(sequences_data),
        pd.DataFrame(experimental_properties_data),
        pd.DataFrame(external_identifiers_data),
        pd.DataFrame(external_links_data),
        pd.DataFrame(pathways_data),
        pd.DataFrame(reactions_data),
    )


# Function to generate a large XML file with 20,000 drug entries
def generate_random_drug_xml(dataframes, output_file):
    drugs_df, groups_df, synonyms_df, products_df, categories_df, references_df, synthesis_df, indications_df, \
        pharmacodynamics_df, prices_df, manufacturers_df, packagers_df, affected_organisms_df, food_interactions_df, \
        drug_interactions_df, atc_codes_df, patents_df, sequences_df, experimental_properties_df, external_identifiers_df, \
        external_links_df, pathways_df, reactions_df = dataframes

    root = ET.Element("drugbank", xmlns="http://www.drugbank.ca")
    drug = ET.SubElement(root, "drug", type="biotech")

    drug_info = drugs_df.sample(n=1).iloc[0]
    ET.SubElement(drug, "drugbank-id", primary="true").text = drug_info["id"][0]
    ET.SubElement(drug, "name").text = drug_info["name"]
    ET.SubElement(drug, "cas-number").text = drug_info["cas"]
    ET.SubElement(drug, "state").text = drug_info["state"]

    if not atc_codes_df.empty:
        atc_codes = ET.SubElement(drug, "atc-codes")
        atc_sample = atc_codes_df.sample(n=1)
        atc_code = ET.SubElement(atc_codes, "atc-code", code=atc_sample.iloc[0]["code"])
        ET.SubElement(atc_code, "level", code=atc_sample.iloc[0]["level_code"]).text = atc_sample.iloc[0]["level_name"]

    if not patents_df.empty:
        patents = ET.SubElement(drug, "patents")
        patent_sample = patents_df.sample(n=1).iloc[0]
        patent = ET.SubElement(patents, "patent")
        ET.SubElement(patent, "number").text = patent_sample["number"]
        ET.SubElement(patent, "country").text = patent_sample["country"]
        ET.SubElement(patent, "approved").text = patent_sample["approved"]
        ET.SubElement(patent, "expires").text = patent_sample["expires"]

    if not food_interactions_df.empty:
        food_interactions = ET.SubElement(drug, "food-interactions")
        ET.SubElement(food_interactions, "food-interaction").text = food_interactions_df.sample(n=1).iloc[0][
            "interaction"]

    if not drug_interactions_df.empty:
        drug_interactions = ET.SubElement(drug, "drug-interactions")
        interaction_sample = drug_interactions_df.sample(n=1).iloc[0]
        interaction = ET.SubElement(drug_interactions, "drug-interaction")
        ET.SubElement(interaction, "drugbank-id").text = interaction_sample["interacting_drug_id"]
        ET.SubElement(interaction, "name").text = interaction_sample["interacting_drug_name"]
        ET.SubElement(interaction, "description").text = interaction_sample["description"]

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Random drug XML generated in {output_file}")

