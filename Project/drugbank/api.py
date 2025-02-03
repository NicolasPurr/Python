from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .parsers import parse_pathways
from lxml import etree

app = FastAPI()

relative_file_path = "data/drugbank_partial.xml"

try:
    # Parse the input XML.
    tree = etree.parse(relative_file_path)
    root = tree.getroot()
except etree.ParseError as e:
    print(f"Error parsing XML: {e}")
    exit(1)

# Get pathways and pathway counts
pathways, drug_pathway_counts = parse_pathways(root)

class DrugRequest(BaseModel):
    drug_id: str

@app.post("/get_pathway_count/")
def get_pathway_count(request: DrugRequest):
    drug_id = request.drug_id.strip()
    if drug_id not in pathways["DrugBank_ID"].values:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"drug_id": drug_id, "pathway_count": drug_pathway_counts[drug_id]}
