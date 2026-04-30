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
    
    # Use scrape to get the markdown content directly
    scrape_result = app.scrape(url=url, formats=['markdown'])
    
    # The new SDK returns an object with attributes
    if hasattr(scrape_result, 'markdown'):
        text = scrape_result.markdown
        title = None
        if hasattr(scrape_result, 'metadata'):
            if hasattr(scrape_result.metadata, 'title'):
                title = scrape_result.metadata.title
            elif isinstance(scrape_result.metadata, dict):
                title = scrape_result.metadata.get('title')
                
    # Fallback for dict responses (older SDKs or raw API responses)
    elif isinstance(scrape_result, dict):
        if 'data' in scrape_result and isinstance(scrape_result['data'], dict):
            text = scrape_result['data'].get('markdown')
            metadata = scrape_result['data'].get('metadata', {})
        else:
            text = scrape_result.get('markdown')
            metadata = scrape_result.get('metadata', {})
        title = metadata.get('title')
    else:
        logger.error(f"❌ Unexpected Firecrawl response type: {type(scrape_result)}")
        return None, None
        
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
