import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, GeolocationConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

class Crawl4aiScraper:
    def __init__(self, link, session=None):
        self.link = link
        self.session = session

    async def scrape_async(self):
        crawler_strategy = None
        markdown_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.6, threshold_type="dynamic", min_word_threshold=30),
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
            remove_overlay_elements=True,
            markdown_generator=markdown_generator,
            simulate_user=True,
            magic=True,
        )

        browser_config = BrowserConfig(headless=True)

        try:
            async with AsyncWebCrawler(config=browser_config, crawler_strategy=crawler_strategy) as crawler:
                result = await crawler.arun(self.link, config=run_config)
        except Exception:
            result = None

        if result and result.success:
            return result.markdown.fit_markdown, result.media.get("images", []), result.metadata.get("title", "")
        else:
            return "", [], ""

if __name__ == '__main__':
    async def main():
        scraper = Crawl4aiScraper("https://www.cnn.com")
        content, images, title = await scraper.scrape_async()
        print("Title:", title)
        print("Content:", content)
        print("Images:", images)
    asyncio.run(main())
