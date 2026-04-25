"""
RAG Service — fully async LangChain pipeline.
Uses HuggingFace embeddings (local) + Supabase pgvector + Mistral-7B LLM.
"""

import os
import logging
import asyncio
from typing import Optional

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from .db import upsert_documents, similarity_search

load_dotenv()
logger = logging.getLogger(__name__)

# Model IDs
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

_embeddings: Optional[HuggingFaceEndpointEmbeddings] = None
_llm: Optional[HuggingFaceEndpoint] = None


async def embed_with_retry(embed_model: HuggingFaceEndpointEmbeddings, texts: list[str], max_retries: int = 5) -> list[list[float]]:
    """Handles HuggingFace API cold starts by retrying with backoff."""
    for attempt in range(max_retries):
        try:
            # Note: embed_documents is synchronous in the current LangChain implementation
            return embed_model.embed_documents(texts)
        except Exception as e:
            err_msg = str(e).lower()
            if ("loading" in err_msg or "503" in err_msg) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                logger.info(f"HuggingFace model is loading. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Embedding failed after {attempt+1} attempts: {str(e)}")
                raise


def get_embeddings() -> HuggingFaceEndpointEmbeddings:
    global _embeddings
    if _embeddings is None:
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        logger.info("Initializing Cloud Embeddings (HuggingFace API mode)...")
        _embeddings = HuggingFaceEndpointEmbeddings(
            model=EMBED_MODEL,
            huggingfacehub_api_token=hf_token
        )
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
    
    # Use retry for query embedding as well
    embeddings = await embed_with_retry(embed_model, [question])
    query_embedding = embeddings[0]
    
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
    
    # --- Batching Logic: Avoid Cloud API payload limits ---
    batch_size = 20
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        logger.info(f"Embedding batch {i//batch_size + 1} (Size: {len(batch_texts)})...")
        batch_embeddings = await embed_with_retry(embed_model, batch_texts)
        all_embeddings.extend(batch_embeddings)

    records = [
        {
            "content": docs[i].page_content,
            "metadata": docs[i].metadata,
            "embedding": all_embeddings[i],
        }
        for i in range(len(docs))
    ]

    await upsert_documents(records)
    
    # Generate summary after successful ingestion
    summary = await summarize_text(text)
    
    return len(docs), summary
