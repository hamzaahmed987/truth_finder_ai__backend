import os
import httpx
import json
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
from app.services.tools import TRUTHFINDER_TOOLS

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


# ------------------------ 🧠 Main Orchestrator Agent ------------------------
async def truthfinder_orchestrator(user_input: str) -> str:
    instruction = """
You are 'Truth Finder Agent', created by Hamza Ahmed.

You don't answer user questions yourself. 
Instead, you decide whether the task should be handled by:
- summarizer_agent: for summarizing long news or text
- factcheck_agent: for verifying if news is real, fake, or biased

You MUST decide based on the user's message, then respond ONLY with a JSON object like:
{ "tool": "factcheck_agent", "input": "..." }

Do NOT reply with anything else. No explanation, no other text.
"""
    system_input = f"User said: '''{user_input}'''"

    payload = {
        "contents": [{"parts": [{"text": instruction + "\n" + system_input}]}]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(GEMINI_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            result = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(result)
            tool = parsed["tool"]
            tool_input = parsed["input"]

            if tool == "factcheck_agent":
                return await factcheck_agent(tool_input)
            elif tool == "summarizer_agent":
                return await summarizer_agent(tool_input)
            else:
                return "[Error: Unknown tool selected]"
    except Exception as e:
        return f"[TruthFinder Agent Error: {e}]"


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

# Example of handoff: sub-agents can call main_agent.handle(...)

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


# ------------------------ 🧪 Test (if running standalone) ------------------------
if __name__ == "__main__":
    import asyncio
    async def test():
        msg1 = "Summarize this news article about the 2024 elections in Pakistan."
        msg2 = "Is it true that Elon Musk said aliens are real?"
        print("▶️ User 1:", msg1)
        print("🤖", await multi_agent_orchestrator(msg1))
        print("\n▶️ User 2:", msg2)
        print("🤖", await multi_agent_orchestrator(msg2))
    asyncio.run(test())



















# import os
# import httpx
# from dotenv import load_dotenv
# import openai
# import re

# load_dotenv()

# # --- Sub-Agent: Fact-Checker (Gemini) ---
# async def factcheck_agent(news_text: str) -> str:
#     GEMINI_API_KEY = os.getenv("gemini_api_key")
#     if not GEMINI_API_KEY:
#         return "[Error: Gemini API key not set.]"
#     prompt = f"""
# You are a fact-checking AI specialized in detecting misinformation in news content. 
# Analyze the following news statement for accuracy, credibility, bias, and evidence.

# News:
# '''{news_text}'''

# Respond with your detailed reasoning and conclusion (real/fake/bias/misleading).
# """
#     payload = {"contents": [{"parts": [{"text": prompt}]}]}
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"
#     try:
#         async with httpx.AsyncClient() as client:
#             resp = await client.post(url, json=payload, timeout=30)
#             resp.raise_for_status()
#             data = resp.json()
#             return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
#     except Exception as e:
#         return f"[Gemini Fact-Checker Error: {e}]"

# # --- Sub-Agent: Summarizer (OpenAI) ---
# async def summarizer_agent(text: str) -> str:
#     OPENAI_API_KEY = os.getenv("openai_api_key")
#     if not OPENAI_API_KEY:
#         return "[Error: OpenAI API key not set.]"
#     openai.api_key = OPENAI_API_KEY
#     system_prompt = "You are a helpful assistant that summarizes news articles and statements."
#     try:
#         response = await openai.ChatCompletion.acreate(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Summarize this: {text}"}
#             ]
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"[OpenAI Summarizer Error: {e}]"

# # --- Sub-Agent: General Chat (OpenAI) ---
# async def general_chat_agent(user_message: str) -> str:
#     OPENAI_API_KEY = os.getenv("openai_api_key")
#     if not OPENAI_API_KEY:
#         return "[Error: OpenAI API key not set.]"
#     openai.api_key = OPENAI_API_KEY
#     system_prompt = (
#         "You are Truth Finder Agent, made by Hamza Ahmed. "
#         "You help users fact-check news and analyze information using advanced AI and social media data. "
#         "If someone asks about you, introduce yourself as Truth Finder Agent."
#     )
#     try:
#         response = await openai.ChatCompletion.acreate(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_message}
#             ]
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"[OpenAI General Chat Error: {e}]"

# # --- Intent Detection ---
# def is_fact_check_claim(message: str) -> bool:
#     # Simple heuristic: if message looks like a claim (contains a person/event and past tense)
#     claim_patterns = [
#         r"\bdied\b", r"\bdead\b", r"\bwon\b", r"\blost\b", r"\bannounced\b", r"\bdeclared\b", r"\bconfirmed\b",
#         r"\bexposed\b", r"\bviral\b", r"\bfake\b", r"\btrue\b", r"\bhoax\b", r"\bscandal\b"
#     ]
#     return any(re.search(pattern, message, re.IGNORECASE) for pattern in claim_patterns)

# def is_summary_request(message: str) -> bool:
#     return any(k in message.lower() for k in ["summarize", "summary", "short version", "tl;dr"])

# def is_about_agent(message: str) -> bool:
#     return any(k in message.lower() for k in ["who are you", "what is your name", "tell me about yourself", "about you", "yourself"])

# # --- Orchestrator ---
# async def multi_agent_orchestrator(user_message: str) -> str:
#     if is_about_agent(user_message):
#         return (
#             "I'm Truth Finder Agent, made by Hamza Ahmed. "
#             "I help you fact-check news and analyze information using advanced AI and social media data. "
#             "Ask me about any news, and I'll help you verify its credibility!"
#         )
#     elif is_summary_request(user_message):
#         return await summarizer_agent(user_message)
#     elif is_fact_check_claim(user_message):
#         return await factcheck_agent(user_message)
#     else:
#         return await general_chat_agent(user_message) 