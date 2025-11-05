"""
API endpoints for product operations.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import re
import json
import time
from datetime import datetime
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductListResponse,
    ProductAnalysisResponse
)
from app.services.storage_service import StorageService
from app.services.serper_service import SerperService
from app.services.firecrawl_service import FirecrawlService
from app.services.gemini_service import GeminiService
from app.utils.helpers import generate_product_id
from app.core.logging_config import get_logger


logger = get_logger(__name__)
pipeline_logger = get_logger("pipeline")


router = APIRouter(prefix="/products", tags=["products"])

storage_service = StorageService()
serper_service = SerperService()
firecrawl_service = FirecrawlService()
gpt_service = GeminiService()


async def analyze_product_pipeline(product_id: str, product_name: str):
    """
    Background task to run the complete product analysis pipeline.
    
    Steps:
    1. Search for review URLs using Serper
    2. Scrape URLs using Firecrawl (sequentially)
    3. Extract review text
    4. Analyze with GPT LLM (after each scrape)
    5. Save results to MongoDB
    """
    pipeline_start_time = time.time()
    pipeline_logger.info(f"\n{'='*80}")
    pipeline_logger.info(f"[PIPELINE START] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pipeline_logger.info(f"[PIPELINE START] Product ID: {product_id}")
    pipeline_logger.info(f"[PIPELINE START] Product Name: {product_name}")
    pipeline_logger.info(f"{'='*80}\n")
    
    try:
        # Stage 1: Search for URLs
        stage1_start = time.time()
        pipeline_logger.info(f"\n{'─'*80}")
        pipeline_logger.info(f"[STAGE 1] SERPER SEARCH - STARTED")
        pipeline_logger.info(f"[STAGE 1] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pipeline_logger.info(f"[STAGE 1] Searching for: {product_name}")
        pipeline_logger.info(f"{'─'*80}")
        
        await storage_service.update_processing_status(
            product_id=product_id,
            stage="search",
            status="in_progress",
            progress=10,
            current_step=f"Searching for review URLs for {product_name}..."
        )
        
        urls = await serper_service.search_product_reviews(product_name)
        stage1_duration = time.time() - stage1_start
        
        if not urls:
            pipeline_logger.error(f"[STAGE 1] ❌ FAILED - No URLs returned from Serper API")
            pipeline_logger.error(f"[STAGE 1] Duration: {stage1_duration:.2f}s")
            await storage_service.update_processing_status(
                product_id=product_id,
                stage="search",
                status="failed",
                progress=0,
                current_step="No review URLs found",
                error="No URLs returned from Serper API"
            )
            return
        
        pipeline_logger.info(f"[STAGE 1] ✅ COMPLETED - Found {len(urls)} URLs")
        pipeline_logger.info(f"[STAGE 1] Duration: {stage1_duration:.2f}s")
        pipeline_logger.debug(f"[STAGE 1] URLs: {json.dumps(urls, indent=2)}")
        
        await storage_service.update_processing_status(
            product_id=product_id,
            stage="scrape",
            status="in_progress",
            progress=20,
            current_step=f"Found {len(urls)} URLs. Starting to scrape..."
        )
        
        # Stage 2: Process URLs sequentially (scrape → analyze → save)
        stage2_start = time.time()
        pipeline_logger.info(f"\n{'─'*80}")
        pipeline_logger.info(f"[STAGE 2] SEQUENTIAL URL PROCESSING - STARTED")
        pipeline_logger.info(f"[STAGE 2] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pipeline_logger.info(f"[STAGE 2] Processing {len(urls)} URLs sequentially")
        pipeline_logger.info(f"[STAGE 2] Flow: Scrape → Save → Analyze → Save (for each URL)")
        pipeline_logger.info(f"{'─'*80}")
        
        accumulated_reviews = []
        successful_scrapes = 0
        failed_scrapes = 0
        
        for i, url in enumerate(urls):
            url_start_time = time.time()
            pipeline_logger.info(f"\n{'·'*80}")
            pipeline_logger.info(f"[URL {i+1}/{len(urls)}] STARTED - {datetime.now().strftime('%H:%M:%S')}")
            pipeline_logger.info(f"[URL {i+1}/{len(urls)}] Target: {url}")
            pipeline_logger.info(f"{'·'*80}")
            
            # Update progress
            progress = 20 + int((i / len(urls)) * 60)
            await storage_service.update_processing_status(
                product_id=product_id,
                stage="scrape",
                status="in_progress",
                progress=min(progress, 80),
                current_step=f"Scraping URL {i+1}/{len(urls)}..."
            )
            
            # Step 2.1: Scrape URL
            scrape_start = time.time()
            pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.1] SCRAPING...")
            scrape_result = await firecrawl_service.scrape_url(url)
            scrape_duration = time.time() - scrape_start
            pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.1] Scrape duration: {scrape_duration:.2f}s")
            
            # Save raw review immediately
            if scrape_result.get("success") and scrape_result.get("content"):
                content = scrape_result.get("content", "")
                if content:
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.1] ✅ Scrape SUCCESS - Content: {len(content)} chars")
                    
                    # Step 2.2: Save raw review
                    save_start = time.time()
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.2] SAVING RAW REVIEW TO DATABASE...")
                    await storage_service.save_raw_reviews(product_id, [scrape_result])
                    save_duration = time.time() - save_start
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.2] ✅ Save duration: {save_duration:.2f}s")
                    
                    accumulated_reviews.append(content)
                    successful_scrapes += 1
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.2] Accumulated reviews: {len(accumulated_reviews)}")
                    
                    # Update progress
                    progress = 20 + int(((i + 0.5) / len(urls)) * 60)
                    await storage_service.update_processing_status(
                        product_id=product_id,
                        stage="analyze",
                        status="in_progress",
                        progress=min(progress, 80),
                        current_step=f"Analyzing {len(accumulated_reviews)} review(s) with AI..."
                    )
                    
                    # Step 2.3: Analyze accumulated reviews
                    analyze_start = time.time()
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.3] ANALYZING WITH GPT...")
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.3] Input: {len(accumulated_reviews)} review(s), {sum(len(r) for r in accumulated_reviews)} total chars")
                    analysis_result = await gpt_service.analyze_product(accumulated_reviews)
                    analyze_duration = time.time() - analyze_start
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.3] ✅ Analysis duration: {analyze_duration:.2f}s")
                    pipeline_logger.debug(f"[URL {i+1}/{len(urls)}] [STEP 2.3] Analysis keys: {list(analysis_result.keys())}")
                    
                    # Step 2.4: Save analysis results
                    save_analysis_start = time.time()
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.4] SAVING ANALYSIS RESULTS TO DATABASE...")
                    await storage_service.save_analysis_results(product_id, analysis_result)
                    save_analysis_duration = time.time() - save_analysis_start
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] [STEP 2.4] ✅ Save duration: {save_analysis_duration:.2f}s")
                    
                    url_duration = time.time() - url_start_time
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] ✅ COMPLETED - Total duration: {url_duration:.2f}s")
                    pipeline_logger.info(f"[URL {i+1}/{len(urls)}] Breakdown: Scrape={scrape_duration:.2f}s, Save={save_duration:.2f}s, Analyze={analyze_duration:.2f}s, SaveAnalysis={save_analysis_duration:.2f}s")
                else:
                    failed_scrapes += 1
                    url_duration = time.time() - url_start_time
                    pipeline_logger.warning(f"[URL {i+1}/{len(urls)}] ❌ FAILED - Empty content - Duration: {url_duration:.2f}s")
            else:
                failed_scrapes += 1
                error_msg = scrape_result.get("error", "Unknown error")
                url_duration = time.time() - url_start_time
                pipeline_logger.warning(f"[URL {i+1}/{len(urls)}] ❌ FAILED - {error_msg} - Duration: {url_duration:.2f}s")
        
        stage2_duration = time.time() - stage2_start
        pipeline_logger.info(f"\n{'─'*80}")
        pipeline_logger.info(f"[STAGE 2] ✅ COMPLETED")
        pipeline_logger.info(f"[STAGE 2] Duration: {stage2_duration:.2f}s")
        pipeline_logger.info(f"[STAGE 2] Results: Success={successful_scrapes}, Failed={failed_scrapes}, Total={len(urls)}")
        pipeline_logger.info(f"[STAGE 2] Final review count: {len(accumulated_reviews)}")
        pipeline_logger.info(f"[STAGE 2] Final content length: {sum(len(r) for r in accumulated_reviews)} chars")
        pipeline_logger.info(f"{'─'*80}\n")
        
        if not accumulated_reviews:
            pipeline_logger.error(f"\n{'!'*80}")
            pipeline_logger.error(f"[PIPELINE FAILURE] No review content extracted from any scraped pages")
            pipeline_logger.error(f"{'!'*80}\n")
            await storage_service.update_processing_status(
                product_id=product_id,
                stage="scrape",
                status="failed",
                progress=0,
                current_step="No review content extracted",
                error="Failed to extract review content from scraped pages"
            )
            return
        
        await storage_service.update_processing_status(
            product_id=product_id,
            stage="analyze",
            status="completed",
            progress=100,
            current_step="Analysis complete!"
        )
        
        pipeline_duration = time.time() - pipeline_start_time
        pipeline_logger.info(f"\n{'='*80}")
        pipeline_logger.info(f"[PIPELINE END] ✅ SUCCESS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pipeline_logger.info(f"[PIPELINE END] Product ID: {product_id}")
        pipeline_logger.info(f"[PIPELINE END] Product Name: {product_name}")
        pipeline_logger.info(f"[PIPELINE END] Total Duration: {pipeline_duration:.2f}s")
        pipeline_logger.info(f"[PIPELINE END] URLs processed: {len(urls)}")
        pipeline_logger.info(f"[PIPELINE END] Reviews extracted: {len(accumulated_reviews)}")
        pipeline_logger.info(f"[PIPELINE END] Stage 1 (Serper) duration: {stage1_duration:.2f}s")
        pipeline_logger.info(f"[PIPELINE END] Stage 2 (Sequential) duration: {stage2_duration:.2f}s")
        pipeline_logger.info(f"{'='*80}\n")
        
    except Exception as e:
        pipeline_duration = time.time() - pipeline_start_time
        pipeline_logger.error(f"\n{'!'*80}")
        pipeline_logger.error(f"[PIPELINE END] ❌ FAILED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pipeline_logger.error(f"[PIPELINE END] Product ID: {product_id}")
        pipeline_logger.error(f"[PIPELINE END] Product Name: {product_name}")
        pipeline_logger.error(f"[PIPELINE END] Duration before failure: {pipeline_duration:.2f}s")
        pipeline_logger.error(f"[PIPELINE END] Error: {str(e)}")
        pipeline_logger.error(f"[PIPELINE END] Error type: {type(e).__name__}")
        pipeline_logger.error(f"{'!'*80}\n", exc_info=True)
        
        await storage_service.update_processing_status(
            product_id=product_id,
            stage="analyze",
            status="failed",
            progress=0,
            current_step=f"Error: {str(e)}",
            error=str(e)
        )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(product_data: ProductCreate):
    """
    Create a new product entry.
    """
    logger.info(f"Creating product: {product_data.product_name}")
    try:
        product_doc = await storage_service.create_product(
            product_name=product_data.product_name,
            metadata=product_data.metadata
        )
        
        logger.info(f"Product created successfully - ID: {product_doc.product_id}")
        return ProductResponse(
            product_id=product_doc.product_id,
            product_name=product_doc.product_name,
            created_at=product_doc.created_at,
            status=product_doc.status,
            metadata=product_doc.metadata
        )
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


@router.post("/{product_id}/analyze", status_code=202)
async def analyze_product(product_id: str, background_tasks: BackgroundTasks):
    """
    Start product analysis pipeline.
    Returns immediately with processing status.
    """
    logger.info(f"Analysis requested for product: {product_id}")
    
    # Check if product exists
    product = await storage_service.get_product(product_id)
    if not product:
        logger.warning(f"Product not found: {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already analyzing or completed
    if product.status == "processing":
        logger.info(f"Product {product_id} already being processed")
        return {"product_id": product_id, "status": "processing", "message": "Analysis already in progress"}
    
    if product.status == "completed":
        logger.info(f"Product {product_id} already analyzed")
        return {"product_id": product_id, "status": "completed", "message": "Analysis already completed"}
    
    # Update status to processing
    await storage_service.update_product_status(product_id, "processing")
    logger.info(f"Starting analysis pipeline for product: {product_id} ({product.product_name})")
    
    # Start background task
    background_tasks.add_task(
        analyze_product_pipeline,
        product_id=product_id,
        product_name=product.product_name
    )
    
    return {
        "product_id": product_id,
        "status": "processing",
        "message": "Analysis started"
    }


@router.get("/{product_id}", response_model=ProductAnalysisResponse)
async def get_product_analysis(product_id: str):
    """
    Get product with optional analysis.
    Returns product info even if analysis hasn't been run yet.
    """
    product = await storage_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    analysis = await storage_service.get_product_analysis(product_id)
    
    # If no analysis, return product info only
    if not analysis:
        return ProductAnalysisResponse(
            product_id=product.product_id,
            product_name=product.product_name,
            created_at=product.created_at,
            status=product.status
        )
    
    # Get review count
    reviews = await storage_service.get_raw_reviews(product_id)
    reviews_count = len(reviews)
    
    # Build response
    from app.schemas.product import (
        SentimentAnalysis, FeatureSentiment, TopAspect,
        UserSegment, QualityIssue, PriceInfo
    )
    
    # Convert analysis to response format
    sentiment = SentimentAnalysis(**analysis.sentiment) if analysis.sentiment else None
    
    def _normalize_quotes_list(quotes):
        # Accepts list[str] or list[dict]; returns list[dict{"quote": str}]
        if not quotes:
            return []
        if isinstance(quotes, list):
            if len(quotes) > 0 and isinstance(quotes[0], str):
                return [{"quote": q} for q in quotes]
            return quotes
        return []

    features = {}
    if analysis.features:
        for feature_name, feature_data in analysis.features.items():
            # Normalize quotes if model returned plain strings
            if isinstance(feature_data, dict) and "quotes" in feature_data:
                feature_data = {**feature_data, "quotes": _normalize_quotes_list(feature_data.get("quotes"))}
            # Add feature name to the data since it's required by schema
            feature_data_with_name = {**feature_data, "feature": feature_name}
            features[feature_name] = FeatureSentiment(**feature_data_with_name)
    
    top_praises = []
    if analysis.top_praises:
        for p in analysis.top_praises:
            if isinstance(p, dict) and "quotes" in p:
                p = {**p, "quotes": _normalize_quotes_list(p.get("quotes"))}
            top_praises.append(TopAspect(**p))

    top_complaints = []
    if analysis.top_complaints:
        for c in analysis.top_complaints:
            if isinstance(c, dict) and "quotes" in c:
                c = {**c, "quotes": _normalize_quotes_list(c.get("quotes"))}
            top_complaints.append(TopAspect(**c))
    user_segments = [UserSegment(**s) for s in analysis.user_segments] if analysis.user_segments else []
    quality_issues = []
    if analysis.quality_issues:
        for q in analysis.quality_issues:
            if isinstance(q, dict) and "quotes" in q:
                q = {**q, "quotes": _normalize_quotes_list(q.get("quotes"))}
            quality_issues.append(QualityIssue(**q))
    
    # Map prices: convert 'platform' to 'source' if needed
    prices = []
    if analysis.prices:
        for p in analysis.prices:
            price_data = dict(p)
            if 'platform' in price_data and 'source' not in price_data:
                price_data['source'] = price_data.pop('platform')
            prices.append(PriceInfo(**price_data))
    
    return ProductAnalysisResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        created_at=product.created_at,
        status=product.status,
        analyzed_at=analysis.analyzed_at,
        reviews_count=reviews_count,
        sentiment=sentiment,
        features=features if features else None,
        top_praises=top_praises if top_praises else None,
        top_complaints=top_complaints if top_complaints else None,
        user_segments=user_segments if user_segments else None,
        quality_issues=quality_issues if quality_issues else None,
        prices=prices if prices else None,
        competitor_mentions=analysis.competitor_mentions,
        value_analysis=analysis.value_analysis,
        summary=analysis.summary,
        general_sentiment=analysis.general_sentiment,
        pros=analysis.pros,
        cons=analysis.cons,
        description=analysis.description
    )


@router.get("", response_model=ProductListResponse)
async def get_all_products():
    """
    Get all products.
    """
    products = await storage_service.get_all_products()
    
    product_responses = [
        ProductResponse(
            product_id=p.product_id,
            product_name=p.product_name,
            created_at=p.created_at,
            status=p.status,
            metadata=p.metadata
        )
        for p in products
    ]
    
    return ProductListResponse(products=product_responses)

