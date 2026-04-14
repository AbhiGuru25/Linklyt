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
from services.rag import ingest
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
    
    # Check for specific error types to provide cleaner messages
    detail = "Internal Server Error"
    if "503" in str(exc) or "loading" in str(exc).lower():
        detail = "AI model is warming up. Please try again in 30 seconds."
    elif "supabase" in str(exc).lower() or "httpx" in str(exc).lower():
        detail = "Database connection issue. Please check your Supabase settings."
    
    return JSONResponse(
        status_code=500,
        content={"detail": detail, "message": str(exc)},
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


from fastapi.responses import StreamingResponse
import json
from typing import Optional

class AnalyzeResponse(BaseModel):
    url: str
    chunks_indexed: int
    cached: bool
    summary: Optional[str] = None
    message: str


class AskRequest(BaseModel):
    url: HttpUrl
    question: str
    use_search: bool = False


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Linklyt AI API"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    url_str = str(req.url)

    if not req.force_refresh and await is_url_cached(url_str):
        return AnalyzeResponse(
            url=url_str,
            chunks_indexed=0,
            cached=True,
            message="URL already indexed. Ready to answer questions.",
        )

    text = await scrape_url(url_str)
    if not text:
        raise HTTPException(status_code=422, detail="Could not extract text.")

    chunks, summary = await ingest(url_str, text)
    await cache_url(url_str)

    return AnalyzeResponse(
        url=url_str,
        chunks_indexed=chunks,
        cached=False,
        summary=summary,
        message=f"Success! Indexed {chunks} chunks and generated a summary.",
    )


@app.post("/ask")
async def ask_question(req: AskRequest):
    url_str = str(req.url)

    if not await is_url_cached(url_str):
        raise HTTPException(status_code=404, detail="URL not yet indexed.")

    async def event_generator():
        from services.rag import stream_ask
        async for token in stream_ask(url_str, req.question, req.use_search):
            yield f"data: {json.dumps({'token': token})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class AutomateRequest(BaseModel):
    url: str
    summary: str
    answer: str
    webhook_url: str


@app.post("/automate")
async def automate(req: AutomateRequest):
    from services.automation import send_to_n8n
    result = await send_to_n8n({
        "url": req.url,
        "summary": req.summary,
        "ai_answer": req.answer
    }, req.webhook_url)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True,
    )
