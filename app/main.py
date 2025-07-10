from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TruthFinder API",
    description="AI-powered news analysis and fact-checking service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "TruthFinder API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TruthFinder API"}

# Import routes with error handling
try:
    from app.routes.fact_check import router as fact_check_router
    app.include_router(fact_check_router, prefix="/api/v1", tags=["fact-check"])
except ImportError as e:
    print(f"Warning: Could not import fact_check router: {e}")
    
    @app.post("/api/v1/fact-check")
    async def fallback_fact_check():
        return JSONResponse(
            status_code=503,
            content={"error": "Fact-check service temporarily unavailable"}
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url.path)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)