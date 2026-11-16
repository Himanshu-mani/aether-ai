"""Crawl public HTTP(S) pages for live retrieval."""

import ipaddress
import socket
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from langchain_core.tools import tool


def _validate_public_url(url: str) -> str | None:
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return "Only valid public HTTP or HTTPS URLs can be crawled."
        host = parsed.hostname.rstrip(".").lower()
        if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal")):
            return "Local and internal network URLs are not allowed."
        try:
            addresses = [ipaddress.ip_address(host)]
        except ValueError:
            try:
                addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, None)]
            except (OSError, ValueError):
                return "The URL hostname could not be resolved."
        if any(not address.is_global for address in addresses):
            return "Private, loopback, and reserved network addresses are not allowed."
        return None
    except ValueError:
        return "Invalid URL."


@tool
async def live_web_scrape_tool(url: str) -> str:
    """Fetch readable content from a public HTTP(S) webpage."""
    error = _validate_public_url(url)
    if error:
        return error
    browser_config = BrowserConfig(headless=True, browser_type="chromium")
    run_config = CrawlerRunConfig(word_count_threshold=10, exclude_external_links=True)
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if not result.success:
                return f"Failed to scrape {url}: {result.error_message}"
            content = (result.markdown or "").strip()
            if not content:
                return f"No readable text was found at {url}."
            return f"[Source: {url}]\n\n{content[:3000]}"
    except Exception as exc:
        return f"Error occurred while scraping {url}: {exc}"
