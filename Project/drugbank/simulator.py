# drugbank/simulator.py
import pandas as pd
import random


def generate_fake_drugs(existing_df, num_new=19900):
    """Generates fake drugs using existing data as a base."""
    new_data = []
    for i in range(num_new):
        fake_id = f"DB{100000 + i}"
        row = existing_df.sample().iloc[0]
        new_data.append({**row, "DrugBank ID": fake_id})

    return pd.concat([existing_df, pd.DataFrame(new_data)])


def save_generated_data():
    with open("data/drugbank_partial.xml", "r", encoding="utf-8") as file:
        xml_content = file.read()
        df = parse_drugs(xml_content)

    fake_df = generate_fake_drugs(df)
    fake_df.to_csv("data/drugbank_partial_and_generated.csv", index=False)
