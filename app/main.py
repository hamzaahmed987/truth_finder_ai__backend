from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import fact_check

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered news fact-checking API using Twitter data and Gemini AI",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only include the agent/analyze route
app.include_router(fact_check.router, prefix="/api/v1", tags=["agent"])