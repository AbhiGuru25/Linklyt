"""
Linklyt AI — FastAPI Backend
Endpoints:
  POST /analyze  — Scrape + index a URL
  POST /ask      — Query an indexed URL
  GET  /health   — Health check
"""

import logging
import os
import sys
import asyncio

# Set ProactorEventLoop on Windows for Playwright/Subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

from services.scraper import scrape_url
from services.rag import ingest, ask
from services.db import is_url_cached, cache_url

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from starlette.responses import JSONResponse

app = FastAPI(
    title="Linklyt AI API",
    description="RAG-powered URL intelligence — scrape, embed, and chat with any web page.",
    version="1.0.0",
)

# ─── CORS — allow everything in development to eliminate friction ──────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "message": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


# ─── Schemas ─────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    force_refresh: bool = False


class AnalyzeResponse(BaseModel):
    url: str
    chunks_indexed: int
    cached: bool
    message: str


class AskRequest(BaseModel):
    url: HttpUrl
    question: str


class AskResponse(BaseModel):
    url: str
    question: str
    answer: str


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Linklyt AI API"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    url_str = str(req.url)

    # Check cache — skip re-scraping unless force_refresh is requested
    if not req.force_refresh and await is_url_cached(url_str):
        return AnalyzeResponse(
            url=url_str,
            chunks_indexed=0,
            cached=True,
            message="URL already indexed. Ready to answer questions.",
        )

    # Scrape the page
    logger.info(f"Scraping: {url_str}")
    text = await scrape_url(url_str)
    if not text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from this URL. Try a different page.",
        )

    # Chunk, embed, and store
    chunks = await ingest(url_str, text)

    # Cache the URL so we don't re-scrape it
    await cache_url(url_str)

    return AnalyzeResponse(
        url=url_str,
        chunks_indexed=chunks,
        cached=False,
        message=f"Successfully indexed {chunks} chunks. Ready to answer questions.",
    )


@app.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    url_str = str(req.url)

    if not await is_url_cached(url_str):
        raise HTTPException(
            status_code=404,
            detail="URL not yet indexed. Please click Analyse first.",
        )

    answer = await ask(url_str, req.question)

    return AskResponse(
        url=url_str,
        question=req.question,
        answer=answer,
    )


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True,
    )
