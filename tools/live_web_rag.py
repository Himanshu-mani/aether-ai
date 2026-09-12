import asyncio
from langchain_core.tools import tool
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

@tool
async def live_web_scrape_tool(url: str) -> str:
    """
    Input: a valid URL string.
    Scrapes the content of a target URL and returns rich, clean markdown.
    """
    print(f"\n[🌐] AI Chatbot is crawling the web for Creators Himanshu & Anurag: {url}")
    
    # Configure lightweight, headless scraping
    browser_config = BrowserConfig(headless=True, browser_type="chromium")
    
    # Filter junk text naturally and keep the pure content block
    run_config = CrawlerRunConfig(
        word_count_threshold=10,
        exclude_external_links=True
    )
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                print("  [✅] Live Data Extracted Successfully via Crawl4AI!")
                content = result.markdown
                
                # Truncate content to ~3000 chars to save 4GB VRAM during Gemma 2 inference
                return f"[Source: {url}]\n\n{content[:3000]}"
            else:
                return f"Failed to scrape {url}. Error: {result.error_message}"
    except Exception as e:
        return f"Error occurred while scraping {url}: {str(e)}"
