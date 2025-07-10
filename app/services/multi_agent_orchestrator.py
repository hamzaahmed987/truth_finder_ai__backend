import os
import httpx
import json
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
print(f"[DEBUG] GEMINI_API_KEY: {os.getenv('gemini_api_key')}")
from app.services.tools import TRUTHFINDER_TOOLS

load_dotenv()
GEMINI_API_KEY = os.getenv("gemini_api_key")
print(f"[DEBUG] GEMINI_API_KEY: {GEMINI_API_KEY}")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# Add greeting keywords
GREETING_KEYWORDS = ["hello", "hi", "hey", "salaam", "assalam", "greetings"]

# ------------------------ 🔧 Sub-Agent: Fact-Checker ------------------------
async def factcheck_agent(news_text: str) -> str:
    prompt = f"""
You are a fact-checking AI agent. Analyze the following news and respond if it's real, fake, biased, or misleading. 
Also give a short reasoning for your conclusion.

News:
'''{news_text}'''

Give final verdict and explain why.
"""
    return await call_gemini_api(prompt)

# ------------------------ ✂️ Sub-Agent: Summarizer ------------------------
async def summarizer_agent(text: str) -> str:
    prompt = f"""
You are a summarizer agent. Your task is to summarize the following article or news text into a short and clear summary.

Text:
'''{text}'''

Return a 3-5 sentence summary.
"""
    return await call_gemini_api(prompt)

# ------------------------ 🔁 Utility: Gemini API Caller ------------------------
async def call_gemini_api(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(GEMINI_URL, json=payload)
            try:
                res.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"[DEBUG] Gemini API HTTP error: {e.response.status_code} {e.response.text}")
                return f"[Gemini API Error: {e.response.status_code} {e.response.text}]"
            data = res.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    except Exception as e:
        print(f"[DEBUG] Gemini API error: {e}")
        return f"[Gemini API Error: {e}]"

# Main TruthFinderAgent class
class TruthFinderAgent:
    def __init__(self, tools):
        self.tools = {getattr(tool, 'name', tool.__class__.__name__): tool for tool in tools}

    async def handle(self, user_input: str, tool_name: str = None, **kwargs):
        if tool_name and tool_name in self.tools:
            tool = self.tools[tool_name]
            return await tool(**kwargs)
        # Default: Use orchestrator logic to pick tool
        return await multi_agent_orchestrator(user_input)

# Instantiate the main agent with all tools
main_agent = TruthFinderAgent(TRUTHFINDER_TOOLS)

# Update orchestrator to use tools and allow handoff
async def multi_agent_orchestrator(user_message: str) -> str:
    # Example intent detection (expand as needed)
    if any(k in user_message.lower() for k in GREETING_KEYWORDS):
        return "Hello! 👋 I'm TruthFinder. How can I help you with news, fact-checking, or analysis today?"
    if any(k in user_message.lower() for k in ["who are you", "about you", "yourself"]):
        return (
            "I'm Truth Finder Agent, made by Hamza Ahmed. "
            "I help you fact-check news and analyze information using advanced AI and social media data. "
            "Ask me about any news, and I'll help you verify its credibility!"
        )
    elif any(k in user_message.lower() for k in ["summarize", "summary", "short version", "tl;dr"]):
        return await main_agent.handle(user_message, tool_name="summarize_news", news_text=user_message)
    elif any(k in user_message.lower() for k in ["fact check", "is it true", "verify", "real or fake"]):
        return await main_agent.handle(user_message, tool_name="fact_checker", claim=user_message)
    elif any(k in user_message.lower() for k in ["bias", "political bias", "tone", "sentiment"]):
        return await main_agent.handle(user_message, tool_name="analyze_sentiment", text=user_message)
    elif any(k in user_message.lower() for k in ["keywords", "extract", "entities"]):
        return await main_agent.handle(user_message, tool_name="extract_keywords", text=user_message)
    elif any(k in user_message.lower() for k in ["statistic", "number", "verify stat"]):
        return await main_agent.handle(user_message, tool_name="verify_stat", stat=user_message)
    elif any(k in user_message.lower() for k in ["report", "generate report", "final report"]):
        # Example: You'd need to gather summary, verdict, keywords first
        summary = await main_agent.handle(user_message, tool_name="summarize_news", news_text=user_message)
        verdict = await main_agent.handle(user_message, tool_name="fact_checker", claim=user_message)
        keywords = await main_agent.handle(user_message, tool_name="extract_keywords", text=user_message)
        return await main_agent.handle(user_message, tool_name="generate_report", summary=summary, verdict=verdict, keywords=keywords)
    elif any(k in user_message.lower() for k in ["twitter", "tweet", "social media"]):
        return await main_agent.handle(user_message, tool_name="search_twitter", keyword=user_message)
    else:
        # Fallback: Use Gemini LLM for general chat
        prompt = (
            "You are TruthFinder, an AI assistant that analyzes news, detects misinformation, summarizes content, "
            "and explains findings. You never mention Google or Gemini. Stay in character as TruthFinder.\n"
            f"User: {user_message}\nAssistant:"
        )
        return await call_gemini_api(prompt) 