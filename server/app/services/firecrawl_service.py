"""
Service for interacting with Firecrawl API to scrape web pages.
"""
import aiohttp
import asyncio
import json
from typing import List, Dict, Any
from app.core.config import settings
from app.utils.helpers import extract_domain, extract_platform_name
from app.core.logging_config import get_logger


logger = get_logger(__name__)
pipeline_logger = get_logger("pipeline")


class FirecrawlService:
    """Service for Firecrawl API integration."""
    
    def __init__(self):
        self.api_key = settings.FIRECRAWL_API_KEY
        self.base_url = settings.FIRECRAWL_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = settings.SCRAPER_TIMEOUT
        self.max_concurrent = settings.MAX_CONCURRENT_SCRAPERS
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single URL using Firecrawl API.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content and metadata
        """
        payload = {
            "url": url,
            "onlyMainContent": True,
            "maxAge": 172800000,  # 2 days in milliseconds
            "parsers": ["pdf"],
            "formats": ["markdown"],
            "excludeTags": [
                "nav",
                "header",
                "footer",
                "aside",
                "script",
                "style",
                "iframe",
                "svg",
                "button",
                "input",
                "select",
                "textarea",
                "form",
                "menu",
                "sidebar",
                "advertisement",
                "ads",
                "ad-banner",
                "ad-container",
                "ad-wrapper",
                "ad-banner-container",
                "promo",
                "promo-box",
                "popup",
                "popup-overlay",
                "cookie-banner",
                "cookie-notice",
                "cookie-consent",
                "social-media",
                "social-share",
                "share-buttons",
                "share-widget",
                "comments-section",
                "comments-container",
                "related-products",
                "related-items",
                "breadcrumb",
                "breadcrumbs",
                "search-bar",
                "search-box",
                "notification",
                "notification-banner",
                "alert",
                "alert-box",
                "modal",
                "modal-overlay",
                "newsletter",
                "newsletter-signup",
                "subscribe",
                "top-bar",
                "topbar",
                "sticky-header",
                "sticky-footer",
                "navbar",
                "navigation"
            ]
        }
        
        pipeline_logger.debug(f"[FIRECRAWL] Starting scrape for URL: {url}")
        pipeline_logger.debug(f"[FIRECRAWL] Payload: {json.dumps(payload, indent=2)}")
        pipeline_logger.debug(f"[FIRECRAWL] Endpoint: {self.base_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                pipeline_logger.debug(f"[FIRECRAWL] Making POST request to Firecrawl API for: {url}")
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    pipeline_logger.debug(f"[FIRECRAWL] Response status for {url}: {response.status}")
                    
                    # Check HTTP status first
                    if response.status != 200:
                        try:
                            error_data = await response.json()
                            error_text = error_data.get("error", f"HTTP {response.status} error")
                            pipeline_logger.error(f"[FIRECRAWL] HTTP error for {url} - Status: {response.status}, Error: {error_text}")
                            pipeline_logger.debug(f"[FIRECRAWL] Error response: {json.dumps(error_data, indent=2)}")
                        except:
                            error_text = await response.text()
                            pipeline_logger.error(f"[FIRECRAWL] HTTP error for {url} - Status: {response.status}, Error: {error_text}")
                        
                        return {
                            "url": url,
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "content": "",
                            "domain": extract_domain(url),
                            "platform": extract_platform_name(url)
                        }
                    
                    data = await response.json()
                    pipeline_logger.debug(f"[FIRECRAWL] Response keys for {url}: {list(data.keys())}")
                    
                    # Check for errors in response
                    if not data.get("success", False):
                        error_msg = data.get("error", "Unknown error")
                        pipeline_logger.error(f"[FIRECRAWL] API error for {url}: {error_msg}")
                        pipeline_logger.debug(f"[FIRECRAWL] Error response: {json.dumps(data, indent=2)}")
                        return {
                            "url": url,
                            "success": False,
                            "error": f"Firecrawl error: {error_msg}",
                            "content": "",
                            "domain": extract_domain(url),
                            "platform": extract_platform_name(url)
                        }
                    
                    # Extract markdown content from v2 API response
                    content = ""
                    if "data" in data and "markdown" in data["data"]:
                        content = data["data"]["markdown"]
                        pipeline_logger.debug(f"[FIRECRAWL] Extracted markdown content length: {len(content)} characters")
                    elif "markdown" in data:
                        content = data["markdown"]
                        pipeline_logger.debug(f"[FIRECRAWL] Extracted markdown content length: {len(content)} characters")
                    else:
                        pipeline_logger.warning(f"[FIRECRAWL] No markdown content found in response for {url}")
                        pipeline_logger.debug(f"[FIRECRAWL] Response structure: {json.dumps(list(data.keys()) if isinstance(data, dict) else 'not a dict', indent=2)}")
                    
                    if content:
                        pipeline_logger.info(f"[FIRECRAWL] Successfully scraped {url} - Content length: {len(content)} chars")
                        # Log first 200 chars of content for debugging
                        pipeline_logger.debug(f"[FIRECRAWL] Content preview (first 200 chars): {content[:200]}...")
                    else:
                        pipeline_logger.warning(f"[FIRECRAWL] No content extracted from {url}")
                    
                    metadata = data.get("data", {}).get("metadata", {})
                    pipeline_logger.debug(f"[FIRECRAWL] Metadata for {url}: {json.dumps(metadata, indent=2, default=str)}")
                    
                    return {
                        "url": url,
                        "success": True,
                        "content": content,
                        "domain": extract_domain(url),
                        "platform": extract_platform_name(url),
                        "metadata": metadata
                    }
                    
        except asyncio.TimeoutError:
            pipeline_logger.error(f"[FIRECRAWL] Timeout error for URL: {url}")
            return {
                "url": url,
                "success": False,
                "error": "Timeout",
                "content": "",
                "domain": extract_domain(url),
                "platform": extract_platform_name(url)
            }
        except Exception as e:
            pipeline_logger.error(f"[FIRECRAWL] Exception scraping {url}: {str(e)}", exc_info=True)
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "content": "",
                "domain": extract_domain(url),
                "platform": extract_platform_name(url)
            }
    
    async def scrape_urls_parallel(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs in parallel with concurrency limit.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scrape results
        """
        pipeline_logger.info(f"[FIRECRAWL] Starting parallel scrape for {len(urls)} URLs")
        pipeline_logger.debug(f"[FIRECRAWL] URLs to scrape: {json.dumps(urls, indent=2)}")
        pipeline_logger.debug(f"[FIRECRAWL] Max concurrent workers: {self.max_concurrent}")
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scrape_with_semaphore(url: str):
            async with semaphore:
                return await self.scrape_url(url)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        successful_count = 0
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pipeline_logger.error(f"[FIRECRAWL] Exception for URL {urls[i]}: {str(result)}", exc_info=True)
                processed_results.append({
                    "url": urls[i],
                    "success": False,
                    "error": str(result),
                    "content": "",
                    "domain": extract_domain(urls[i]),
                    "platform": extract_platform_name(urls[i])
                })
                failed_count += 1
            else:
                processed_results.append(result)
                if result.get("success"):
                    successful_count += 1
                else:
                    failed_count += 1
        
        pipeline_logger.info(f"[FIRECRAWL] Parallel scrape completed - Success: {successful_count}, Failed: {failed_count}, Total: {len(urls)}")
        pipeline_logger.debug(f"[FIRECRAWL] Scrape results summary: {json.dumps([{'url': r['url'], 'success': r.get('success'), 'error': r.get('error', '')} for r in processed_results], indent=2)}")
        
        return processed_results

