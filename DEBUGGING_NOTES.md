# Vercel Deployment Debugging Notes

## Current Status

The application is deployed to Vercel at `https://past-news.vercel.app` but **all API endpoints are returning `FUNCTION_INVOCATION_FAILED` errors** (500 status code).

## Problem Summary

Integration tests are failing because the deployed Vercel serverless functions cannot be invoked. Even the simplest possible Python handlers fail with the same error.

## Tests Status

- **Unit tests**: ✅ All passing (91 tests)
  - `test_article_selector.py`: 27 tests passed
  - `test_date_calculator.py`: 18 tests passed
  - `test_guardian_client.py`: 11 tests passed
  - `test_news_cache.py`: 22 tests passed

- **Integration tests**: ❌ All failing (12 tests)
  - All tests receive HTTP 500 errors with `FUNCTION_INVOCATION_FAILED` message
  - Tests expect responses from `/api/index?option=...`

## What We've Tried

### 1. Fixed Initial Configuration Issues ✅

**Commit:** `8b1a3d8` - "Fix Vercel serverless function deployment issues"

Fixed three problems:
- Removed `-e .` from requirements.txt (editable install doesn't work on Vercel)
- Fixed vercel.json route pattern: changed `/(.*)`  to `/((?!api).*)` to exclude API routes from frontend rewrites
- Removed invalid `handler(request, response)` function from api/index.py

### 2. Tried Including Source Dependencies ❌

**Commit:** `3118b9a` - "Add functions configuration to include src directory"

Added to vercel.json:
```json
"functions": {
  "api/**/*.py": {
    "includeFiles": "src/**"
  }
}
```

**Result:** Still failed with `FUNCTION_INVOCATION_FAILED`

### 3. Restructured to Copy Dependencies Locally ❌

**Commit:** `bf74ff6` - "Restructure api directory to include all dependencies locally"

- Copied all files from `src/` into `api/` directory
- Changed imports from `from src.module` to `from module`
- Files copied:
  - `article_selector.py`
  - `date_calculator.py`
  - `guardian_client.py`
  - `news_cache.py`
  - `__init__.py`

**Result:** Still failed with `FUNCTION_INVOCATION_FAILED`

### 4. Created Test Endpoints ❌

Created multiple test endpoints to isolate the issue:

**api/test.py** - Minimal Flask app:
```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/', methods=['GET'])
def test():
    return jsonify({'status': 'ok', 'message': 'Vercel Python function is working!'})
```
**Result:** Failed

**api/hello.py** - Basic WSGI handler:
```python
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status": "ok", "message": "Python is working!"}'
    }
```
**Result:** Failed

**api/simple.py** - BaseHTTPRequestHandler (recommended by Vercel docs):
```python
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok", "message": "Python runtime is working!"}')
        return
```
**Result:** Failed

**api/nodeps.py** - Zero external dependencies:
```python
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"status": "ok"})
        self.wfile.write(response.encode('utf-8'))
        return
```
**Result:** Not yet tested

## Current File Structure

```
past_news/
├── api/
│   ├── __init__.py
│   ├── index.py (main Flask endpoint)
│   ├── article_selector.py
│   ├── date_calculator.py
│   ├── guardian_client.py
│   ├── news_cache.py
│   ├── test.py (test endpoint)
│   ├── hello.py (test endpoint)
│   ├── simple.py (test endpoint)
│   └── nodeps.py (test endpoint)
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── src/ (original source code, still exists)
├── tests/
├── requirements.txt
├── pyproject.toml
└── vercel.json
```

## Current Configuration Files

### requirements.txt
```
requests>=2.31.0
python-dateutil>=2.8.2
flask>=3.0.0
```

### vercel.json
```json
{
  "rewrites": [
    { "source": "/", "destination": "/frontend/index.html" },
    { "source": "/((?!api).*)", "destination": "/frontend/$1" }
  ]
}
```

### pyproject.toml (relevant sections)
```toml
[project]
name = "past-news"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "python-dateutil>=2.8.2",
    "flask>=3.0.0",
]
```

## Key Findings from Documentation

According to [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python):

1. **Python Version**: Vercel uses Python 3.12 (cannot be changed)
2. **Entry Point**: Vercel looks for either:
   - A `handler` class inheriting from `BaseHTTPRequestHandler`, OR
   - An `app` variable exposing a WSGI/ASGI application
3. **File Locations**: Supported locations include `api/*.py`

According to [Flask on Vercel Documentation](https://vercel.com/docs/frameworks/backend/flask):

1. **Entrypoint files**: `app.py`, `index.py`, `server.py`, or in subdirectories like `src/`, `app/`
2. **App export**: Must have `app = Flask(__name__)` variable
3. **Deployment**: Flask apps become a single Vercel Function

## Possible Root Causes (Unresolved)

1. **Environment Variables**: The `GUARDIAN_API_KEY` might not be set in Vercel environment
   - This could cause internal server errors
   - Need to verify via Vercel dashboard

2. **Python Version Mismatch**: Local environment uses Python 3.13.2, but Vercel uses 3.12
   - pyproject.toml says `>=3.12` which should be compatible
   - May need to explicitly set Python version

3. **Dependency Installation Failure**: Requirements might not be installing correctly
   - No build logs visible without Vercel CLI
   - Could be issue with pyproject.toml vs requirements.txt

4. **Function Size Limit**: Bundle might exceed 250MB limit
   - Unlikely given simple codebase size
   - Could check with excludeFiles configuration

5. **Missing Vercel CLI**: Cannot see build logs or deployment details
   - Install: `npm i -g vercel`
   - Would allow: `vercel logs` and `vercel dev` for local testing

## Next Steps to Try

### High Priority

1. **Check Vercel Dashboard**
   - Verify GUARDIAN_API_KEY environment variable is set
   - Check function logs for actual error messages
   - Verify deployment succeeded

2. **Install and Use Vercel CLI**
   ```bash
   npm i -g vercel
   vercel link  # Link to existing project
   vercel logs  # View deployment logs
   vercel dev   # Test locally with Vercel's environment
   ```

3. **Test Simple Endpoint First**
   - Deploy and test `api/nodeps.py` (already created, needs push)
   - This has zero external dependencies
   - If this fails, the issue is with Vercel config, not code

### Medium Priority

4. **Simplify Dependencies**
   - Try with minimal requirements.txt
   - Check if specific versions cause issues

5. **Add Python Runtime Configuration**
   - Try adding explicit Python version specification
   - Check if pyproject.toml conflicts with requirements.txt

6. **Check Bundle Size**
   - Add excludeFiles configuration in vercel.json
   - Exclude test files and unnecessary data

### Low Priority

7. **Alternative Deployment Approach**
   - Consider moving Flask app to root level instead of api/
   - Use full Flask deployment instead of serverless functions

8. **Local Vercel Testing**
   - Use `vercel dev` to replicate the serverless environment locally
   - Debug with actual Vercel runtime

## How to Continue

1. Check Vercel dashboard for:
   - Environment variables (especially GUARDIAN_API_KEY)
   - Build logs
   - Function logs
   - Deployment status

2. Install Vercel CLI and run:
   ```bash
   vercel logs --follow
   ```

3. Try testing locally with Vercel's environment:
   ```bash
   vercel dev
   ```

4. If still failing, consider reaching out to Vercel support with:
   - Deployment URL: https://past-news.vercel.app
   - Error message: FUNCTION_INVOCATION_FAILED
   - Minimal reproduction case (api/nodeps.py)

## Testing Commands

```bash
# Run unit tests (these work!)
uv run pytest tests/ -v -k "not test_integration"

# Run integration tests against deployed instance
API_BASE_URL=https://past-news.vercel.app uv run pytest tests/test_integration.py -v

# Test individual endpoints
curl "https://past-news.vercel.app/api/simple"
curl "https://past-news.vercel.app/api/nodeps"
curl "https://past-news.vercel.app/api/index?option=one_week"
```

## Git Status

Latest commits:
- `c5fed8b` - Add BaseHTTPRequestHandler test endpoint
- `45114f9` - Add basic WSGI handler test
- `0c5c863` - Add minimal test endpoint to debug Vercel deployment
- `bf74ff6` - Restructure api directory to include all dependencies locally
- `3118b9a` - Add functions configuration to include src directory
- `8b1a3d8` - Fix Vercel serverless function deployment issues

All changes are pushed to: https://github.com/fedenanni/past_news

## Sources

- [Using the Python Runtime with Vercel Functions](https://vercel.com/docs/functions/runtimes/python)
- [Flask on Vercel](https://vercel.com/docs/frameworks/backend/flask)
- [Python 3.12 and Ruby 3.3 are now available - Vercel](https://vercel.com/changelog/python-3-12-and-ruby-3-3-are-now-available)
