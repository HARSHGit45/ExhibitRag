from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


load_dotenv()

app = FastAPI(
    title="Science Park RAG Chatbot",
    version="2.0"
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi"
}


prompt = ChatPromptTemplate.from_template("""
You are a science park assistant assigned ONLY to the {exhibit} exhibit.

Rules:
- Answer questions strictly related to this exhibit.
- If the question is outside this exhibit, say:
  "I can only explain things related to this exhibit."
- Respond ONLY in {language}.
- Use simple, kid-friendly explanations.

Context:
{context}

Question:
{input}

Answer:
""")


class ChatRequest(BaseModel):
    exhibit_id: str
    question: str
    language: str   # en  for english/ hi for hindi / mr for marathi


def format_docs(docs):
    """Format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


@app.post("/chat")
def chat(req: ChatRequest):
    
    language_name = LANGUAGE_MAP.get(req.language, "English")
    
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 4,
            "filter": {"exhibit_id": req.exhibit_id}
        }
    )
    
    rag_chain = (
        {
            "context": retriever | format_docs,
            "input": RunnablePassthrough(),
            "exhibit": lambda _: req.exhibit_id.replace("_", " ").title(),
            "language": lambda _: language_name
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    

    answer = rag_chain.invoke(req.question)
    
    return {
        "exhibit": req.exhibit_id,
        "language": language_name,
        "question": req.question,
        "answer": answer
    }


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Science Park RAG Chatbot is running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)