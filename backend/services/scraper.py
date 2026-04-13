import asyncio
import hashlib
import logging
import sys
from typing import Optional

import trafilatura
from playwright.async_api import async_playwright

# --- Windows Asyncio Fix ---
# On Windows, the default SelectorEventLoop doesn't support subprocesses/Playwright.
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logger = logging.getLogger(__name__)


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def scrape_url(url: str) -> Optional[str]:
    """
    Attempts to scrape clean text from a URL.
    1. Tries Trafilatura (fast, no browser).
    2. Falls back to Playwright for JS-heavy pages.
    Returns the cleaned text or None on failure.
    """
    # --- Attempt 1: Trafilatura (fast) ---
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
            )
            if text and len(text.strip()) > 200:
                logger.info(f"[Trafilatura] Scraped {url}: {len(text)} chars")
                return text.strip()
    except Exception as e:
        logger.warning(f"[Trafilatura] Failed for {url}: {e}")

    # --- Attempt 2: Playwright fallback ---
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html = await page.content()
            await browser.close()

            text = trafilatura.extract(html, include_comments=False, include_tables=False)
            if text and len(text.strip()) > 200:
                logger.info(f"[Playwright] Scraped {url}: {len(text)} chars")
                return text.strip()
    except Exception as e:
        logger.error(f"[Playwright] Failed for {url}: {e}")

    return None
