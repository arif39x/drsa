import httpx
from crawl4ai import WebCrawler

class ResearchScraper:
    # web research orchestrator via SearXNG and Crawl4AI.

    def __init__(self, searxng_url="http://localhost:8080"):
        self.searxng_url = searxng_url
        self.crawler = WebCrawler()

    async def search_and_scrape(self, query):
        """Perform meta-search and scrape the top results."""
        async with httpx.AsyncClient() as client:
            params = {"q": query, "format": "json"}
            resp = await client.get(f"{self.searxng_url}/search", params=params)
            results = resp.json().get("results", [])

            scraped_data = []
            for res in results[:3]:
                url = res.get("url")
                if url:
                    crawl_res = self.crawler.run(url=url)
                    scraped_data.append({
                        "title": res.get("title"),
                        "url": url,
                        "markdown": crawl_res.markdown
                    })
            return scraped_data
