from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class NewsCheckRequest(BaseModel):
    news_text: Optional[str] = Field(
        None, 
        description="Direct news text to check",
        max_length=5000
    )
    news_url: Optional[str] = Field(
        None, 
        description="URL of news article"
    )
    twitter_keyword: Optional[str] = Field(
        None, 
        description="Keyword to search on Twitter",
        max_length=100
    )
    max_tweets: Optional[int] = Field(
        10, 
        ge=1, 
        le=50, 
        description="Maximum number of tweets to fetch"
    )
    
    @validator('news_url')
    def validate_url(cls, v):
        if v is not None:
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(v):
                raise ValueError('Invalid URL format')
        return v
    
    @validator('twitter_keyword')
    def validate_keyword(cls, v):
        if v is not None:
            # Remove special characters that might cause issues
            v = re.sub(r'[^\w\s#@]', '', v)
            if len(v.strip()) == 0:
                raise ValueError('Keyword cannot be empty after sanitization')
        return v

class TwitterSearchRequest(BaseModel):
    keyword: str = Field(..., description="Keyword to search on Twitter")
    max_results: int = Field(
        10, 
        ge=1, 
        le=100, 
        description="Maximum number of tweets to fetch"
    )