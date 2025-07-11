# NOTE: Input and output guardrails are enforced at the route level (fact_check.py). This service assumes sanitized and safe input.
import os
import httpx
from dotenv import load_dotenv
from app.services.multi_agent_orchestrator import multi_agent_orchestrator

load_dotenv()

class NewsAnalyzer:
    def __init__(self):
        self.orchestrator = multi_agent_orchestrator

    async def analyze_news(self, news_text: str) -> str:
        """
        Analyze news using the multi-agent orchestrator.
        """
        try:
            result = await self.orchestrator(news_text)
            return result
        except Exception as e:
            return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing or ask about something else."

    async def fact_check(self, claim: str) -> str:
        """
        Fact-check a specific claim.
        """
        try:
            result = await self.orchestrator(f"Fact check this claim: {claim}")
            return result
        except Exception as e:
            return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing or ask about something else."

    async def summarize(self, text: str) -> str:
        """
        Summarize the given text.
        """
        try:
            result = await self.orchestrator(f"Summarize this: {text}")
            return result
        except Exception as e:
            return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing or ask about something else." 