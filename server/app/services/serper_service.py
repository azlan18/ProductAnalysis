"""
Service for interacting with Serper API to search for product review URLs.
"""
import aiohttp
import asyncio
import json
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging_config import get_logger


logger = get_logger(__name__)
pipeline_logger = get_logger("pipeline")


class SerperService:
    """Service for Serper API integration."""
    
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = settings.SERPER_BASE_URL
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def search_product_reviews(self, product_name: str) -> List[str]:
        """
        Search for product review URLs using Serper API.
        Returns list of URLs (2nd to 5th, skipping first).
        
        Args:
            product_name: Name of the product to search for
            
        Returns:
            List of URLs from search results
        """
        query = f"{product_name} shopping reviews"
        
        payload = {
            "q": query,
            "num": settings.SERPER_RESULTS_COUNT,
            "gl": "in",  # India
            "hl": "en"  # English
        }
        
        pipeline_logger.info(f"[SERPER] Starting search for product: {product_name}")
        pipeline_logger.debug(f"[SERPER] Input - Product Name: {product_name}")
        pipeline_logger.debug(f"[SERPER] Query: {query}")
        pipeline_logger.debug(f"[SERPER] Payload: {json.dumps(payload, indent=2)}")
        pipeline_logger.debug(f"[SERPER] Endpoint: {self.base_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                pipeline_logger.debug(f"[SERPER] Making POST request to Serper API...")
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    pipeline_logger.debug(f"[SERPER] Response status: {response.status}")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        pipeline_logger.error(f"[SERPER] API error - Status: {response.status}, Error: {error_text}")
                        raise Exception(f"Serper API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    pipeline_logger.debug(f"[SERPER] Response received - Keys: {list(data.keys())}")
                    
                    # Extract URLs from organic results
                    urls = []
                    if "organic" in data:
                        organic_results = data["organic"]
                        pipeline_logger.info(f"[SERPER] Found {len(organic_results)} organic results")
                        pipeline_logger.debug(f"[SERPER] All organic results: {json.dumps([r.get('link', '') for r in organic_results[:10]], indent=2)}")
                        
                        # Skip first URL (usually useless), take 2nd and 3rd (2 URLs total)
                        if len(organic_results) > 1:
                            urls = [result.get("link", "") for result in organic_results[1:3] if result.get("link")]
                            pipeline_logger.info(f"[SERPER] Extracted {len(urls)} URLs (skipping first result)")
                            pipeline_logger.debug(f"[SERPER] Selected URLs: {json.dumps(urls, indent=2)}")
                        else:
                            pipeline_logger.warning(f"[SERPER] Not enough results (only {len(organic_results)} found)")
                    else:
                        pipeline_logger.warning(f"[SERPER] No 'organic' key in response. Response keys: {list(data.keys())}")
                    
                    if not urls:
                        pipeline_logger.error(f"[SERPER] No URLs extracted from response")
                        pipeline_logger.debug(f"[SERPER] Full response: {json.dumps(data, indent=2)}")
                    
                    pipeline_logger.info(f"[SERPER] Successfully retrieved {len(urls)} URLs for product: {product_name}")
                    return urls
                    
        except aiohttp.ClientError as e:
            pipeline_logger.error(f"[SERPER] Network error calling Serper API: {str(e)}", exc_info=True)
            raise Exception(f"Network error calling Serper API: {str(e)}")
        except Exception as e:
            pipeline_logger.error(f"[SERPER] Error searching for product reviews: {str(e)}", exc_info=True)
            raise Exception(f"Error searching for product reviews: {str(e)}")

