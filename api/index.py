# api/index.py
# Vercel entry point for FastAPI app

from app.main import app

# Export for Vercel
handler = app 