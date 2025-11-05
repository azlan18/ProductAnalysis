"""
Pydantic schemas for product-related API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    product_name: str = Field(..., min_length=1, description="Name of the product")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class ProductResponse(BaseModel):
    """Schema for product response."""
    product_id: str
    product_name: str
    created_at: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for product list response."""
    products: list[ProductResponse]


class AnalysisStatusResponse(BaseModel):
    """Schema for analysis status response."""
    product_id: str
    stage: str
    status: str
    progress: int = Field(..., ge=0, le=100)
    current_step: str
    timestamp: datetime
    error: Optional[str] = None


class PriceInfo(BaseModel):
    """Schema for price information."""
    source: str
    url: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None


class CustomerQuote(BaseModel):
    """Schema for customer quote."""
    quote: str


class FeatureSentiment(BaseModel):
    """Schema for feature-level sentiment."""
    feature: str
    sentiment: str
    score: float = Field(..., ge=0, le=10)
    mentions: int
    quotes: list[CustomerQuote] = Field(default_factory=list)


class TopAspect(BaseModel):
    """Schema for top praises/complaints."""
    aspect: str
    frequency: int
    percentage: float
    score: float = Field(..., ge=0, le=10)
    quotes: list[CustomerQuote] = Field(default_factory=list)


class UserSegment(BaseModel):
    """Schema for user segment analysis."""
    segment: str
    satisfaction: float = Field(..., ge=0, le=100)
    count: int


class QualityIssue(BaseModel):
    """Schema for quality issues."""
    issue: str
    frequency: int
    severity: str  # high, medium, low
    quotes: list[CustomerQuote] = Field(default_factory=list)


class SentimentAnalysis(BaseModel):
    """Schema for overall sentiment."""
    score: float = Field(..., ge=0, le=10)
    sentiment: str  # positive, negative, neutral
    distribution: Dict[str, float] = Field(default_factory=dict)


class ProductAnalysisResponse(BaseModel):
    """Schema for complete product analysis response."""
    product_id: str
    product_name: str
    created_at: datetime
    status: str
    analyzed_at: Optional[datetime] = None
    reviews_count: int = 0
    sentiment: Optional[SentimentAnalysis] = None
    features: Optional[Dict[str, FeatureSentiment]] = None
    top_praises: Optional[list[TopAspect]] = None
    top_complaints: Optional[list[TopAspect]] = None
    user_segments: Optional[list[UserSegment]] = None
    quality_issues: Optional[list[QualityIssue]] = None
    prices: Optional[list[PriceInfo]] = None
    competitor_mentions: Optional[Dict[str, Any]] = None
    value_analysis: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    general_sentiment: Optional[str] = None
    pros: Optional[list[str]] = None
    cons: Optional[list[str]] = None
    description: Optional[str] = None  # Markdown formatted


class CompareRequest(BaseModel):
    """Schema for comparison request."""
    product_ids: list[str] = Field(..., min_length=2, max_length=4)


class ComparisonResponse(BaseModel):
    """Schema for comparison response."""
    comparison_id: str
    created_at: datetime
    compared_products: list[str]
    overall_winner: str
    winner_reasoning: str
    comparison_matrix: Dict[str, Dict[str, Optional[float]]]
    pros_cons: Dict[str, Dict[str, list[str]]]  # pros and cons as lists of strings
    feature_comparison: Dict[str, Any]
    verdict_by_use_case: Dict[str, str]
    key_differences: list[str]  # Simple list of strings
    summary: Dict[str, Any]

