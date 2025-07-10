# api/index.py
# Vercel entry point for FastAPI app

from app.main import app

# Optional: Allow running locally with `python api/index.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True) 