from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import json

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Truth Finder AI"
    app_version: str = "1.0.0"
    debug: bool = True

    # Twitter API credentials (make optional with fallbacks)
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None

    # Gemini API (make optional with fallback)
    gemini_api_key: Optional[str] = None

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    # API Settings
    max_tweets_per_request: int = 50
    default_tweets_count: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            # Custom parser for CORS origins
            if field_name == 'cors_origins':
                return [origin.strip() for origin in raw_val.split(',') if origin.strip()]
            try:
                return json.loads(raw_val)
            except Exception:
                return raw_val

# Create settings instance
settings = Settings()

DEFAULT_AGENT_INSTRUCTIONS = (
    "You are TruthFinder, an AI-powered news assistant. "
    "You specialize in summarizing, fact-checking, bias detection, investigation, and generating reports "
    "on news articles or claims. Your goal is to help people spot misinformation and make informed decisions using verified information."
)