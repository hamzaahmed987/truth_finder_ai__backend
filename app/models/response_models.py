from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CredibilityLevel(str, Enum):
    HIGHLY_CREDIBLE = "highly_credible"
    CREDIBLE = "credible"
    QUESTIONABLE = "questionable"
    LIKELY_FAKE = "likely_fake"
    FAKE = "fake"

class TwitterTweet(BaseModel):
    id: str
    text: str
    author_username: str
    author_id: str
    created_at: datetime
    public_metrics: Dict[str, int]
    url: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FactCheckResult(BaseModel):
    is_fake: bool = Field(description="Whether the news is determined to be fake")
    credibility_level: CredibilityLevel = Field(description="Overall credibility assessment")
    confidence_score: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Confidence score between 0 and 1"
    )
    reasoning: str = Field(description="Detailed reasoning for the assessment")
    sources_checked: List[str] = Field(description="List of sources used in analysis")
    analysis_details: str = Field(description="Comprehensive analysis details")
    key_findings: List[str] = Field(
        default=[], 
        description="Key findings from the analysis"
    )
    contradictions_found: List[str] = Field(
        default=[], 
        description="Contradictions found in the content"
    )
    supporting_evidence: List[str] = Field(
        default=[], 
        description="Evidence supporting the content"
    )

class AnalysisMetrics(BaseModel):
    processing_time: float = Field(description="Time taken for analysis in seconds")
    tweets_analyzed: int = Field(description="Number of tweets analyzed")
    sources_consulted: int = Field(description="Number of sources consulted")
    api_calls_made: int = Field(description="Number of API calls made")

class NewsAnalysisResponse(BaseModel):
    success: bool = Field(description="Whether the analysis was successful")
    message: str = Field(description="Status message")
    original_content: str = Field(description="Original content that was analyzed")
    content_summary: Optional[str] = Field(
        None, 
        description="Summary of the content analyzed"
    )
    twitter_data: List[TwitterTweet] = Field(
        default=[], 
        description="Twitter data used in analysis"
    )
    fact_check_result: FactCheckResult = Field(description="Fact-checking results")
    metrics: AnalysisMetrics = Field(description="Analysis metrics")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the analysis"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }