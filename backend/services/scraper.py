import asyncio
import hashlib
import logging
import re
from typing import Optional

import httpx
import trafilatura
from trafilatura.settings import use_config

logger = logging.getLogger(__name__)

# Configure trafilatura for maximum text extraction
_trafilatura_config = use_config()
_trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def scrape_url(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Scrapes clean text and title from a URL.
    3-tier approach — no Playwright/Chromium required:
      1. Trafilatura direct fetch (fastest)
      2. httpx with browser headers + Trafilatura HTML parsing
      3. Raw HTML tag-stripping (last resort)
    Returns (cleaned_text, page_title).
    """

    # --- Attempt 1: Trafilatura direct fetch ---
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(
                downloaded,
                config=_trafilatura_config,
                include_comments=False,
                include_tables=True,
                favor_precision=False,
                favor_recall=True,
            )
            title = None
            try:
                meta = trafilatura.extract_metadata(downloaded)
                title = meta.title if meta else None
            except Exception:
                pass

            if text and len(text.strip()) > 200:
                logger.info(f"[Trafilatura] Scraped {url}: {len(text)} chars")
                return text.strip(), title
            else:
                logger.warning(f"[Trafilatura] Only {len(text or '')} chars — trying httpx fallback...")
    except Exception as e:
        logger.warning(f"[Trafilatura] Failed for {url}: {e}")

    # --- Attempt 2: httpx with browser-like headers ---
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        # Extract title from <title> tag
        title = None
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = re.sub(r"\s+", " ", title_match.group(1)).strip()

        # Use trafilatura to parse clean text from the raw HTML
        text = trafilatura.extract(
            html,
            config=_trafilatura_config,
            include_comments=False,
            include_tables=True,
            favor_precision=False,
            favor_recall=True,
        )

        if text and len(text.strip()) > 200:
            logger.info(f"[httpx] Scraped {url}: {len(text)} chars")
            return text.strip(), title
        else:
            logger.warning(f"[httpx] Low content for {url}: {len(text or '')} chars — trying raw fallback...")

    except Exception as e:
        logger.error(f"[httpx] Failed for {url}: {e}")

    # --- Attempt 3: Raw HTML tag stripping (last resort) ---
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url)
            html = response.text

        # Remove <script> and <style> blocks
        html = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", "", html, flags=re.DOTALL | re.IGNORECASE)
        # Strip remaining HTML tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()

        if text and len(text) > 200:
            logger.info(f"[Fallback] Raw text for {url}: {len(text)} chars")
            return text[:50000], None  # Cap at 50k chars to avoid token overload

    except Exception as e:
        logger.error(f"[Fallback] Failed for {url}: {e}")

    logger.error(f"All scraping attempts failed for {url}")
    return None, None
