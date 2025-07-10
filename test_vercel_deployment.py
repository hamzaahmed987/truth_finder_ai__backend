#!/usr/bin/env python3
"""
Test script to verify Vercel deployment compatibility
"""

import sys
import os

def test_imports():
    """Test if all modules can be imported successfully"""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        from app.main import app
        print("✅ app.main imported successfully")
        
        from app.core.config import settings
        print("✅ app.core.config imported successfully")
        
        from app.routes.fact_check import router
        print("✅ app.routes.fact_check imported successfully")
        
        from app.services.gemini_service import GeminiService
        print("✅ app.services.gemini_service imported successfully")
        
        from app.services.twitter_service import TwitterService
        print("✅ app.services.twitter_service imported successfully")
        
        from app.services.multi_agent_orchestrator import MultiAgentOrchestrator
        print("✅ app.services.multi_agent_orchestrator imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_endpoint():
    """Test if the API endpoint can be created"""
    print("\n🔍 Testing API endpoint creation...")
    
    try:
        from app.main import app
        
        # Test if the app has the expected endpoints
        routes = [route.path for route in app.routes]
        print(f"✅ App created with {len(routes)} routes")
        
        # Check for key endpoints
        expected_endpoints = ["/", "/health", "/api/v1/fact-check"]
        for endpoint in expected_endpoints:
            if any(endpoint in route for route in routes):
                print(f"✅ Found endpoint: {endpoint}")
            else:
                print(f"⚠️  Missing endpoint: {endpoint}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test error: {e}")
        return False

def test_services():
    """Test if services can be initialized"""
    print("\n🔍 Testing service initialization...")
    
    try:
        # Test Gemini service
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        print("✅ GeminiService initialized")
        
        # Test Twitter service
        from app.services.twitter_service import TwitterService
        twitter_service = TwitterService()
        print("✅ TwitterService initialized")
        
        # Test Multi-Agent Orchestrator
        from app.services.multi_agent_orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator()
        print("✅ MultiAgentOrchestrator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Vercel deployment compatibility tests...\n")
    
    tests = [
        test_imports,
        test_api_endpoint,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend should deploy successfully on Vercel.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 