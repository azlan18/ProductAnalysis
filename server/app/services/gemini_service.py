"""
Service for interacting with Google Gemini LLM API.
"""
import json
import re
import tempfile
from typing import Dict, Any, List
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.logging_config import get_logger


logger = get_logger(__name__)
pipeline_logger = get_logger("pipeline")


class GeminiService:
    """Service for Gemini LLM integration."""
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
    
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
            "quotes": [<array of relevant quotes>]
        }}
    }},
    "top_praises": [
        {{
            "aspect": "<what people praise>",
            "frequency": <integer>,
            "percentage": <float>,
            "score": <float 0-10>,
            "quotes": [<array of quotes>]
        }}
    ],
    "top_complaints": [
        {{
            "aspect": "<what people complain about>",
            "frequency": <integer>,
            "percentage": <float>,
            "score": <float 0-10>,
            "quotes": [<array of quotes>]
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
            "quotes": [<array of quotes>]
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
            "mentions": <integer>,
            "sentiment": "<better/worse/similar>",
            "quotes": [<array of quotes>]
        }}
    }},
    "value_analysis": {{
        "score": <float 0-10>,
        "sentiment": "<value for money assessment>",
        "percentage_saying_worth_it": <float>,
        "better_alternatives": [<array of alternatives if mentioned>]
    }},
    "summary": {{
        "one_liner": "<one sentence summary>",
        "best_for": [<array of use cases>],
        "not_recommended_for": [<array of use cases>],
        "strengths": [<array of key strengths>],
        "weaknesses": [<array of key weaknesses>],
        "verdict": "<detailed paragraph verdict>"
    }},
    "general_sentiment": "<overall sentiment text>",
    "pros": [<array of pros in markdown format>],
    "cons": [<array of cons in markdown format>],
    "description": "<comprehensive product description in markdown format with all components>"
}}

Important:
- Extract prices from reviews if mentioned, include source URLs from the reviews
- Be thorough and extract all meaningful insights
- Use markdown formatting in description, pros, and cons
- Include emojis where appropriate (👍, 👎, ⚠️, etc.)
- Provide accurate sentiment scores based on review content
- Include actual quotes from reviews in quotes arrays
- Make sure all JSON is properly formatted and valid
"""
    
    def _get_comparison_prompt(self, products_data: List[Dict[str, Any]]) -> str:
        """
        Generate prompt for product comparison.
        
        Args:
            products_data: List of product analysis data
            
        Returns:
            Formatted prompt string
        """
        products_context = "\n\n".join([
            f"Product: {p['product_name']}\n"
            f"Sentiment Score: {p.get('sentiment', {}).get('score', 0)}\n"
            f"Features: {json.dumps(p.get('features', {}), indent=2)}\n"
            f"Top Praises: {json.dumps(p.get('top_praises', []), indent=2)}\n"
            f"Top Complaints: {json.dumps(p.get('top_complaints', []), indent=2)}\n"
            f"Summary: {json.dumps(p.get('summary', {}), indent=2)}\n"
            f"Pros: {p.get('pros', [])}\n"
            f"Cons: {p.get('cons', [])}\n"
            for p in products_data
        ])
        
        return f"""You are an expert product comparison analyst. Compare the following products and provide a comprehensive comparison in JSON format.

Products Data:
{products_context}

Please compare these products and provide the following information in a structured JSON format:

{{
    "overall_winner": "<product_id>",
    "winner_reasoning": "<detailed explanation of why this product wins>",
    "comparison_matrix": {{
        "<feature_name>": {{
            "<product_id>": <score 0-10>,
            "<product_id>": <score 0-10>
        }}
    }},
    "pros_cons": {{
        "<product_id>": {{
            "pros": [<array of pros with emojis if needed>],
            "cons": [<array of cons with emojis if needed>]
        }}
    }},
    "feature_comparison": {{
        "<feature_name>": {{
            "winner": "<product_id>",
            "reasoning": "<why this product wins this feature>",
            "scores": {{
                "<product_id>": <score>,
                "<product_id>": <score>
            }}
        }}
    }},
    "verdict_by_use_case": {{
        "gaming": "<product_id>",
        "photography": "<product_id>",
        "battery_life": "<product_id>",
        "value": "<product_id>",
        "all_rounder": "<product_id>",
        "<other_use_case>": "<product_id>"
    }},
    "key_differences": [
        "<bullet point difference 1>",
        "<bullet point difference 2>",
        "<bullet point difference 3>"
    ],
    "summary": {{
        "recommendation": "<detailed paragraph recommending which product to buy>",
        "best_for_different_users": {{
            "<user_type>": "<product_id and reasoning>"
        }},
        "final_verdict": "<comprehensive final verdict>"
    }}
}}

