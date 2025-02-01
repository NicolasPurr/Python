from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .parsers import parse_pathways

app = FastAPI()

with open("data/drugbank_partial.xml", "r", encoding="utf-8") as file:
    xml_content = file.read()

pathways, drug_pathway_counts = parse_pathways(xml_content)

class DrugRequest(BaseModel):
    drug_id: str

@app.post("/get_pathway_count/")
def get_pathway_count(request: DrugRequest):
    drug_id = request.drug_id.strip()
    if drug_id not in pathways["DrugBank_ID"].values:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"drug_id": drug_id, "pathway_count": drug_pathway_counts[drug_id]}
