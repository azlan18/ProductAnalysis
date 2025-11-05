"""
Pydantic models for Gemini API structured output responses.
These models define the exact structure expected from the LLM.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class SentimentDistribution(BaseModel):
    """Sentiment distribution percentages."""
    positive: float = Field(default=0.0, ge=0, le=100)
    negative: float = Field(default=0.0, ge=0, le=100)
    neutral: float = Field(default=0.0, ge=0, le=100)


class SentimentResponse(BaseModel):
    """Sentiment analysis response."""
    score: float = Field(..., ge=0, le=10)
    sentiment: str  # positive, negative, neutral
    distribution: SentimentDistribution = Field(default_factory=SentimentDistribution)


class FeatureSentimentResponse(BaseModel):
    """Feature-level sentiment response."""
    sentiment: str  # positive, negative, neutral
    score: float = Field(..., ge=0, le=10)
    mentions: int = Field(..., ge=0)
    quotes: List[str] = Field(default_factory=list)


class TopAspectResponse(BaseModel):
    """Top aspect (praise/complaint) response."""
    aspect: str
    frequency: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)
    score: float = Field(..., ge=0, le=10)
    quotes: List[str] = Field(default_factory=list)


class UserSegmentResponse(BaseModel):
    """User segment response."""
    segment: str
    satisfaction: float = Field(..., ge=0, le=100)
    count: int = Field(..., ge=0)


class QualityIssueResponse(BaseModel):
    """Quality issue response."""
    issue: str
    frequency: int = Field(..., ge=0)
    severity: str  # high, medium, low
    quotes: List[str] = Field(default_factory=list)


class PriceInfoResponse(BaseModel):
    """Price information response."""
    source: str
    url: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None


class CompetitorMentionResponse(BaseModel):
    """Competitor mention response."""
    mentions: int = Field(..., ge=0)
    sentiment: str  # better, worse, similar
    quotes: List[str] = Field(default_factory=list)


class ValueAnalysisResponse(BaseModel):
    """Value analysis response."""
    score: float = Field(..., ge=0, le=10)
    sentiment: str
    percentage_saying_worth_it: float = Field(default=0.0, ge=0, le=100)
    better_alternatives: List[str] = Field(default_factory=list)


class SummaryResponse(BaseModel):
    """Summary response."""
    one_liner: str
    best_for: List[str] = Field(default_factory=list)
    not_recommended_for: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    verdict: str


class ProductAnalysisResponseModel(BaseModel):
    """Complete product analysis response model for Gemini structured output."""
    sentiment: SentimentResponse
    features: Dict[str, FeatureSentimentResponse] = Field(default_factory=dict)
    top_praises: List[TopAspectResponse] = Field(default_factory=list)
    top_complaints: List[TopAspectResponse] = Field(default_factory=list)
    user_segments: List[UserSegmentResponse] = Field(default_factory=list)
    quality_issues: List[QualityIssueResponse] = Field(default_factory=list)
    prices: List[PriceInfoResponse] = Field(default_factory=list)
    competitor_mentions: Dict[str, CompetitorMentionResponse] = Field(default_factory=dict)
    value_analysis: Optional[ValueAnalysisResponse] = None
    summary: SummaryResponse
    general_sentiment: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    description: str


class ProsConsResponse(BaseModel):
    """Pros and cons for a product."""
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)


class FeatureComparisonResponse(BaseModel):
    """Feature comparison response."""
    winner: str
    reasoning: str
    scores: Dict[str, float] = Field(default_factory=dict)


class VerdictByUseCaseResponse(BaseModel):
    """Verdict by use case response."""
    gaming: Optional[str] = None
    photography: Optional[str] = None
    battery_life: Optional[str] = None
    value: Optional[str] = None
    all_rounder: Optional[str] = None


class BestForDifferentUsersResponse(BaseModel):
    """Best product for different user types."""
    pass  # Dynamic keys, will be Dict[str, str]


class ComparisonSummaryResponse(BaseModel):
    """Comparison summary response."""
    recommendation: str
    best_for_different_users: Dict[str, str] = Field(default_factory=dict)
    final_verdict: str


class ProductComparisonResponseModel(BaseModel):
    """Complete product comparison response model for Gemini structured output."""
    overall_winner: str
    winner_reasoning: str
    comparison_matrix: Dict[str, Dict[str, Optional[float]]] = Field(default_factory=dict)
    pros_cons: Dict[str, ProsConsResponse] = Field(default_factory=dict)
    feature_comparison: Dict[str, FeatureComparisonResponse] = Field(default_factory=dict)
    verdict_by_use_case: VerdictByUseCaseResponse
    key_differences: List[str] = Field(default_factory=list)
    summary: ComparisonSummaryResponse

