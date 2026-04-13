"""
Supabase DB Service — async-compatible client using httpx.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


async def is_url_cached(url: str) -> bool:
    """Check if a URL has already been indexed."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/url_cache",
            headers=_HEADERS,
            params={"url": f"eq.{url}", "select": "url"},
        )
        return len(resp.json()) > 0


async def cache_url(url: str, title: str = "") -> None:
    """Mark a URL as indexed."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/url_cache",
            headers={**_HEADERS, "Prefer": "resolution=merge-duplicates"},
            json={"url": url, "title": title},
        )


async def upsert_documents(docs: list[dict]) -> None:
    """
    Insert document chunks with their embeddings into Supabase.
    Each doc: {"content": str, "metadata": dict, "embedding": list[float]}
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers=_HEADERS,
            json=docs,
        )


async def similarity_search(embedding: list[float], url: str, k: int = 4) -> list[dict]:
    """Run a pgvector similarity search filtered by source URL."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_documents",
            headers=_HEADERS,
            json={
                "query_embedding": embedding,
                "match_count": k,
                "filter": {"source": url},
            },
        )
        return resp.json()
