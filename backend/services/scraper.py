import asyncio
import hashlib
import logging
import os
from typing import Optional

from firecrawl import FirecrawlApp

logger = logging.getLogger(__name__)


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def _firecrawl_scrape(url: str) -> tuple[Optional[str], Optional[str]]:
    """Synchronous Firecrawl scrape call."""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.error("❌ FIRECRAWL_API_KEY environment variable is missing.")
        raise ValueError("FIRECRAWL_API_KEY is missing.")
        
    app = FirecrawlApp(api_key=api_key)
    logger.info(f"🔥 Scraping {url} via Firecrawl...")
    
    # Use scrape_url to get the markdown content directly
    scrape_result = app.scrape_url(url, params={'formats': ['markdown']})
    
    # Handle response depending on SDK version returns
    if isinstance(scrape_result, dict):
        if 'data' in scrape_result and isinstance(scrape_result['data'], dict):
            # Format returned by some SDK versions
            text = scrape_result['data'].get('markdown')
            metadata = scrape_result['data'].get('metadata', {})
        else:
            # Format returned by newer SDK versions
            text = scrape_result.get('markdown')
            metadata = scrape_result.get('metadata', {})
    else:
        logger.error(f"❌ Unexpected Firecrawl response type: {type(scrape_result)}")
        return None, None
        
    title = metadata.get('title')
    
    if text and len(text.strip()) > 50:
        logger.info(f"✅ Firecrawl success: {len(text)} chars scraped.")
        return text.strip(), title
        
    logger.warning(f"⚠️ Firecrawl returned empty or very short content for {url}")
    return None, None


async def scrape_url(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Scrapes clean markdown text and title from a URL using Firecrawl API.
    Returns (cleaned_text, page_title).
    """
    try:
        # Run the synchronous Firecrawl call in a thread to avoid blocking the async event loop
        return await asyncio.to_thread(_firecrawl_scrape, url)
    except Exception as e:
        logger.error(f"❌ Firecrawl failed for {url}: {str(e)}", exc_info=True)
        return None, None
