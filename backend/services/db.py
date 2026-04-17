"""
Supabase DB Service — async-compatible client using httpx.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

# --- Self-Healing URL Logic ---
# If the user just provided a Project ID (e.g. 'abcde...'), auto-construct the full URL
if SUPABASE_URL and not SUPABASE_URL.startswith("http"):
    if "." not in SUPABASE_URL: # Likely just a Project ID
        print(f"🔧 Auto-fixing SUPABASE_URL: Detected Project ID, converting to https://{SUPABASE_URL}.supabase.co")
        SUPABASE_URL = f"https://{SUPABASE_URL}.supabase.co"
    else:
        # If it has dots but no protocol, just add https://
        SUPABASE_URL = f"https://{SUPABASE_URL}"

# Final validation
if not SUPABASE_URL or not SUPABASE_URL.startswith("https://"):
    raise ValueError(f"CRITICAL: SUPABASE_URL is missing or invalid. Current value: '{SUPABASE_URL}'")
if not SUPABASE_KEY:
    raise ValueError("CRITICAL: SUPABASE_SERVICE_KEY is missing.")

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
        resp.raise_for_status()
        return len(resp.json()) > 0


async def cache_url(url: str, title: str = "") -> None:
    """Mark a URL as indexed."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/url_cache",
            headers={**_HEADERS, "Prefer": "resolution=merge-duplicates"},
            json={"url": url, "title": title},
        )
        resp.raise_for_status()


async def upsert_documents(docs: list[dict]) -> None:
    """
    Insert document chunks with their embeddings into Supabase.
    Each doc: {"content": str, "metadata": dict, "embedding": list[float]}
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers=_HEADERS,
            json=docs,
        )
        resp.raise_for_status()


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
        resp.raise_for_status()
        return resp.json()
