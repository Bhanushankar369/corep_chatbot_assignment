from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from dotenv import load_dotenv
load_dotenv()

docs = []
for file in ["data/corep_rules.pdf", "data/pra_rule_book.pdf"]:
    loader = PyPDFLoader(file)
    docs.extend(loader.load())
    

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=300
)

chunks = splitter.split_documents(docs)

embeddings = HuggingFaceBgeEmbeddings(
    model_name = "all-MiniLM-L6-v2"
)

db = FAISS.from_documents(
    chunks,
    embeddings
)

db.save_local("corep_index_genai")