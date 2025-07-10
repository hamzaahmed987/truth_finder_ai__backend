import logging
import os
import asyncio
from typing import List, Optional
from datetime import datetime

import tweepy
from dotenv import load_dotenv

from app.models.response_models import TwitterTweet
from app.core.config import settings

load_dotenv()
logger = logging.getLogger(__name__)


class TwitterService:
    def __init__(self):
        self.client = None
        self.is_available = False
        
        try:
            # Check if we have the required API keys
            if not all([
                settings.twitter_api_key,
                settings.twitter_api_secret,
                settings.twitter_access_token,
                settings.twitter_access_token_secret
            ]):
                logger.warning("⚠️ Twitter API keys not configured. Twitter service will be disabled.")
                return
                
            self.client = tweepy.Client(
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_token_secret,
                wait_on_rate_limit=True
            )
            self.is_available = True
            logger.info("✅ Twitter client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Twitter client: {e}")
            self.is_available = False

    async def search_tweets(self, keyword: str, max_results: int = 10) -> List[TwitterTweet]:
        """Search recent tweets containing the keyword (cleaned)."""
        if not self.is_available:
            logger.warning("⚠️ Twitter service not available. Returning empty results.")
            return []
            
        return await asyncio.to_thread(self._search_tweets_sync, keyword, max_results)

    def _search_tweets_sync(self, keyword: str, max_results: int) -> List[TwitterTweet]:
        if not self.client:
            return []
            
        try:
            query = self._clean_search_query(keyword)
            logger.info(f"🔍 Searching tweets: {query}")

            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "author_id", "public_metrics"],
                expansions=["author_id"],
                user_fields=["username", "verified"]
            )

            if not tweets.data:
                logger.info("⚠️ No tweets found.")
                return []

            users = {u.id: u for u in tweets.includes.get("users", [])}
            tweet_list = []

            for tweet in tweets.data:
                user = users.get(tweet.author_id)
                tweet_list.append(TwitterTweet(
                    id=str(tweet.id),
                    text=tweet.text,
                    author_username=user.username if user else "unknown",
                    author_id=str(tweet.author_id),
                    created_at=tweet.created_at,
                    public_metrics=tweet.public_metrics or {},
                    url=f"https://twitter.com/{user.username}/status/{tweet.id}" if user else "unknown"
                ))

            logger.info(f"✅ Found {len(tweet_list)} tweets")
            return tweet_list

        except tweepy.TooManyRequests:
            logger.error("🚫 Twitter rate limit hit")
            return []
        except tweepy.Unauthorized:
            logger.error("🔐 Twitter API unauthorized")
            return []
        except Exception as e:
            logger.error(f"❌ Twitter search error: {e}")
            return []

    async def get_tweet_by_id(self, tweet_id: str) -> Optional[TwitterTweet]:
        """Get a tweet by ID."""
        if not self.is_available:
            return None
            
        return await asyncio.to_thread(self._get_tweet_by_id_sync, tweet_id)

    def _get_tweet_by_id_sync(self, tweet_id: str) -> Optional[TwitterTweet]:
        if not self.client:
            return None
            
        try:
            response = self.client.get_tweet(
                tweet_id,
                tweet_fields=["created_at", "author_id", "public_metrics"],
                expansions=["author_id"],
                user_fields=["username"]
            )

            if not response.data:
                return None

            user = response.includes.get("users", [None])[0]
            return TwitterTweet(
                id=str(response.data.id),
                text=response.data.text,
                author_username=user.username if user else "unknown",
                author_id=str(response.data.author_id),
                created_at=response.data.created_at,
                public_metrics=response.data.public_metrics or {},
                url=f"https://twitter.com/{user.username}/status/{response.data.id}" if user else "unknown"
            )
        except Exception as e:
            logger.error(f"❌ Failed to fetch tweet {tweet_id}: {e}")
            return None

    def _clean_search_query(self, keyword: str) -> str:
        keyword = keyword.strip()
        if "lang:en" not in keyword:
            keyword += " lang:en"
        if "exclude:retweets" not in keyword:
            keyword += " -is:retweet"
        return keyword
