from fastapi import Depends, HTTPException, status
from app.core.config import settings

async def verify_api_key(api_key: str = None):
    """
    Dependency to verify API key (if you want to add authentication later)
    """
    # For now, just return True
    # You can implement API key verification here
    return True

async def get_settings():
    """
    Dependency to get application settings
    """
    return settings