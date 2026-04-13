"""
RAG Service — fully async LangChain pipeline.
Uses HuggingFace embeddings (local) + Supabase pgvector + Mistral-7B LLM.
"""

import os
import logging
from typing import Optional

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .db import upsert_documents, similarity_search

load_dotenv()
logger = logging.getLogger(__name__)

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

_embeddings: Optional[HuggingFaceEmbeddings] = None
_llm: Optional[HuggingFaceEndpoint] = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model (first time may take ~30s)...")
        _embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return _embeddings


def get_llm() -> HuggingFaceEndpoint:
    global _llm
    if _llm is None:
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        _llm = HuggingFaceEndpoint(
            repo_id=HF_LLM_MODEL,
            huggingfacehub_api_token=hf_token,
            temperature=0.2,
            max_new_tokens=512,
        )
    return _llm


def chunk_text(text: str, url: str) -> list[Document]:
    """Split text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=64,
    )
    chunks = splitter.split_text(text)
    return [Document(page_content=c, metadata={"source": url}) for c in chunks]


async def ingest(url: str, text: str) -> int:
    """
    Chunk text, generate embeddings locally, and store in Supabase.
    Returns the number of chunks stored.
    """
    docs = chunk_text(text, url)
    logger.info(f"Ingesting {len(docs)} chunks for {url}")

    embed_model = get_embeddings()
    texts = [d.page_content for d in docs]
    embeddings = embed_model.embed_documents(texts)

    records = [
        {
            "content": docs[i].page_content,
            "metadata": docs[i].metadata,
            "embedding": embeddings[i],
        }
        for i in range(len(docs))
    ]

    await upsert_documents(records)
    return len(docs)


async def ask(url: str, question: str) -> str:
    """
    Find relevant chunks for the given URL and generate an AI answer.
    """
    embed_model = get_embeddings()
    query_embedding = embed_model.embed_query(question)

    results = await similarity_search(query_embedding, url, k=4)

    if not results:
        return "I couldn't find any relevant information about that on this page."

    context = "\n\n".join([r["content"] for r in results])

    prompt = f"""You are a helpful assistant that answers questions about web pages.
Use ONLY the provided context to answer. If the answer isn't in the context, say "I couldn't find that on this page."

Context:
{context}

Question: {question}

Answer:"""

    llm = get_llm()
    answer = llm.invoke(prompt)
    return answer.strip()
