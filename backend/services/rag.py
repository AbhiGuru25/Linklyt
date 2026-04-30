"""
RAG Service — fully async pipeline.
Uses HuggingFace embeddings + Supabase pgvector + Groq (Llama-3.1-8B) LLM.
Groq is free, blazing fast, and 100% stable.
"""

import os
import logging
import asyncio
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.tools import DuckDuckGoSearchRun

from .db import upsert_documents, similarity_search

logger = logging.getLogger(__name__)

# --- Model Configuration ---
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant"  # Free, fast, smart

_embeddings: Optional[HuggingFaceEndpointEmbeddings] = None
_groq_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    """Get or create the Groq client."""
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def call_groq(system_prompt: str, user_prompt: str) -> str:
    """
    Calls the Groq API for LLM inference.
    Groq is FREE, has no routing issues, and is extremely fast.
    """
    client = get_groq_client()
    logger.info(f"🚀 Groq API: Calling {GROQ_MODEL}...")
    
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=512,
    )
    
    result = completion.choices[0].message.content
    logger.info("✅ Groq API: Success")
    return result.strip()


async def embed_with_retry(
    embed_model: HuggingFaceEndpointEmbeddings,
    texts: list[str],
    max_retries: int = 5
) -> list[list[float]]:
    """Handles HuggingFace API cold starts by retrying with backoff."""
    for attempt in range(max_retries):
        try:
            return embed_model.embed_documents(texts)
        except Exception as e:
            err_msg = str(e).lower()
            if ("loading" in err_msg or "503" in err_msg) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                logger.info(f"HuggingFace embeddings loading. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
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


def chunk_text(text: str, url: str) -> list[Document]:
    """Split text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=64,
    )
    chunks = splitter.split_text(text)
    return [Document(page_content=c, metadata={"source": url}) for c in chunks]


async def extract_nlp_insights(text: str) -> dict:
    """
    Advanced NLP Nerve Center:
    Extracts Sentiment, Entities, and Keywords in one shot using Groq.
    """
    system = "You are an NLP Specialist. Analyze the provided text and return a JSON object with: 'sentiment' (one word), 'entities' (list of people/orgs), and 'keywords' (top 5 topics)."
    user = f"Analyze this text and return ONLY JSON:\n\n{text[:3000]}"
    
    try:
        result = await asyncio.to_thread(call_groq, system, user)
        # Attempt to parse JSON from the LLM response
        import json
        import re
        # Clean up common LLM markdown formatting if present
        cleaned = re.sub(r'```json\n|\n```', '', result)
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"NLP Extraction failed: {e}")
        return {"sentiment": "Neutral", "entities": [], "keywords": []}


async def summarize_text(text: str) -> str:
    """Generate a brief summary of the text using Groq."""
    system = "You are a concise summarizer. Summarize text in exactly three bullet points. Use professional language."
    user = f"Summarize this text:\n\n{text[:4000]}"
    result = await asyncio.to_thread(call_groq, system, user)
    return result


# --- LangGraph Pipeline ---
from typing import TypedDict
from langgraph.graph import StateGraph, END


class ResearchState(TypedDict):
    url: str
    question: str
    context: str
    web_data: str
    answer: str


async def local_search_node(state: ResearchState):
    """Retrieve indexed chunks from Supabase."""
    logger.info("🔍 LangGraph: Checking local database...")
    embed_model = get_embeddings()
    embeddings = await embed_with_retry(embed_model, [state["question"]])
    results = await similarity_search(embeddings[0], state["url"], k=4)
    context = "\n\n".join([r["content"] for r in results]) if results else "No local info."
    return {"context": context}


async def web_search_node(state: ResearchState):
    """Retrieve live info from DuckDuckGo."""
    logger.info(f"🌐 LangGraph: Searching web for '{state['question']}'...")
    search = DuckDuckGoSearchRun()
    try:
        results = search.run(state["question"])
    except Exception as e:
        logger.error(f"Web search error: {e}")
        results = "Web search unavailable."
    return {"web_data": results}


async def synthesis_node(state: ResearchState):
    """Combine local + web info into a final answer using Groq."""
    logger.info("✍️ LangGraph: Synthesizing final answer...")
    system = "You are a Linklyt Research Assistant. Synthesize a professional, comprehensive answer using the provided context and web search results."
    user = (
        f"PAGE CONTEXT:\n{state['context']}\n\n"
        f"LIVE WEB SEARCH:\n{state['web_data']}\n\n"
        f"USER QUESTION: {state['question']}"
    )
    answer = await asyncio.to_thread(call_groq, system, user)
    return {"answer": answer}


def create_research_graph():
    workflow = StateGraph(ResearchState)
    workflow.add_node("local_search", local_search_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("synthesis", synthesis_node)

    workflow.set_entry_point("local_search")
    workflow.add_edge("local_search", "web_search")
    workflow.add_edge("web_search", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile()


_research_app = create_research_graph()


async def stream_search_answer(url: str, question: str):
    """Execute the LangGraph research workflow."""
    initial_state = {
        "url": url,
        "question": question,
        "context": "",
        "web_data": "",
        "answer": ""
    }

    try:
        logger.info(f"🚀 Graph: Starting research for {url}")
        final_output = await _research_app.ainvoke(initial_state)
        logger.info("✅ Graph: Success")
        answer = final_output.get("answer", "No answer generated.")
        yield str(answer)
    except Exception as e:
        logger.error(f"🔥 Graph Error: {str(e)}", exc_info=True)
        yield f"Error in research workflow: {str(e)}"


async def stream_ask(url: str, question: str, use_search: bool = False):
    """
    Search relevant chunks and generate an answer using Groq.
    """
    try:
        if use_search:
            async for chunk in stream_search_answer(url, question):
                yield chunk
            return

        # Standard RAG: embed question → similarity search → Groq answer
        embed_model = get_embeddings()

        embeddings = await embed_with_retry(embed_model, [question])
        results = await similarity_search(embeddings[0], url, k=4)
        context = "\n\n".join([r["content"] for r in results]) if results else "No local data found."

        system = "You are a helpful assistant. Use ONLY the provided context to answer. If the answer is not in the context, say 'I don't have enough information about that from this page.'"
        user = f"Context:\n{context}\n\nQuestion: {question}"

        logger.info(f"🤖 Groq RAG: Invoking {GROQ_MODEL}...")
        response = await asyncio.to_thread(call_groq, system, user)
        logger.info("✅ Groq RAG: Success")

        yield response if response.strip() else "The AI returned an empty response."

    except Exception as e:
        logger.error(f"🔥 Critical RAG Error: {str(e)}", exc_info=True)
        yield f"System Stability Error: {str(e)}. Please try again."


async def ingest(url: str, text: str) -> tuple[int, str]:
    """
    Chunk text, store in Supabase, and generate a summary.
    Returns (chunks_count, summary).
    """
    docs = chunk_text(text, url)
    logger.info(f"Ingesting {len(docs)} chunks for {url}")

    embed_model = get_embeddings()
    texts = [d.page_content for d in docs]

    # Batch embeds to avoid payload limits
    batch_size = 20
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i: i + batch_size]
        logger.info(f"Embedding batch {i // batch_size + 1} (Size: {len(batch_texts)})...")
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
    
    # Generate summary and NLP insights
    summary = await summarize_text(text)
    nlp_data = await extract_nlp_insights(text)
    
    return len(docs), summary, nlp_data
