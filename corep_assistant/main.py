import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict


app = FastAPI(
    title="COREP RAG Assistant",
    version="1.0"
)

class QueryRequest(BaseModel):
    scenario: str

class Field(BaseModel):
    field_code: str
    description: str
    value: float
    rule_reference: str

class QueryResponse(BaseModel):
    llm_output: Dict
    validation_flags: List[str]
    audit_log: List[Dict]
    
    
    
    
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "corep_index_genai")

    
    
    
    
    
import os
import json
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate


PROMPT = """
            You are a regulatory reporting assistant.

            Use ONLY the retrieved rule text to answer.

            If required data is missing, populate "missing_data".
            If rule text is insufficient, set value to null.
            Do NOT guess.

            Scenario:
            {scenario}

            COREP Template: Own Funds

            Return a SINGLE valid JSON object.
            No explanations.
            No markdown.
            No backticks.
            No text before or after JSON.

            JSON must follow this example schema exactly:
            {schema}

            Retrieved Rules:
            {context}

            Output MUST begin with '{{' and end with '}}'.
            """
            

COREP_SCHEMA = {
    "template": "Own Funds",
    "fields": [
        {
            "field_code": "CET1_001",
            "description": "Common Equity Tier 1 Capital",
            "value": 0.0,
            "rule_reference": "CRR Art. 26"
        }
    ],
    "missing_data": [],
    "validation_flags": []
}




load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Load once
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY,
    temperature=0
)

prompt = PromptTemplate.from_template(PROMPT)

def run_query(scenario: str):
    docs = db.similarity_search(scenario, k=4)
    
    if not docs:
        return {
            "template": "Own Funds",
            "fields": [],
            "missing_data": [
                "No COREP rule text found defining CET1 composition"
            ],
            "validation_flags": []
        }, []

    context = "\n\n".join(d.page_content for d in docs)

    final_prompt = prompt.format(
        scenario=scenario,
        context=context,
        schema=json.dumps(COREP_SCHEMA, indent=2)
    )

    response = llm.invoke(final_prompt)
    
    import re

    raw = response.content

    print("\n========== RAW LLM OUTPUT ==========\n", raw, flush=True)
    print("\n===================================\n", flush=True)

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    parsed = json.loads(match.group())


    return parsed, docs
    
    
    
    
    
    




def validate(fields):

    flags = []

    cet1 = next((f["value"] for f in fields if "CET1" in f["description"]), 0)
    at1 = next((f["value"] for f in fields if "AT1" in f["description"]), 0)
    t2 = next((f["value"] for f in fields if "Tier2" in f["description"]), 0)

    total = cet1 + at1 + t2

    reported_total = next(
        (f["value"] for f in fields if "Total Capital" in f["description"]),
        None
    )

    if reported_total and reported_total != total:
        flags.append("Total capital mismatch")

    return flags






    
    
    
    
    
    
    

@app.post("/query", response_model=QueryResponse)
def query_corep(req: QueryRequest):
    try:
        output, docs = run_query(req.scenario)

        data = output if isinstance(output, dict) else None
        if data is None:
            raise ValueError("LLM did not return valid JSON")

        flags = validate(data.get("fields", []))

        return {
            "llm_output": data,
            "validation_flags": flags,
            "audit_log": [d.metadata for d in docs]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
