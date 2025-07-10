import re
import httpx
from typing import Optional, List
import logging
from bs4 import BeautifulSoup
import asyncio
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

async def extract_text_from_url(url: str) -> Optional[str]:
    """
    Extract text content from a URL
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text from common news article elements
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '.main-content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text()
                    break
            
            # Fallback to body if no specific content found
            if not content:
                content = soup.body.get_text() if soup.body else soup.get_text()
            
            # Clean up the text
            content = clean_text(content)
            
            # Limit content length
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            return content
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching URL {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from URL {url}: {e}")
        return None

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-"]', '', text)
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'([.,!?;:]){2,}', r'\1', text)
    
    # Strip and return
    return text.strip()

def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Create a simple summary of the text
    """
    if not text:
        return ""
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Take first few sentences that fit within max_length
    summary = ""
    for sentence in sentences:
        if len(summary + sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip()

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text for search purposes
    """
    if not text:
        return []
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in keywords[:max_keywords]]

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_confidence_score(score: float) -> str:
    """
    Format confidence score for display
    """
    if score >= 0.8:
        return f"High ({score:.1%})"
    elif score >= 0.6:
        return f"Medium ({score:.1%})"
    elif score >= 0.4:
        return f"Low ({score:.1%})"
    else:
        return f"Very Low ({score:.1%})"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def calculate_engagement_score(metrics: dict) -> float:
    """
    Calculate engagement score from social media metrics
    """
    likes = metrics.get('like_count', 0)
    retweets = metrics.get('retweet_count', 0)
    replies = metrics.get('reply_count', 0)
    quotes = metrics.get('quote_count', 0)
    
    # Weighted engagement score
    score = (likes * 1) + (retweets * 3) + (replies * 2) + (quotes * 2)
    return score

def detect_language(text: str) -> str:
    """
    Simple language detection (basic implementation)
    """
    # This is a very basic implementation
    # In production, you might want to use a proper language detection library
    english_words = {'the', 'and', 'or', 'is', 'are', 'was', 'were', 'have', 'has'}
    words = text.lower().split()
    english_count = sum(1 for word in words if word in english_words)
    
    if len(words) > 0 and english_count / len(words) > 0.1:
        return 'en'
    else:
        return 'unknown'

async def batch_process(items: List, batch_size: int = 5):
    """
    Process items in batches to avoid overwhelming APIs
    """
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        # Process batch here
        results.extend(batch)
        
        # Small delay between batches
        if i + batch_size < len(items):
            await asyncio.sleep(0.1)
    
    return results

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent issues
    """
    if not text:
        return ""
    
    # Remove potential harmful characters
    text = re.sub(r'[<>{}[\]\\]', '', text)
    
    # Limit length
    if len(text) > 5000:
        text = text[:5000]
    
    return text.strip()