Important:
- Use emojis where appropriate (👍, 👎, ⚠️, 🏆, etc.)
- Be detailed and specific in comparisons
- Highlight key differences clearly
- Provide actionable recommendations
- Make sure all JSON is properly formatted and valid
- Include all products in comparison_matrix and pros_cons
"""
    
    async def analyze_product(self, reviews: List[str]) -> Dict[str, Any]:
        """
        Analyze product reviews using Gemini LLM.
        
        Args:
            reviews: List of review texts
            
        Returns:
            Structured analysis dictionary
        """
        pipeline_logger.info(f"[GEMINI] Starting product analysis")
        pipeline_logger.debug(f"[GEMINI] Input - Number of reviews: {len(reviews)}")
        
        # Combine all reviews
        reviews_text = "\n\n---\n\n".join(reviews)
        original_length = len(reviews_text)
        pipeline_logger.debug(f"[GEMINI] Combined reviews text length: {original_length} characters")
        
        # Log review lengths for debugging
        review_lengths = [len(r) for r in reviews]
        pipeline_logger.debug(f"[GEMINI] Individual review lengths: {review_lengths}")
        pipeline_logger.debug(f"[GEMINI] Review text preview (first 500 chars): {reviews_text[:500]}...")
        
        # Truncate if too long (Gemini has token limits)
        max_chars = 200000  # Approximate token limit
        if len(reviews_text) > max_chars:
            pipeline_logger.warning(f"[GEMINI] Reviews text too long ({len(reviews_text)} chars), truncating to {max_chars} chars")
            reviews_text = reviews_text[:max_chars] + "\n\n[Content truncated due to length...]"
        
        prompt = self._get_analysis_prompt(reviews_text)
        prompt_length = len(prompt)
        pipeline_logger.debug(f"[GEMINI] Prompt length: {prompt_length} characters")
        pipeline_logger.debug(f"[GEMINI] Prompt preview (first 1000 chars): {prompt[:1000]}...")
        
        try:
            pipeline_logger.info(f"[GEMINI] Calling Gemini API with model: {self.model_name} (JSON mode)")
            
            # Create content with the prompt
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # Generate content config with JSON mode (no strict schema to avoid validation issues)
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="application/json",
            )
            pipeline_logger.debug(f"[GEMINI] Config created with JSON mode (no strict schema)")
            
            # Generate content with structured output (non-streaming)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            )
            
            pipeline_logger.info(f"[GEMINI] Response received - Length: {len(response.text)} characters")
            
            # Parse JSON response (with cleaning for malformed JSON)
            if response.text:
                try:
                    # Try direct parsing first
                    analysis_result = json.loads(response.text)
                    pipeline_logger.info(f"[GEMINI] Successfully parsed JSON response")
                except json.JSONDecodeError as e:
                    pipeline_logger.warning(f"[GEMINI] Initial JSON parse failed: {str(e)}, attempting to clean and retry")
                    
                    # Clean common JSON issues
                    cleaned_text = response.text
                    
                    # Remove markdown code blocks if present
                    import re
                    cleaned_text = re.sub(r'```json\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
                    
                    # Try to extract JSON if it's embedded in other text
                    json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                    if json_match:
                        cleaned_text = json_match.group(0)
                    
                    # Log the problematic area for debugging
                    error_pos = getattr(e, 'pos', 0)
                    context_start = max(0, error_pos - 100)
                    context_end = min(len(cleaned_text), error_pos + 100)
                    pipeline_logger.error(f"[GEMINI] JSON error near position {error_pos}")
                    pipeline_logger.error(f"[GEMINI] Context: ...{cleaned_text[context_start:context_end]}...")
                    
                    try:
                        # Try parsing cleaned version
                        analysis_result = json.loads(cleaned_text)
                        pipeline_logger.info(f"[GEMINI] Successfully parsed JSON after cleaning")
                    except json.JSONDecodeError as e2:
                        pipeline_logger.error(f"[GEMINI] Failed to parse JSON even after cleaning - Error: {str(e2)}")
                        pipeline_logger.error(f"[GEMINI] Full response text saved for debugging")
                        
                        # Save the full response for debugging
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(response.text)
                            pipeline_logger.error(f"[GEMINI] Full response saved to: {f.name}")
                        
                        raise Exception(f"Failed to parse JSON from LLM response even after cleaning: {str(e2)}")
                
                pipeline_logger.debug(f"[GEMINI] Analysis result keys: {list(analysis_result.keys())}")
                
                # Log key metrics from analysis
                if "sentiment" in analysis_result:
                    sentiment_score = analysis_result["sentiment"].get("score", "N/A")
                    pipeline_logger.info(f"[GEMINI] Analysis complete - Sentiment score: {sentiment_score}")
                
                if "top_praises" in analysis_result:
                    pipeline_logger.debug(f"[GEMINI] Top praises count: {len(analysis_result['top_praises'])}")
                
                if "top_complaints" in analysis_result:
                    pipeline_logger.debug(f"[GEMINI] Top complaints count: {len(analysis_result['top_complaints'])}")
                
                pipeline_logger.debug(f"[GEMINI] Full analysis result: {json.dumps(analysis_result, indent=2, default=str)}")
                
                return analysis_result
            else:
                raise Exception("Empty response from Gemini API")
            
        except Exception as e:
            pipeline_logger.error(f"[GEMINI] Error analyzing product: {str(e)}", exc_info=True)
            pipeline_logger.error(f"[GEMINI] Error details - Type: {type(e).__name__}, Message: {str(e)}")
            raise Exception(f"Error analyzing product with Gemini: {str(e)}")
    
    async def compare_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple products using Gemini LLM.
        
        Args:
            products_data: List of product analysis dictionaries
            
        Returns:
            Structured comparison dictionary
        """
        pipeline_logger.info(f"[GEMINI] Starting product comparison")
        pipeline_logger.debug(f"[GEMINI] Input - Number of products: {len(products_data)}")
        pipeline_logger.debug(f"[GEMINI] Product IDs: {[p.get('product_id', 'N/A') for p in products_data]}")
        
        prompt = self._get_comparison_prompt(products_data)
        prompt_length = len(prompt)
        pipeline_logger.debug(f"[GEMINI] Comparison prompt length: {prompt_length} characters")
        pipeline_logger.debug(f"[GEMINI] Prompt preview (first 1000 chars): {prompt[:1000]}...")
        
        try:
            pipeline_logger.info(f"[GEMINI] Calling Gemini API for comparison with model: {self.model_name} (JSON mode)")
            
            # Create content with the prompt
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # Generate content config with JSON mode (no strict schema to avoid validation issues)
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="application/json",
            )
            pipeline_logger.debug(f"[GEMINI] Config created with JSON mode (no strict schema)")
            
            # Generate content with structured output (non-streaming)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            )
            
            pipeline_logger.info(f"[GEMINI] Response received - Length: {len(response.text)} characters")
            
            # Parse JSON response (with cleaning for malformed JSON)
            if response.text:
                try:
                    # Try direct parsing first
                    comparison_result = json.loads(response.text)
                    pipeline_logger.info(f"[GEMINI] Successfully parsed JSON response")
                except json.JSONDecodeError as e:
                    pipeline_logger.warning(f"[GEMINI] Initial JSON parse failed: {str(e)}, attempting to clean and retry")
                    
                    # Clean common JSON issues
                    cleaned_text = response.text
                    
                    # Remove markdown code blocks if present
                    cleaned_text = re.sub(r'```json\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
                    
                    # Try to extract JSON if it's embedded in other text
                    json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                    if json_match:
                        cleaned_text = json_match.group(0)
                    
                    # Log the problematic area for debugging
                    error_pos = getattr(e, 'pos', 0)
                    context_start = max(0, error_pos - 100)
                    context_end = min(len(cleaned_text), error_pos + 100)
                    pipeline_logger.error(f"[GEMINI] JSON error near position {error_pos}")
                    pipeline_logger.error(f"[GEMINI] Context: ...{cleaned_text[context_start:context_end]}...")
                    
                    try:
                        # Try parsing cleaned version
                        comparison_result = json.loads(cleaned_text)
                        pipeline_logger.info(f"[GEMINI] Successfully parsed JSON after cleaning")
                    except json.JSONDecodeError as e2:
                        pipeline_logger.error(f"[GEMINI] Failed to parse JSON even after cleaning - Error: {str(e2)}")
                        pipeline_logger.error(f"[GEMINI] Full response text saved for debugging")
                        
                        # Save the full response for debugging
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(response.text)
                            pipeline_logger.error(f"[GEMINI] Full response saved to: {f.name}")
                        
                        raise Exception(f"Failed to parse JSON from LLM response even after cleaning: {str(e2)}")
                
                pipeline_logger.debug(f"[GEMINI] Comparison result keys: {list(comparison_result.keys())}")
                
                if "overall_winner" in comparison_result:
                    pipeline_logger.info(f"[GEMINI] Overall winner: {comparison_result['overall_winner']}")
                
                pipeline_logger.debug(f"[GEMINI] Full comparison result: {json.dumps(comparison_result, indent=2, default=str)}")
                
                return comparison_result
            else:
                raise Exception("Empty response from Gemini API")
            
        except Exception as e:
            pipeline_logger.error(f"[GEMINI] Error comparing products: {str(e)}", exc_info=True)
            pipeline_logger.error(f"[GEMINI] Error details - Type: {type(e).__name__}, Message: {str(e)}")
            raise Exception(f"Error comparing products with Gemini: {str(e)}")

