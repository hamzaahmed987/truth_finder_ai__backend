# api/index.py
# Vercel entry point for FastAPI app

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app
    print("Successfully imported FastAPI app")
except Exception as e:
    print(f"Error importing app: {e}")
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"message": "Fallback API", "error": str(e)}

# Export for Vercel
handler = app 