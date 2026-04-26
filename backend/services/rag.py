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


from .db import upsert_documents, similarity_search

load_dotenv()
logger = logging.getLogger(__name__)

# Model IDs
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_LLM_MODEL = "microsoft/Phi-3-mini-4k-instruct"

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


from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# --- LangGraph State Definition ---
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
    """Combine local + web info into a final answer."""
    logger.info("✍️ LangGraph: Synthesizing final answer...")
    llm = get_llm()
    prompt = f"""You are a Linklyt Research Assistant.
    PAGE CONTEXT: {state['context']}
    LIVE WEB SEARCH: {state['web_data']}
    USER QUESTION: {state['question']}
    
    Synthesize a comprehensive, professional answer using both the page context and web info.
    ANSWER:"""
    
    # We yield the full answer here as a string for the state
    answer = await llm.ainvoke(prompt)
    return {"answer": answer}

# --- Build the Graph ---
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
    """
    Execute the LangGraph research workflow.
    Since HuggingFaceEndpoint.astream works on strings, we yield tokens!
    """
    initial_state = {
        "url": url,
        "question": question,
        "context": "",
        "web_data": "",
        "answer": ""
    }
    
    # Run the graph
    try:
        logger.info(f"🚀 Graph: Starting research for {url}")
        final_output = await _research_app.ainvoke(initial_state)
        logger.info("✅ Graph: Success")
        answer = final_output.get("answer", "No answer generated.")
        
        # Ensure answer is a plain string
        if hasattr(answer, 'text'):
            answer = answer.text
        elif hasattr(answer, 'content'):
            answer = answer.content
        yield str(answer)
    except StopIteration:
        logger.error("🔥 Graph: Caught StopIteration! Converting to string.")
        yield "Internal Error: Research model stopped prematurely."
    except Exception as e:
        logger.error(f"🔥 Graph: Error: {str(e)}", exc_info=True)
        yield f"Error in research workflow: {str(e)}"


async def stream_ask(url: str, question: str, use_search: bool = False):
    """
    Search relevant chunks and generate a streaming answer.
    """
    if use_search:
        async for chunk in stream_search_answer(url, question):
            yield chunk
        return

    # Standard RAG: use ainvoke instead of astream to avoid HuggingFace StopIteration bug
    llm = get_llm()
    embed_model = get_embeddings()
    
    embeddings = await embed_with_retry(embed_model, [question])
    results = await similarity_search(embeddings[0], url, k=4)
    context = "\n\n".join([r["content"] for r in results]) if results else "No local data found."

    prompt = f"Use ONLY the following context to answer. If answer is not there, say you don't know.\nContext: {context}\nQuestion: {question}\nAnswer:"
    
    # ainvoke returns the full string — avoids RuntimeError: coroutine raised StopIteration in _astream
    try:
        logger.info(f"🤖 LLM: Invoking {HF_LLM_MODEL}...")
        response = await llm.ainvoke(prompt)
        logger.info("✅ LLM: Success")
        
        if hasattr(response, 'text'):
            text = response.text
        elif hasattr(response, 'content'):
            text = response.content
        else:
            text = str(response)
        
        if not text:
            yield "The AI returned an empty response."
        else:
            yield text
    except StopIteration:
        logger.error("🔥 LLM: Caught StopIteration from ainvoke!")
        yield "The AI model encountered a technical error. Please try again."
    except Exception as e:
        logger.error(f"🔥 LLM: Error during ainvoke: {str(e)}", exc_info=True)
        yield f"AI Error: {str(e)}"


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
