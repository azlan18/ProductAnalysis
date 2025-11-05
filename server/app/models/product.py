"""
Beanie database models for MongoDB collections.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from beanie import Document, Indexed
from pydantic import Field


class Product(Document):
    """Product model."""
    
    product_id: Indexed(str, unique=True)
    product_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, processing, completed, failed
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_stats: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "products"
        indexes = [
            "product_id",
            "created_at",
            "status"
        ]


class RawReview(Document):
    """Raw review model."""
    
    product_id: Indexed(str)
    source_url: str
    source_platform: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: str
    firecrawl_metadata: Dict[str, Any] = Field(default_factory=dict)
    domain: str = ""
    
    class Settings:
        name = "raw_reviews"
        indexes = [
            "product_id",
            "source_platform"
        ]


class AnalysisResult(Document):
    """Analysis result model."""
    
    product_id: Indexed(str, unique=True)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Sentiment data
    sentiment: Dict[str, Any] = Field(default_factory=dict)
    
    # Features
    features: Dict[str, Any] = Field(default_factory=dict)
    
    # Top praises and complaints
    top_praises: List[Dict[str, Any]] = Field(default_factory=list)
    top_complaints: List[Dict[str, Any]] = Field(default_factory=list)
    
    # User segments
    user_segments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Quality issues
    quality_issues: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Prices
    prices: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Competitor mentions
    competitor_mentions: Optional[Dict[str, Any]] = None
    
    # Value analysis
    value_analysis: Optional[Dict[str, Any]] = None
    
    # Summary
    summary: Dict[str, Any] = Field(default_factory=dict)
    general_sentiment: str = ""
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    description: str = ""
    
    class Settings:
        name = "analysis_results"
        indexes = [
            "product_id",
            "analyzed_at"
        ]


class ProcessingLog(Document):
    """Processing log model."""
    
    product_id: Indexed(str)
    stage: str  # search, scrape, analyze
    status: str  # in_progress, completed, failed
    progress: int = Field(ge=0, le=100)
    current_step: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    
    class Settings:
        name = "processing_logs"
        indexes = [
            [("product_id", 1), ("timestamp", -1)]
        ]


class Comparison(Document):
    """Comparison model."""
    
    comparison_id: Indexed(str, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    compared_products: List[str]
    
    # Comparison results
    overall_winner: str = ""
    winner_reasoning: str = ""
    comparison_matrix: Dict[str, Any] = Field(default_factory=dict)
    pros_cons: Dict[str, Any] = Field(default_factory=dict)
    feature_comparison: Dict[str, Any] = Field(default_factory=dict)
    verdict_by_use_case: Dict[str, Any] = Field(default_factory=dict)
    key_differences: List[str] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "comparisons"
        indexes = [
            "comparison_id",
            "created_at",
            "compared_products"
        ]
