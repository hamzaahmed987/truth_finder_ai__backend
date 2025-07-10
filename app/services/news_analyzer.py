# NOTE: Input and output guardrails are enforced at the route level (fact_check.py). This service assumes sanitized and safe input.
import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
print(f"[DEBUG] GEMINI_API_KEY: {os.getenv('gemini_api_key')}")

class DummyService:
    async def search_tweets(self, keyword, max_results):
        return []
    async def analyze_news_credibility(self, content, sources):
        return {}

class NewsAnalyzer:
    def __init__(self):
        self.twitter_bearer_token = os.getenv('twitter_bearer_token')
        self.gemini_api_key = os.getenv('gemini_api_key')
        self.twitter_service = DummyService()
        self.gemini_service = DummyService()

    async def fetch_tweets(self, keyword, max_results=10):
        if not self.twitter_bearer_token:
            return []
        url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results={min(max_results, 100)}&tweet.fields=created_at,author_id,public_metrics"
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                tweets = []
                for t in data.get('data', []):
                    tweets.append({
                        'id': t['id'],
                        'text': t['text'],
                        'author_id': t['author_id'],
                        'created_at': t['created_at'],
                        'public_metrics': t.get('public_metrics', {}),
                        'author_username': 'unknown',  # You can fetch user info if needed
                        'url': f"https://twitter.com/i/web/status/{t['id']}"
                    })
                return tweets
            except Exception as e:
                print(f"Twitter API error: {e}")
                return []

    async def call_gemini(self, content, tweets=None):
        if not self.gemini_api_key:
            print("[DEBUG] Gemini API key missing in NewsAnalyzer.call_gemini")
            return {'analysis': 'No Gemini API key provided.', 'confidence': 0.0, 'verdict': 'UNKNOWN'}
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key=" + self.gemini_api_key
        prompt = f"Fact-check the following news content.\nContent: {content}\n"
        if tweets:
            prompt += f"Related tweets: {tweets}\n"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                # Parse Gemini response
                text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return {'analysis': text, 'confidence': 0.8, 'verdict': 'ANALYZED'}
            except Exception as e:
                print(f"[DEBUG] NewsAnalyzer.call_gemini Gemini API error: {e}")
                return {'analysis': f'Gemini API error: {e}', 'confidence': 0.0, 'verdict': 'ERROR'}

    async def analyze_news(self, news_text=None, news_url=None, twitter_keyword=None, max_tweets=10):
        content = news_text or news_url or ''
        tweets = []
        if twitter_keyword:
            tweets = await self.fetch_tweets(twitter_keyword, max_tweets)
        gemini_result = await self.call_gemini(content, tweets=[t['text'] for t in tweets])
        # Compose response as a dictionary matching NewsAnalysisResponse
        return {
            'success': True,
            'message': 'Analysis complete',
            'original_content': content,
            'content_summary': '',
            'twitter_data': tweets,
            'fact_check_result': {
                'is_fake': False,
                'credibility_level': 'credible',
                'confidence_score': gemini_result.get('confidence', 0.8),
                'reasoning': gemini_result.get('analysis', ''),
                'sources_checked': [],
                'analysis_details': gemini_result.get('analysis', ''),
                'key_findings': [],
                'contradictions_found': [],
                'supporting_evidence': []
            },
            'metrics': {
                'processing_time': 0.5,
                'tweets_analyzed': len(tweets),
                'sources_consulted': 0,
                'api_calls_made': 2
            },
            'timestamp': datetime.utcnow().isoformat()
        } 