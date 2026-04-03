import httpx

class ResearchScraper:
    # web research orchestrator via SearXNG and Crawl4AI.

    def __init__(self, searxng_url="http://localhost:8080"):
        self.searxng_url = searxng_url

    async def search_and_scrape(self, query):
        """Perform meta-search and scrape the top results."""
        from crawl4ai import AsyncWebCrawler
        
        async with httpx.AsyncClient() as client:
            params = {"q": query, "format": "json"}
            resp = await client.get(f"{self.searxng_url}/search", params=params)
            results = resp.json().get("results", [])

            scraped_data = []
            async with AsyncWebCrawler() as crawler:
                for res in results[:3]:
                    url = res.get("url")
                    if url:
                        crawl_res = await crawler.arun(url=url)
                        scraped_data.append({
                            "title": res.get("title"),
                            "url": url,
                            "markdown": crawl_res.markdown
                        })
            return scraped_data
