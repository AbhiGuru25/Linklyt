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
    nlp_data: Optional[dict] = None
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
async def analyze(request: AnalyzeRequest):
    # Support multiple URLs separated by commas
    urls = [u.strip() for u in request.url.split(',') if u.strip()]
    if not urls:
        raise HTTPException(status_code=400, detail="No valid URLs provided.")
    
    # Process all URLs (in parallel for speed)
    async def process_single_url(u):
        text, title = await scrape_url(u)
        if text:
            chunks, summary, nlp = await ingest(u, text)
            # Truncate title for DB stability
            safe_title = (title or u)[:200]
            await cache_url(u, safe_title)
            return {"url": u, "chunks": chunks, "text": text}
        return None

    results = await asyncio.gather(*[process_single_url(u) for u in urls])
    results = [r for r in results if r]

    if not results:
        raise HTTPException(status_code=422, detail="Could not extract text from any provided URLs.")

    # Combine data for synthesis
    total_chunks = sum(r['chunks'] for r in results)
    combined_text = "\n\n".join([f"SOURCE: {r['url']}\n{r['text'][:2000]}" for r in results])
    
    # Generate a synthesized summary and NLP data across all sources
    summary = await summarize_text(combined_text)
    nlp_data = await extract_nlp_insights(combined_text)
    
    return AnalyzeResponse(
        url=", ".join([r['url'] for r in results]),
        chunks_indexed=total_chunks,
        cached=False,
        summary=summary,
        nlp_data=nlp_data,
        message=f"Success! Synthesized intelligence from {len(results)} sources ({total_chunks} total chunks).",
    )


@app.post("/ask")
async def ask_question(req: AskRequest):
    url_str = str(req.url)

    if not await is_url_cached(url_str):
        raise HTTPException(status_code=404, detail="URL not yet indexed.")

    async def event_generator():
        from services.rag import stream_ask
        got_tokens = False
        try:
            async for token in stream_ask(url_str, req.question, req.use_search):
                if token:
                    got_tokens = True
                    yield f"data: {json.dumps({'token': token})}\n\n"
            if not got_tokens:
                yield f"data: {json.dumps({'token': 'The AI returned an empty response. Please try again.'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'token': f'Error: {str(e)}'})}\n\n"

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


@app.get("/history")
async def history():
    from services.db import get_url_history
    return await get_url_history()


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=True,
    )
