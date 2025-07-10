from fastapi import APIRouter, HTTPException, Request
from app.services.news_analyzer import NewsAnalyzer
from app.services.multi_agent_orchestrator import main_agent, multi_agent_orchestrator
import logging
import re
import uuid
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
news_analyzer = NewsAnalyzer()

# In-memory chat sessions
CHAT_SESSIONS = {}

# Identity response
IDENTITY_RESPONSE = (
    "I am TruthFinder — your AI-powered news assistant. "
    "I specialize in summarizing, fact-checking, bias detection, investigation, and generating reports "
    "on news articles or claims. My goal is to help people spot misinformation and make informed decisions using verified information."
)

# Intent keyword sets
IDENT_KEYWORDS = ["who are you", "what's your name", "tell me about yourself", "what are you", "who is truthfinder", "what is your work", "what is your purpose", "what is your goal", "what is your mission", "what is your vision", "what is your goal", "what is your mission", "what is your vision", "what is your goal", "what is your mission", "what is your vision"]
SUMMARY_KEYWORDS = ["summarize", "summary"]
FACTCHECK_KEYWORDS = ["fact check", "is it true", "verify", "real or fake"]
BIAS_KEYWORDS = ["bias", "political bias", "tone", "sentiment"]
INVESTIGATE_KEYWORDS = ["investigate", "investigation", "deep check"]
REPORT_KEYWORDS = ["report", "generate report", "final report"]
NEWS_KEYWORDS = ["news", "article", "headline", "report", "fact", "fake", "misinformation", "bias"]

BLOCKED_KEYWORDS = [
    'hate', 'violence', 'terror', 'kill', 'attack', 'explicit', 'nsfw', 'bomb', 'shoot', 'drugs', 'sex', 'porn',
]

PROMPT_INJECTION_PATTERNS = [
    r'ignore previous instructions',
    r'pretend to be',
    r'you are now',
    r'disable safety',
    r'\[.*\]',
]

def sanitize_input(text: str) -> str:
    if not text:
        return text
    text = re.sub(r'[<>"\\]', '', text)
    return text[:2000]

def contains_blocked_keywords(text: str) -> bool:
    return any(word in text.lower() for word in BLOCKED_KEYWORDS)

def contains_prompt_injection(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in PROMPT_INJECTION_PATTERNS)

def filter_output(text: str) -> str:
    return '[REDACTED: Inappropriate content detected]' if contains_blocked_keywords(text) else text

@router.post("/agent/chat")
async def chat_agent(request: Request):
    try:
        data = await request.json()
        message = sanitize_input(data.get('message', ''))
        session_id = data.get('session_id') or str(uuid.uuid4())

        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        if contains_blocked_keywords(message):
            raise HTTPException(status_code=400, detail="Inappropriate content detected.")
        if contains_prompt_injection(message):
            raise HTTPException(status_code=400, detail="Prompt injection attempt detected.")

        history = CHAT_SESSIONS.setdefault(session_id, [])
        history.append({"role": "user", "content": message})
        lower_msg = message.lower()

        # Intent routing using the new main agent/orchestrator
        try:
            if any(k in lower_msg for k in IDENT_KEYWORDS):
                agent_reply = IDENTITY_RESPONSE
            elif any(k in lower_msg for k in SUMMARY_KEYWORDS + FACTCHECK_KEYWORDS + BIAS_KEYWORDS + INVESTIGATE_KEYWORDS + REPORT_KEYWORDS + NEWS_KEYWORDS):
                agent_reply = await multi_agent_orchestrator(message)
            else:
                agent_reply = await multi_agent_orchestrator(message)
        except Exception as e:
            logger.error(f"Error in agent orchestration: {e}")
            agent_reply = "I'm experiencing technical difficulties right now. Please try again in a moment."

        history.append({"role": "agent", "content": agent_reply})
        return {"response": agent_reply, "session_id": session_id, "history": history}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat_agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")

@router.get("/health")
async def health_check():
    """Health check endpoint for the fact-check service"""
    return {"status": "healthy", "service": "fact-check"}

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get chat session history"""
    try:
        history = CHAT_SESSIONS.get(session_id, [])
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session")


