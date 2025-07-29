import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.processors.pdf import PDFCrawlerStrategy, PDFContentScrapingStrategy
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

class Crawl4aiScraper:
    def __init__(self, link, session=None):
        self.link = link
        self.session = session

    async def scrape_async(self):
        if self.link.lower().endswith(".pdf"):
            crawler_strategy = PDFCrawlerStrategy()
            scraping_strategy = PDFContentScrapingStrategy(extract_images=True)
            run_config = CrawlerRunConfig(scraping_strategy=scraping_strategy)
        else:
            crawler_strategy = None
            markdown_generator = DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.6, threshold_type="dynamic"),
                options={
                    "ignore_links": True,
                    "ignore_images": True,
                    "escape_html": True,
                    "body_width": 0,
                    "skip_internal_links": True,
                    "include_sup_sub": True
                }
            )
            run_config = CrawlerRunConfig(
                exclude_external_links=True,
                remove_overlay_elements=True,
                process_iframes=True,
                include_images=True,
                markdown_generator=markdown_generator
            )

        try:
            browser_config = BrowserConfig(headless=True)
            async with AsyncWebCrawler(config=browser_config, crawler_strategy=crawler_strategy) as crawler:
                result = await asyncio.wait_for(crawler.arun(self.link, config=run_config), timeout=30)
        except asyncio.TimeoutError:
            result = None

        if not result or not result.markdown.fit_markdown or len(result.markdown.fit_markdown) < 100:
            try:
                archive_url = f"https://archive.is/newest/{self.link}"
                async with AsyncWebCrawler(config=browser_config, crawler_strategy=crawler_strategy) as crawler:
                    result = await asyncio.wait_for(crawler.arun(archive_url, config=run_config), timeout=30)
            except asyncio.TimeoutError:
                result = None

        if result and result.success:
            return result.markdown.fit_markdown, result.media.get("images", []), result.metadata.get("title", "")
        else:
            return "", [], ""

if __name__ == '__main__':
    async def main():
        scraper = Crawl4aiScraper("https://arxiv.org/pdf/2310.06825.pdf")
        content, images, title = await scraper.scrape_async()
        print("Title:", title)
        print("Content:", content)
        print("Images:", images)
    asyncio.run(main())
