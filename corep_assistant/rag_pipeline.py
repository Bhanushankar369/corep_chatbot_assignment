from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "corep_index_genai")


from corep_assistant.prompts import PROMPT
from corep_assistant.schema import COREP_SCHEMA

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)

db = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

prompt = PromptTemplate.from_template(PROMPT)

def run_query(scenario):
    docs = db.similarity_search(scenario, k=4)
    
    context = "\n\n".join([d.page_content for d in docs])
    
    final_prompt = prompt.format(
        scenario=scenario,
        context=context,
        schema = COREP_SCHEMA
    )
    
    response = llm.invoke(final_prompt)
    
    return response.content, docs