# drugbank/analysis.py
import pandas as pd

def count_approved_drugs(df):
    """Counts the number of approved, withdrawn, and experimental drugs."""
    return df["Type"].value_counts()

def count_pathways(df):
    """Counts pathways each drug interacts with."""
    return df.groupby("DrugBank ID")["Pathways"].count()