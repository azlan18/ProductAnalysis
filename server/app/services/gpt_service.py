"""
Service for interacting with Azure OpenAI GPT API.
"""
import json
import re
import httpx
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging_config import get_logger


logger = get_logger(__name__)
pipeline_logger = get_logger("pipeline")


class GPTService:
    """Service for Azure OpenAI GPT integration."""
    
    def __init__(self):
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.api_base = settings.AZURE_OPENAI_ENDPOINT
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT
        self.api_version = settings.AZURE_OPENAI_API_VERSION
        self.model = settings.AZURE_OPENAI_MODEL
        
        if not self.api_key:
            logger.error("Azure OpenAI API key not configured")
            raise ValueError("Azure OpenAI API key not configured")
        if not self.api_base:
            logger.error("Azure OpenAI endpoint not configured")
            raise ValueError("Azure OpenAI endpoint not configured")
        if not self.deployment:
            logger.error("Azure OpenAI deployment not configured")
            raise ValueError("Azure OpenAI deployment not configured")
    
    def _get_analysis_prompt(self, reviews_text: str) -> str:
        """
        Generate prompt for product analysis.
        
        Args:
            reviews_text: Combined text from all reviews
            
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert product analyst. Analyze the following product reviews and provide a comprehensive analysis in JSON format.

Reviews Data:
{reviews_text}

Please analyze these reviews and provide the following information in a structured JSON format:

{{
    "sentiment": {{
        "score": <float 0-10>,
        "sentiment": "<positive/negative/neutral>",
        "distribution": {{
            "positive": <percentage>,
            "negative": <percentage>,
            "neutral": <percentage>
        }}
    }},
    "features": {{
        "<feature_name>": {{
            "sentiment": "<positive/negative/neutral>",
            "score": <float 0-10>,
            "mentions": <integer>,
            "quotes": [
                "<actual customer quote text>"
            ]
        }}
    }},
    "top_praises": [
        {{
            "aspect": "<what people praise>",
            "frequency": <integer>,
            "percentage": <float>,
            "score": <float 0-10>,
            "quotes": [
                "<actual customer quote text>"
            ]
        }}
    ],
    "top_complaints": [
        {{
            "aspect": "<what people complain about>",
            "frequency": <integer>,
            "percentage": <float>,
            "score": <float 0-10>,
            "quotes": [
                "<actual customer quote text>"
            ]
        }}
    ],
    "user_segments": [
        {{
            "segment": "<user type>",
            "satisfaction": <float 0-100>,
            "count": <integer>
        }}
    ],
    "quality_issues": [
        {{
            "issue": "<issue description>",
            "frequency": <integer>,
            "severity": "<high/medium/low>",
            "quotes": [
                "<actual customer quote text>"
            ]
        }}
    ],
    "prices": [
        {{
            "source": "<platform name>",
            "url": "<source URL>",
            "price": "<price string>",
            "currency": "<currency code>"
        }}
    ],
    "competitor_mentions": {{
        "<competitor_name>": {{
            "sentiment": "<better/worse/similar>",
            "frequency": <integer>,
            "quotes": [
                "<actual customer quote text>"
            ]
        }}
    }},
    "value_analysis": {{
        "score": <float 0-10>,
        "percentage_saying_worth_it": <float>,
        "reasoning": "<text explanation>"
    }},
    "summary": {{
        "one_liner": "<one sentence summary>",
        "best_for": ["<use case 1>", "<use case 2>"],
        "not_recommended_for": ["<use case 1>", "<use case 2>"],
        "key_strengths": ["<strength 1>", "<strength 2>"],
        "key_weaknesses": ["<weakness 1>", "<weakness 2>"],
        "verdict": "<final verdict paragraph>"
    }},
    "general_sentiment": "<overall sentiment description>",
    "pros": ["<pro 1>", "<pro 2>", "<pro 3>"],
    "cons": ["<con 1>", "<con 2>", "<con 3>"],
    "description": "<markdown formatted product description>"
}}

Return ONLY valid JSON, no markdown formatting or code blocks.

Important:
- DO NOT include customer names or usernames in quotes - use only the quote text
- Extract quotes directly from the review text without adding names"""

    def _get_comparison_prompt(self, products_data: List[Dict[str, Any]]) -> str:
        """
        Generate prompt for product comparison.
        
        Args:
            products_data: List of product analysis dictionaries
            
        Returns:
            Formatted prompt string
        """
        products_text = "\n\n".join([
            f"Product {i+1}: {product['product_name']}\n{json.dumps(product, indent=2)}"
            for i, product in enumerate(products_data)
        ])
        
        return f"""You are an expert product comparison analyst. Compare the following products based on their analysis data and provide a comprehensive comparison in JSON format.

Products Data:
{products_text}

Please compare these products and provide the following information in a structured JSON format:

{{
    "overall_winner": "<product_id>",
    "winner_reasoning": "<why this product won>",
    "comparison_matrix": {{
        "<feature_name>": {{
            "<product_id_1>": <score 0-10>,
            "<product_id_2>": <score 0-10>
        }}
    }},
    "pros_cons": {{
        "<product_id>": {{
            "pros": [
                "<actual customer quote or pro point>"
            ],
            "cons": [
                "<actual customer quote or con point>"
            ]
        }}
    }},
    "feature_comparison": {{
        "<feature_name>": {{
            "winner": "<product_id>",
            "reasoning": "<why this product is better for this feature>",
            "quotes": [
                "<supporting customer quote>"
            ]
        }}
    }},
    "verdict_by_use_case": {{
        "<use_case>": "<product_id> - <reasoning>"
    }},
    "key_differences": [
        "<bullet point difference description>"
    ],
    "summary": {{
        "recommendation": "<overall recommendation>",
        "best_for": {{
            "<use_case>": "<product_id>"
        }}
    }}
}}

Return ONLY valid JSON, no markdown formatting or code blocks.

Important:
- Extract ACTUAL customer quotes from the original product analysis data - use the quotes from top_praises, top_complaints, and features
- DO NOT include customer names or usernames - just use the quote text directly
- Use emojis where appropriate (👍, 👎, ⚠️, 🏆, etc.)
- Be detailed and specific in comparisons
- Highlight key differences clearly with supporting quotes
- Provide actionable recommendations
- Make sure all JSON is properly formatted and valid
- Include all products in comparison_matrix and pros_cons
- key_differences should be a simple list of strings, not objects"""

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response, handling code blocks and markdown.
        
        Args:
            response_text: Raw response text from LLM
            
        Returns:
            Parsed JSON dictionary
        """
        pipeline_logger.debug(f"[GPT] Extracting JSON from response (length: {len(response_text)} chars)")
        
        # Remove markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        try:
            result = json.loads(response_text)
            pipeline_logger.debug(f"[GPT] Successfully parsed JSON response")
            return result
        except json.JSONDecodeError as e:
            pipeline_logger.error(f"[GPT] Failed to parse JSON response: {str(e)}")
            pipeline_logger.debug(f"[GPT] Response text: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from GPT: {str(e)}")

    async def generate_response(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Generate response from Azure OpenAI GPT.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response text from GPT
        """
        request_data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that returns responses in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Lower temperature for more consistent JSON output
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}  # Force JSON response
        }
        
        url = f"{self.api_base}/openai/deployments/{self.deployment}/chat/completions"
        params = {
            "api-version": self.api_version
        }
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        max_retries = 3
        retry_delay = 2
        timeout = 120.0  # Increased timeout for large responses
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    pipeline_logger.debug(f"[GPT] Making request to Azure OpenAI (attempt {attempt + 1}/{max_retries})")
                    response = await client.post(
                        url,
                        params=params,
                        headers=headers,
                        json=request_data,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        response_json = response.json()
                        
                        # Extract the actual response content
                        if "choices" in response_json and len(response_json["choices"]) > 0:
                            message_content = response_json["choices"][0]["message"]["content"]
                            pipeline_logger.debug(f"[GPT] Response received - Length: {len(message_content)} chars")
                            return message_content
                        else:
                            pipeline_logger.error(f"[GPT] Unexpected response format: {response_json}")
                            raise ValueError("Invalid response format from Azure OpenAI")
                    
                    # If we get here, the response wasn't successful
                    error_msg = f"Azure OpenAI API error: HTTP {response.status_code}"
                    if response.text:
                        error_msg += f" - {response.text}"
                    pipeline_logger.error(f"[GPT] {error_msg}")
                    
                    # If it's a timeout or server error, retry
                    if response.status_code >= 500 or response.status_code == 429:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)
                            pipeline_logger.warning(f"[GPT] Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_msg
                    )
                    
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    pipeline_logger.warning(f"[GPT] Request timed out. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    pipeline_logger.error("[GPT] Azure OpenAI API request timed out after all retries")
                    raise HTTPException(
                        status_code=500,
                        detail="Azure OpenAI API request timed out after multiple retries"
                    )
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    pipeline_logger.warning(f"[GPT] Request failed. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    pipeline_logger.error(f"[GPT] Azure OpenAI API request failed after all retries: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Azure OpenAI API request failed after multiple retries: {str(e)}"
                    )
            except Exception as e:
                pipeline_logger.error(f"[GPT] Unexpected error: {str(e)}", exc_info=True)
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    pipeline_logger.warning(f"[GPT] Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise

    async def analyze_product(self, reviews: List[str]) -> Dict[str, Any]:
        """
        Analyze product reviews using GPT.
        
        Args:
            reviews: List of review text strings
            
        Returns:
            Analysis result dictionary
        """
        gpt_start = time.time()
        pipeline_logger.info(f"[GPT] [ANALYZE START] {datetime.now().strftime('%H:%M:%S')}")
        pipeline_logger.info(f"[GPT] Input: {len(reviews)} review(s), {sum(len(r) for r in reviews)} total chars")
        
        # Combine all reviews
        combine_start = time.time()
        reviews_text = "\n\n---REVIEW SEPARATOR---\n\n".join(reviews)
        combine_duration = time.time() - combine_start
        pipeline_logger.debug(f"[GPT] Combined reviews - Duration: {combine_duration:.3f}s, Length: {len(reviews_text)} chars")
        
        # Generate prompt
        prompt_start = time.time()
        prompt = self._get_analysis_prompt(reviews_text)
        prompt_duration = time.time() - prompt_start
        pipeline_logger.debug(f"[GPT] Prompt generated - Duration: {prompt_duration:.3f}s, Length: {len(prompt)} chars")
        
        # Get response from GPT
        api_start = time.time()
        pipeline_logger.info(f"[GPT] Calling Azure OpenAI API (deployment: {self.deployment})...")
        full_response = await self.generate_response(prompt, max_tokens=4000)
        api_duration = time.time() - api_start
        pipeline_logger.info(f"[GPT] API call completed - Duration: {api_duration:.2f}s, Response length: {len(full_response)} chars")
        
        # Extract JSON from response
        parse_start = time.time()
        pipeline_logger.debug(f"[GPT] Parsing JSON from response...")
        analysis_result = self._extract_json_from_response(full_response)
        parse_duration = time.time() - parse_start
        pipeline_logger.info(f"[GPT] JSON parsed successfully - Duration: {parse_duration:.3f}s")
        pipeline_logger.debug(f"[GPT] Analysis result keys: {list(analysis_result.keys())}")
        
        # Log key metrics from analysis
        if "sentiment" in analysis_result:
            sentiment_score = analysis_result["sentiment"].get("score", "N/A")
            pipeline_logger.info(f"[GPT] Sentiment score: {sentiment_score}")
        
        if "top_praises" in analysis_result:
            pipeline_logger.debug(f"[GPT] Top praises: {len(analysis_result['top_praises'])} items")
        
        if "top_complaints" in analysis_result:
            pipeline_logger.debug(f"[GPT] Top complaints: {len(analysis_result['top_complaints'])} items")
        
        total_duration = time.time() - gpt_start
        pipeline_logger.info(f"[GPT] [ANALYZE END] ✅ Duration: {total_duration:.2f}s (Combine={combine_duration:.3f}s, Prompt={prompt_duration:.3f}s, API={api_duration:.2f}s, Parse={parse_duration:.3f}s)")
        
        return analysis_result

    async def compare_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple products using GPT.
        
        Args:
            products_data: List of product analysis dictionaries
            
        Returns:
            Comparison result dictionary
        """
        pipeline_logger.info(f"[GPT] Starting product comparison")
        pipeline_logger.debug(f"[GPT] Input - Number of products: {len(products_data)}")
        
        # Generate prompt
        prompt = self._get_comparison_prompt(products_data)
        pipeline_logger.debug(f"[GPT] Prompt length: {len(prompt)} characters")
        pipeline_logger.debug(f"[GPT] Prompt preview (first 500 chars): {prompt[:500]}...")
        
        # Get response from GPT
        full_response = await self.generate_response(prompt, max_tokens=4000)
        
        pipeline_logger.info(f"[GPT] Response received - Length: {len(full_response)} characters")
        pipeline_logger.debug(f"[GPT] Response preview (first 1000 chars): {full_response[:1000]}...")
        
        # Extract JSON from response
        pipeline_logger.debug(f"[GPT] Extracting JSON from response...")
        comparison_result = self._extract_json_from_response(full_response)
        
        pipeline_logger.info(f"[GPT] Successfully parsed JSON response")
        pipeline_logger.debug(f"[GPT] Comparison result keys: {list(comparison_result.keys())}")
        
        return comparison_result

