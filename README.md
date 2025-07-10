# TruthFinder Backend

AI-powered news analysis and fact-checking service built with FastAPI.

## 🚀 Vercel Deployment

This backend is configured for deployment on Vercel as serverless functions.

### Prerequisites

1. **Vercel CLI** (optional but recommended):
   ```bash
   npm i -g vercel
   ```

2. **Environment Variables** - Set these in your Vercel dashboard:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `TWITTER_API_KEY` - Twitter API key (optional)
   - `TWITTER_API_SECRET` - Twitter API secret (optional)
   - `TWITTER_ACCESS_TOKEN` - Twitter access token (optional)
   - `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret (optional)
   - `TWITTER_BEARER_TOKEN` - Twitter bearer token (optional)

### Deployment Steps

1. **Deploy via Vercel Dashboard**:
   - Connect your GitHub repository to Vercel
   - Set the root directory to `backend`
   - Configure environment variables in the Vercel dashboard
   - Deploy

2. **Deploy via Vercel CLI**:
   ```bash
   cd backend
   vercel
   ```

3. **Deploy via Git**:
   ```bash
   git add .
   git commit -m "Deploy to Vercel"
   git push
   ```

### Project Structure

```
backend/
├── api/
│   └── index.py          # Vercel serverless entry point
├── app/
│   ├── core/
│   │   └── config.py     # Configuration and settings
│   ├── models/
│   │   ├── request_models.py
│   │   └── response_models.py
│   ├── routes/
│   │   └── fact_check.py # API routes
│   ├── services/
│   │   ├── gemini_service.py
│   │   ├── multi_agent_orchestrator.py
│   │   ├── news_analyzer.py
│   │   ├── tools.py
│   │   └── twitter_service.py
│   └── main.py           # FastAPI app
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to ignore in deployment
├── requirements.txt      # Python dependencies
└── README.md
```

### API Endpoints

- `GET /` - Health check
- `GET /health` - Service health status
- `POST /api/v1/agent/chat` - Chat with the AI agent
- `GET /api/v1/sessions/{session_id}` - Get chat session history

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file with your API keys.

3. **Run locally**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Test the backend**:
   ```bash
   python test_local.py
   ```

### Troubleshooting

#### Common Issues

1. **Build Errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check that `api/index.py` exists and imports correctly
   - Verify `vercel.json` configuration

2. **Runtime Errors**:
   - Check environment variables are set in Vercel dashboard
   - Review logs in Vercel dashboard
   - Test locally first with `python test_local.py`

3. **Import Errors**:
   - Ensure all imports use relative paths from `app.`
   - Check that `__init__.py` files exist in all directories

#### Environment Variables

Make sure these are set in your Vercel dashboard:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
# Optional Twitter API keys for full functionality
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
```

### Features

- ✅ FastAPI backend with async support
- ✅ Multi-agent orchestration system
- ✅ Gemini AI integration for analysis
- ✅ Twitter API integration (optional)
- ✅ Robust error handling
- ✅ Health check endpoints
- ✅ CORS support
- ✅ Input sanitization and security
- ✅ Session management
- ✅ Vercel serverless deployment ready

### Security

- Input sanitization and validation
- Prompt injection detection
- Content filtering
- Rate limiting (via Vercel)
- CORS configuration
- Error handling without information leakage
