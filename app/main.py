from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app with fallback values
app = FastAPI(
    title=os.getenv("app_name", "Truth Finder AI"),
    description="AI-powered news fact-checking API using Twitter data and Gemini AI",
    version=os.getenv("app_version", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware with fallback
cors_origins = os.getenv("cors_origins", "http://localhost:3000")
if isinstance(cors_origins, str):
    cors_origins = [cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a simple health check endpoint
@app.get("/")
def root():
    return {"message": "TruthFinder AI API is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "gemini": "available" if os.getenv("gemini_api_key") else "missing_key",
            "twitter": "available" if os.getenv("twitter_bearer_token") else "missing_key"
        }
    }

# Try to include routes, but don't crash if they fail
try:
    from app.routes import fact_check
    app.include_router(fact_check.router, prefix="/api/v1", tags=["agent"])
except Exception as e:
    print(f"Warning: Could not load routes: {e}")
    # Add a fallback route
    @app.get("/api/v1/status")
    def api_status():
        return {"message": "API is running but some routes may be unavailable"}