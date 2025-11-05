"""
API endpoints for product comparison.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.product import CompareRequest, ComparisonResponse
from app.services.storage_service import StorageService
from app.services.gemini_service import GeminiService


router = APIRouter(prefix="/compare", tags=["compare"])

storage_service = StorageService()
gpt_service = GeminiService()


@router.post("", response_model=ComparisonResponse, status_code=201)
async def compare_products(request: CompareRequest):
    """
    Compare 2-4 products.
    """
    product_ids = request.product_ids
    
    if len(product_ids) < 2 or len(product_ids) > 4:
        raise HTTPException(
            status_code=400,
            detail="Please select between 2 and 4 products to compare"
        )
    
    # Fetch all products and their analyses
    products_data = []
    product_names = {}
    
    for product_id in product_ids:
        product = await storage_service.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )
        
        analysis = await storage_service.get_product_analysis(product_id)
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis not found for product {product_id}. Please analyze the product first."
            )
        
        product_names[product_id] = product.product_name
        
        # Prepare product data for comparison
        products_data.append({
            "product_id": product_id,
            "product_name": product.product_name,
            "sentiment": analysis.sentiment if analysis.sentiment else {},
            "features": analysis.features if analysis.features else {},
            "top_praises": analysis.top_praises if analysis.top_praises else [],
            "top_complaints": analysis.top_complaints if analysis.top_complaints else [],
            "summary": analysis.summary if analysis.summary else {},
            "pros": analysis.pros if analysis.pros else [],
            "cons": analysis.cons if analysis.cons else []
        })
    
    # Call GPT for comparison
    try:
        comparison_result = await gpt_service.compare_products(products_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing products: {str(e)}"
        )
    
    # Add product IDs to comparison result
    comparison_result["compared_products"] = product_ids
    
    # Transform key_differences if it comes as dictionaries instead of strings
    if "key_differences" in comparison_result:
        key_diffs = comparison_result["key_differences"]
        if key_diffs and isinstance(key_diffs[0], dict):
            # Extract just the difference text from dictionaries
            comparison_result["key_differences"] = [
                diff.get("difference", str(diff)) if isinstance(diff, dict) else diff
                for diff in key_diffs
            ]
    
    # Transform pros_cons if quotes come as objects instead of strings
    if "pros_cons" in comparison_result:
        pros_cons = comparison_result["pros_cons"]
        for product_id, product_data in pros_cons.items():
            if isinstance(product_data, dict):
                for key in ["pros", "cons"]:
                    if key in product_data and product_data[key]:
                        if isinstance(product_data[key][0], dict):
                            # Extract quote strings from objects
                            product_data[key] = [
                                item.get("quote", str(item)) if isinstance(item, dict) else item
                                for item in product_data[key]
                            ]
    
    # Transform feature_comparison quotes if needed
    if "feature_comparison" in comparison_result:
        feature_comp = comparison_result["feature_comparison"]
        for feature_name, feature_data in feature_comp.items():
            if isinstance(feature_data, dict) and "quotes" in feature_data:
                quotes = feature_data["quotes"]
                if quotes and isinstance(quotes[0], dict):
                    feature_data["quotes"] = [
                        q.get("quote", str(q)) if isinstance(q, dict) else q
                        for q in quotes
                    ]
    
    # Save comparison to database
    comparison_id = await storage_service.save_comparison(comparison_result)
    
    # Fetch the saved comparison to get created_at
    saved_comparison = await storage_service.get_comparison(comparison_id)
    
    # Clean comparison_matrix to replace None values with 0.0
    comparison_matrix = comparison_result.get("comparison_matrix", {})
    cleaned_matrix = {}
    for feature, products in comparison_matrix.items():
        cleaned_matrix[feature] = {
            product_id: (score if score is not None else 0.0)
            for product_id, score in products.items()
        }
    
    # Build response
    return ComparisonResponse(
        comparison_id=comparison_id,
        created_at=saved_comparison.created_at,
        compared_products=product_ids,
        overall_winner=comparison_result.get("overall_winner", product_ids[0]),
        winner_reasoning=comparison_result.get("winner_reasoning", ""),
        comparison_matrix=cleaned_matrix,
        pros_cons=comparison_result.get("pros_cons", {}),
        feature_comparison=comparison_result.get("feature_comparison", {}),
        verdict_by_use_case=comparison_result.get("verdict_by_use_case", {}),
        key_differences=comparison_result.get("key_differences", []),
        summary=comparison_result.get("summary", {})
    )


@router.get("/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison(comparison_id: str):
    """
    Get saved comparison by ID.
    """
    comparison = await storage_service.get_comparison(comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    # Clean comparison_matrix to replace None values with 0.0
    comparison_matrix = comparison.comparison_matrix or {}
    cleaned_matrix = {}
    for feature, products in comparison_matrix.items():
        cleaned_matrix[feature] = {
            product_id: (score if score is not None else 0.0)
            for product_id, score in products.items()
        }
    
    return ComparisonResponse(
        comparison_id=comparison.comparison_id,
        created_at=comparison.created_at,
        compared_products=comparison.compared_products,
        overall_winner=comparison.overall_winner,
        winner_reasoning=comparison.winner_reasoning,
        comparison_matrix=cleaned_matrix,
        pros_cons=comparison.pros_cons,
        feature_comparison=comparison.feature_comparison,
        verdict_by_use_case=comparison.verdict_by_use_case,
        key_differences=comparison.key_differences,
        summary=comparison.summary
    )

