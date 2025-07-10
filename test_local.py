#!/usr/bin/env python3
"""
Simple test script to verify the backend works locally
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_backend():
    """Test the backend components"""
    print("🧪 Testing TruthFinder Backend...")
    
    try:
        # Test 1: Import main app
        print("1. Testing app imports...")
        from app.main import app
        print("   ✅ FastAPI app imported successfully")
        
        # Test 2: Test config
        print("2. Testing configuration...")
        from app.core.config import settings
        print(f"   ✅ Config loaded: {settings.app_name}")
        
        # Test 3: Test services
        print("3. Testing services...")
        from app.services.news_analyzer import NewsAnalyzer
        analyzer = NewsAnalyzer()
        print("   ✅ NewsAnalyzer initialized")
        
        from app.services.twitter_service import TwitterService
        twitter = TwitterService()
        print(f"   ✅ TwitterService initialized (available: {twitter.is_available})")
        
        from app.services.gemini_service import GeminiService
        gemini = GeminiService()
        print(f"   ✅ GeminiService initialized (available: {gemini.is_available})")
        
        # Test 4: Test orchestrator
        print("4. Testing orchestrator...")
        from app.services.multi_agent_orchestrator import multi_agent_orchestrator
        result = await multi_agent_orchestrator("Hello, who are you?")
        print(f"   ✅ Orchestrator test: {result[:100]}...")
        
        print("\n🎉 All tests passed! Backend is ready for Vercel deployment.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1) 