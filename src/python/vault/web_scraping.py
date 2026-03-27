"""
Layer 3: VAULT – Relative Web Scraping
Privacy-first scraper using Crawl4AI (primary) or Firecrawl (fallback).
Called from Rust vault pipeline or Python agent tool nodes.
"""
import asyncio


async def scrape_url(url: str) -> str:
    """Scrape a URL and return clean markdown content."""
    try:
        from crawl4ai import AsyncWebCrawler
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return result.markdown or result.cleaned_html or ""
    except ImportError:
        pass

    # Fallback: basic requests + BeautifulSoup
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=15, headers={"User-Agent": "DRSA/1.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove script/style
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except ImportError:
        return f"(No scraper installed. Run: pip install crawl4ai)\nURL: {url}"


def scrape(url: str) -> str:
    """Synchronous entry point called from Rust via PyO3."""
    return asyncio.run(scrape_url(url))
