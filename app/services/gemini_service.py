import google.generativeai as genai
from app.core.config import settings
from app.models.response_models import FactCheckResult, CredibilityLevel
from typing import List, Dict, Any
import logging
import re
import json
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
print(f"[DEBUG] GEMINI_API_KEY: {os.getenv('gemini_api_key')}")

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            print(f"[DEBUG] GeminiService init error: {e}")
            raise
    
    async def analyze_news_credibility(
        self, 
        news_content: str, 
        twitter_data: List[Dict[str, Any]]
    ) -> FactCheckResult:
        """
        Analyze news content credibility using Gemini AI
        """
        try:
            logger.info("Starting Gemini AI analysis")
            
            # Prepare Twitter context
            twitter_context = self._prepare_twitter_context(twitter_data)
            
            # Create comprehensive analysis prompt
            prompt = self._create_analysis_prompt(news_content, twitter_context)
            
            # Generate analysis
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("Empty response from Gemini AI")
            
            # Parse the structured response
            result = self._parse_gemini_response(response.text)
            
            logger.info(f"Gemini analysis completed. Credibility: {result.credibility_level}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini AI analysis error: {e}")
            print(f"[DEBUG] GeminiService analyze_news_credibility error: {e}")
            return self._create_error_result(str(e))
    
    def _prepare_twitter_context(self, twitter_data: List[Dict[str, Any]]) -> str:
        """
        Prepare Twitter data for analysis
        """
        if not twitter_data:
            return "No Twitter data available for analysis."
        
        context_parts = []
        for i, tweet in enumerate(twitter_data[:10], 1):  # Limit to 10 tweets
            tweet_text = tweet.get('text', '')
            author = tweet.get('author_username', 'unknown')
            metrics = tweet.get('public_metrics', {})
            
            context_parts.append(f"""
Tweet {i}:
Author: @{author}
Content: {tweet_text}
Engagement: {metrics.get('like_count', 0)} likes, {metrics.get('retweet_count', 0)} retweets
            """.strip())
        
        return "\n\n".join(context_parts)
    
    def _create_analysis_prompt(self, news_content: str, twitter_context: str) -> str:
        """
        Create a comprehensive analysis prompt for Gemini
        """
        return f"""
You are an expert fact-checker and news analyst. Analyze the following news content for credibility and truthfulness.

NEWS CONTENT TO ANALYZE:
{news_content}

RELATED SOCIAL MEDIA CONTEXT:
{twitter_context}

Please provide a comprehensive analysis in the following JSON format:

{{
    "is_fake": boolean,
    "credibility_level": "highly_credible" | "credible" | "questionable" | "likely_fake" | "fake",
    "confidence_score": number between 0 and 1,
    "reasoning": "detailed explanation of your assessment",
    "analysis_details": "comprehensive analysis including methodology",
    "key_findings": ["finding1", "finding2", "finding3"],
    "contradictions_found": ["contradiction1", "contradiction2"],
    "supporting_evidence": ["evidence1", "evidence2"]
}}

Analysis criteria:
1. Factual accuracy and verifiability
2. Source credibility and reliability
3. Logical consistency and coherence
4. Emotional manipulation or bias indicators
5. Corroboration with social media discussions
6. Timeline consistency
7. Expert consensus (if applicable)

Provide specific, actionable reasoning for your assessment. Be thorough but concise.
"""
    
    def _parse_gemini_response(self, response_text: str) -> FactCheckResult:
        """
        Parse Gemini's structured response into FactCheckResult
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                return FactCheckResult(
                    is_fake=parsed.get('is_fake', False),
                    credibility_level=CredibilityLevel(parsed.get('credibility_level', 'questionable')),
                    confidence_score=float(parsed.get('confidence_score', 0.5)),
                    reasoning=parsed.get('reasoning', 'Analysis completed'),
                    sources_checked=["Twitter Social Media", "Gemini AI Analysis"],
                    analysis_details=parsed.get('analysis_details', 'Comprehensive AI analysis performed'),
                    key_findings=parsed.get('key_findings', []),
                    contradictions_found=parsed.get('contradictions_found', []),
                    supporting_evidence=parsed.get('supporting_evidence', [])
                )
            else:
                # Fallback parsing if JSON extraction fails
                return self._fallback_parse(response_text)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using fallback parsing")
            return self._fallback_parse(response_text)
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._create_error_result(f"Parsing error: {str(e)}")
    
    def _fallback_parse(self, response_text: str) -> FactCheckResult:
        """
        Fallback parsing method for non-JSON responses
        """
        response_lower = response_text.lower()
        
        # Determine if fake
        is_fake = any(keyword in response_lower for keyword in ['fake', 'false', 'misleading', 'fabricated'])
        
        # Determine confidence
        confidence_score = 0.5
        if 'high confidence' in response_lower or 'very confident' in response_lower:
            confidence_score = 0.