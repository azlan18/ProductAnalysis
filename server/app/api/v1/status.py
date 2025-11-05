"""
API endpoints for processing status tracking.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.product import AnalysisStatusResponse
from app.services.storage_service import StorageService


router = APIRouter(prefix="/products", tags=["status"])

storage_service = StorageService()


@router.get("/{product_id}/status", response_model=AnalysisStatusResponse)
async def get_product_status(product_id: str):
    """
    Get real-time processing status for a product.
    """
    # Check if product exists
    product = await storage_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get latest status
    status = await storage_service.get_latest_status(product_id)
    
    if not status:
        # Return default status if no logs exist
        return AnalysisStatusResponse(
            product_id=product_id,
            stage="pending",
            status=product.status,
            progress=0,
            current_step="Waiting to start analysis",
            timestamp=product.created_at
        )
    
    return AnalysisStatusResponse(
        product_id=product_id,
        stage=status.stage,
        status=status.status,
        progress=status.progress,
        current_step=status.current_step,
        timestamp=status.timestamp,
        error=status.error
    )

