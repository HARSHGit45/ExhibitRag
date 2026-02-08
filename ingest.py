from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os


DATA_DIR = "data"
DB_DIR = "faiss_index"


EXHIBITS = {
    "solar_system": "solarsystem.txt",
    "steam": "steam.txt",
    "pendulam": "pendulam.txt"
}

documents = []


for exhibit_id, file_name in EXHIBITS.items():
    file_path = os.path.join(DATA_DIR, file_name)
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()

    for doc in docs:
        doc.metadata = {
            "exhibit_id": exhibit_id
        }
        documents.append(doc)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = text_splitter.split_documents(documents)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local(DB_DIR)

print("All exhibits ingested into single vector database")
