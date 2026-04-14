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
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents.agent_executor import AgentExecutor
from langchain.agents import create_react_agent
from langchain import hub

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


async def summarize_text(text: str) -> str:
    """Generate a brief summary of the text."""
    llm = get_llm()
    prompt = f"Summarize the following text in exactly three bullet points. Focus on the core value proposition and main topics. \n\nText: {text[:4000]} \n\nSummary:"
    summary = await llm.ainvoke(prompt)
    return summary.strip()


async def stream_ask(url: str, question: str, use_search: bool = False):
    """
    Search relevant chunks and generate a streaming answer.
    If use_search is True, it allows the agent to search the web.
    """
    llm = get_llm()
    embed_model = get_embeddings()
    query_embedding = embed_model.embed_query(question)
    
    # Get local context
    results = await similarity_search(query_embedding, url, k=4)
    context = "\n\n".join([r["content"] for r in results]) if results else "No local data found."

    if not use_search:
        # Standard RAG but streaming
        prompt = f"Use ONLY the following context to answer the question. If answer is not there, say you don't know.\nContext: {context}\nQuestion: {question}\nAnswer:"
        async for chunk in llm.astream(prompt):
            yield chunk
    else:
        # Agentic Search (Simplified for smaller models)
        search = DuckDuckGoSearchRun()
        search_results = search.run(question)
        
        prompt = f"""You are a research assistant. Use the page context and the search results to answer.
        Page Context: {context}
        Latest Web Info: {search_results}
        Question: {question}
        Answer:"""
        
        async for chunk in llm.astream(prompt):
            yield chunk


async def ingest(url: str, text: str) -> tuple[int, str]:
    """
    Chunk text, store in Supabase, and generate a summary.
    Returns (chunks_count, summary).
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
    
    # Generate summary after successful ingestion
    summary = await summarize_text(text)
    
    return len(docs), summary
