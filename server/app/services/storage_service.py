"""
Service for MongoDB database operations using Beanie ODM.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
from app.models.product import Product, RawReview, AnalysisResult, ProcessingLog, Comparison
from app.utils.helpers import generate_product_id


class StorageService:
    """Service for database operations."""
    
    async def create_product(self, product_name: str, metadata: Optional[Dict[str, Any]] = None) -> Product:
        """
        Create a new product entry in MongoDB.
        
        Args:
            product_name: Name of the product
            metadata: Optional metadata dictionary
            
        Returns:
            Created product document
        """
        product_id = generate_product_id(product_name)
        
        # Check if product already exists
        existing = await Product.find_one(Product.product_id == product_id)
        if existing:
            return existing
        
        product = Product(
            product_id=product_id,
            product_name=product_name,
            created_at=datetime.utcnow(),
            status="pending",
            metadata=metadata or {},
            processing_stats={}
        )
        
        await product.insert()
        return product
    
    async def save_raw_reviews(self, product_id: str, reviews_data: List[Dict[str, Any]]) -> int:
        """
        Save raw scraped reviews to MongoDB.
        
        Args:
            product_id: Product ID
            reviews_data: List of review dictionaries from Firecrawl
            
        Returns:
            Number of reviews saved
        """
        saved_count = 0
        reviews_to_insert = []
        
        for review_data in reviews_data:
            if not review_data.get("success") or not review_data.get("content"):
                continue
            
            review = RawReview(
                product_id=product_id,
                source_url=review_data.get("url", ""),
                source_platform=review_data.get("platform", "unknown"),
                scraped_at=datetime.utcnow(),
                raw_data=review_data.get("content", ""),
                firecrawl_metadata=review_data.get("metadata", {}),
                domain=review_data.get("domain", "unknown")
            )
            
            reviews_to_insert.append(review)
            saved_count += 1
        
        if reviews_to_insert:
            await RawReview.insert_many(reviews_to_insert)
        
        return saved_count
    
    async def save_analysis_results(self, product_id: str, analysis_result: Dict[str, Any]) -> bool:
        """
        Save LLM analysis results to MongoDB.
        
        Args:
            product_id: Product ID
            analysis_result: Analysis dictionary from GPT
            
        Returns:
            True if successful
        """
        # Check if analysis already exists
        existing = await AnalysisResult.find_one(AnalysisResult.product_id == product_id)
        
        if existing:
            # Update existing
            for key, value in analysis_result.items():
                setattr(existing, key, value)
            existing.analyzed_at = datetime.utcnow()
            await existing.save()
        else:
            # Create new
            analysis = AnalysisResult(
                product_id=product_id,
                analyzed_at=datetime.utcnow(),
                **analysis_result
            )
            await analysis.insert()
        
        # Update product status
        product = await Product.find_one(Product.product_id == product_id)
        if product:
            product.status = "completed"
            await product.save()
        
        return True
    
    async def get_product_analysis(self, product_id: str) -> Optional[AnalysisResult]:
        """
        Get complete product analysis from MongoDB.
        
        Args:
            product_id: Product ID
            
        Returns:
            Analysis document or None
        """
        return await AnalysisResult.find_one(AnalysisResult.product_id == product_id)
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """
        Get product document from MongoDB.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product document or None
        """
        return await Product.find_one(Product.product_id == product_id)
    
    async def get_all_products(self) -> List[Product]:
        """
        Get all products from MongoDB.
        
        Returns:
            List of product documents
        """
        return await Product.find_all().sort(-Product.created_at).to_list()
    
    async def get_raw_reviews(self, product_id: str) -> List[RawReview]:
        """
        Get raw reviews for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            List of review documents
        """
        return await RawReview.find(RawReview.product_id == product_id).to_list()
    
    async def update_processing_status(
        self,
        product_id: str,
        stage: str,
        status: str,
        progress: int,
        current_step: str,
        error: Optional[str] = None
    ) -> bool:
        """
        Log processing status for real-time tracking.
        
        Args:
            product_id: Product ID
            stage: Current stage (search, scrape, analyze)
            status: Status (in_progress, completed, failed)
            progress: Progress percentage (0-100)
            current_step: Human-readable description
            error: Error message if failed
            
        Returns:
            True if successful
        """
        log = ProcessingLog(
            product_id=product_id,
            stage=stage,
            status=status,
            progress=progress,
            current_step=current_step,
            timestamp=datetime.utcnow(),
            error=error
        )
        
        await log.insert()
        
        # Update product status if needed
        if status in ["completed", "failed"]:
            product = await Product.find_one(Product.product_id == product_id)
            if product:
                product.status = status
                await product.save()
        
        return True
    
    async def get_latest_status(self, product_id: str) -> Optional[ProcessingLog]:
        """
        Get latest processing status for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Latest status document or None
        """
        logs = await ProcessingLog.find(
            ProcessingLog.product_id == product_id
        ).sort(-ProcessingLog.timestamp).limit(1).to_list()
        return logs[0] if logs else None
    
    async def save_comparison(self, comparison_result: Dict[str, Any]) -> str:
        """
        Save comparison results to MongoDB.
        
        Args:
            comparison_result: Comparison dictionary from GPT
            
        Returns:
            Comparison ID
        """
        comparison_id = str(ObjectId())
        
        comparison = Comparison(
            comparison_id=comparison_id,
            created_at=datetime.utcnow(),
            **comparison_result
        )
        
        await comparison.insert()
        return comparison_id
    
    async def get_comparison(self, comparison_id: str) -> Optional[Comparison]:
        """
        Get comparison document from MongoDB.
        
        Args:
            comparison_id: Comparison ID
            
        Returns:
            Comparison document or None
        """
        return await Comparison.find_one(Comparison.comparison_id == comparison_id)
    
    async def update_product_status(self, product_id: str, status: str) -> bool:
        """
        Update product status.
        
        Args:
            product_id: Product ID
            status: New status
            
        Returns:
            True if successful
        """
        product = await Product.find_one(Product.product_id == product_id)
        if product:
            product.status = status
            await product.save()
            return True
        return False
