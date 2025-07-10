from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TruthFinder AI API",
    description="AI-powered news fact-checking API using Twitter data and Gemini AI",
    version="1.0.0"
)

# Pydantic schemas
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    history: List[Dict[str, str]]

class NewsAnalysisRequest(BaseModel):
    news_text: Optional[str] = None
    news_url: Optional[str] = None
    twitter_keyword: Optional[str] = None
    max_tweets: int = 10

class NewsAnalysisResponse(BaseModel):
    success: bool
    message: str
    original_content: str
    content_summary: str
    twitter_data: List[Dict[str, Any]]
    fact_check_result: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: str

# Import your main app logic
try:
    from app.main import app as main_app
    from app.routes.fact_check import chat_agent
    from app.services.news_analyzer import NewsAnalyzer
    
    # Initialize services
    news_analyzer = NewsAnalyzer()
    
    # Root endpoint
    @app.get("/")
    def root():
        return {"message": "TruthFinder AI API is working!", "status": "healthy"}
    
    # Health check
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "services": {"gemini": "available", "twitter": "available"}}
    
    # Chat endpoint
    @app.post("/api/v1/agent/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        try:
            # Use your existing chat logic
            from fastapi import Request
            mock_request = Request(scope={"type": "http", "method": "POST"})
            mock_request._json = {"message": request.message, "session_id": request.session_id}
            
            result = await chat_agent(mock_request)
            return ChatResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    
    # News analysis endpoint
    @app.post("/api/v1/news/analyze", response_model=NewsAnalysisResponse)
    async def analyze_news(request: NewsAnalysisRequest):
        try:
            result = await news_analyzer.analyze_news(
                news_text=request.news_text,
                news_url=request.news_url,
                twitter_keyword=request.twitter_keyword,
                max_tweets=request.max_tweets
            )
            return NewsAnalysisResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
    
    # API documentation
    @app.get("/docs")
    def get_docs():
        return {"message": "Visit /docs for interactive API documentation"}

except ImportError as e:
    # Fallback if imports fail
    @app.get("/")
    def root():
        return {"message": "TruthFinder AI API is working!", "note": "Some services may be unavailable"}
    
    @app.get("/health")
    def health_check():
        return {"status": "degraded", "error": "Service imports failed"}

# Export for Vercel
handler = app 