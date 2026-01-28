# Past News - Trump Timeline

A dynamic web application that demonstrates how media attention shifts over time by displaying Trump-related news from different historical periods. Each article shown is from the same day of the week as today, allowing for consistent temporal comparisons.

## Features

- **Today**: See the most Trump-heavy article from today (auto-loads on page load)
- **One Week Ago**: See the most Trump-heavy article from last week (same day of week)
- **Two Weeks Ago**: View articles from two weeks back (same day of week)
- **One Month Ago**: Check coverage from approximately one month ago (same day of week)
- **Random Date**: Get a random article from the same weekday between today and May 26, 2016 (Trump campaign announcement period)

Articles are selected by first filtering to those with "Trump" in the headline, then choosing the one with the most Trump mentions in the body text.

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla) - Deployed to GitHub Pages
- **Backend**: Python with Flask - Vercel serverless functions
- **Deployment**:
  - Frontend: GitHub Pages (from `docs/` folder)
  - Backend API: Vercel serverless functions
- **API**: The Guardian Open Platform API
- **Testing**: pytest with responses for HTTP mocking

## Project Structure

```
past_news/
├── api/                    # Vercel serverless functions
│   ├── __init__.py
│   ├── index.py           # Main API endpoint
│   ├── date_calculator.py # Date calculation logic (copy for Vercel)
│   ├── guardian_client.py # Guardian API wrapper (copy for Vercel)
│   ├── article_selector.py # Article selection heuristic (copy for Vercel)
│   └── news_cache.py      # Daily news caching system (copy for Vercel)
├── docs/                  # Static frontend files (GitHub Pages)
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── src/                   # Core Python modules (for local dev/testing)
│   ├── __init__.py
│   ├── date_calculator.py # Date calculation logic
│   ├── guardian_client.py # Guardian API wrapper
│   ├── article_selector.py # Article selection heuristic
│   └── news_cache.py      # Daily news caching system
├── tests/                 # Test suite
│   ├── test_date_calculator.py
│   ├── test_guardian_client.py
│   ├── test_article_selector.py
│   ├── test_news_cache.py
│   └── test_integration.py
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore patterns
├── .vercelignore          # Vercel deployment ignore patterns
├── pyproject.toml         # Python project config and dependencies
├── requirements.txt       # Python dependencies (for Vercel)
├── uv.lock                # uv package lock file
├── vercel.json            # Vercel configuration
├── vercel_reqs.txt        # Minimal requirements for testing
└── README.md              # This file
```

## Setup

### Prerequisites

- Python 3.12+
- uv (or pip)
- The Guardian API key (free)

### Installation

1. **Clone the repository**:
   ```bash
   cd past_news
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Get a Guardian API key**:
   - Sign up at [The Guardian Open Platform](https://open-platform.theguardian.com/access/)
   - Get your free API key (300 calls/day)

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## Running Tests

Run the full test suite:

```bash
uv run pytest tests/ -v
```

Run specific test file:

```bash
uv run pytest tests/test_date_calculator.py -v
```

Run with coverage:

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## Local Development

To test locally, you can run individual modules:

### Test date calculations:

```bash
uv run python -c "from src.date_calculator import *; from datetime import date; print(get_one_week_ago(date.today()))"
```

### Test Guardian API (requires API key in environment):

```bash
export GUARDIAN_API_KEY='your-key-here'
uv run python -c "from src.guardian_client import GuardianClient; from datetime import date; client = GuardianClient('your-key'); print(len(client.search_trump_articles(date(2024, 1, 20))))"
```

### Run the API endpoint locally:

```bash
export GUARDIAN_API_KEY='your-key-here'
cd api && uv run python index.py
```

The local API server will run on `http://localhost:5001`. To test the frontend with the local API, update the API URL in [docs/script.js](docs/script.js#L67) temporarily.

## Deployment

The application uses a hybrid deployment strategy:
- **Frontend**: Deployed to GitHub Pages from the `docs/` folder
- **Backend API**: Deployed to Vercel as serverless functions

### Deploying the Backend (Vercel)

#### First-time setup:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Link your project**:
   ```bash
   vercel link
   ```

3. **Add environment variables**:
   ```bash
   vercel env add GUARDIAN_API_KEY
   ```
   Enter your Guardian API key when prompted.

#### Deploy:

```bash
vercel --prod
```

The API will be deployed to a Vercel URL (e.g., `https://past-news.vercel.app/api/index`).

### Deploying the Frontend (GitHub Pages)

1. **Enable GitHub Pages** in your repository settings:
   - Go to Settings → Pages
   - Set Source to "Deploy from a branch"
   - Select branch: `main`
   - Select folder: `/docs`

2. **Push changes** to the main branch:
   ```bash
   git add docs/
   git commit -m "Update frontend"
   git push origin main
   ```

3. The site will be automatically deployed to `https://<username>.github.io/<repository>/`

**Note**: Update the API endpoint URL in [docs/script.js](docs/script.js) to match your Vercel deployment URL.

## API Reference

### GET /api/index

Fetches Trump-related news from a specific time period.

**Query Parameters:**
- `option` (required): One of `today`, `one_week`, `two_weeks`, `one_month`, or `random`

**CORS:** The API includes CORS headers to allow requests from any origin (for GitHub Pages integration).

**Success Response (with article):**
```json
{
  "success": true,
  "date": "2024-01-21",
  "article": {
    "headline": "Trump makes statement...",
    "excerpt": "First few paragraphs...",
    "url": "https://www.theguardian.com/...",
    "published": "2024-01-21T10:00:00Z"
  }
}
```

**Success Response (quiet day):**
```json
{
  "success": true,
  "date": "2015-01-21",
  "article": null,
  "message": "No Trump coverage found on this day"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Architecture

The application follows a decoupled frontend/backend architecture:

### Frontend (GitHub Pages)
- Static HTML/CSS/JavaScript hosted on GitHub Pages
- Located in the `docs/` folder
- Makes API requests to the Vercel backend
- Styled with a Guardian-inspired color palette

### Backend (Vercel Serverless)
- Python Flask application deployed as Vercel serverless functions
- Core modules duplicated in `api/` folder (Vercel requirement - needs flat structure)
- Source modules in `src/` folder used for local development and testing
- Implements CORS headers to allow cross-origin requests from GitHub Pages

### Module Duplication
The Python modules exist in both `src/` and `api/` directories:
- **`src/`**: Used for local development and pytest testing
- **`api/`**: Copies required by Vercel's serverless deployment (must be in same directory as endpoint)

This structure allows for clean testing with pytest while meeting Vercel's deployment requirements.

**Important**: When modifying Python modules, ensure changes are synchronized between `src/` and `api/` directories to maintain consistency between local testing and production deployment.

## How It Works

### Date Calculation

The application maintains the same day of week for all date calculations:
- **One/Two Weeks**: Simple subtraction of 7/14 days
- **One Month**: Uses `dateutil.relativedelta` to go back one month, then adjusts to match the weekday
- **Random**: Generates all valid dates (same weekday) between May 26, 2016 and today, then picks one randomly

### Article Selection

Articles are selected using a two-step process:
1. Filter to articles with "Trump" in the headline (required)
2. From those filtered articles, select the one with the most Trump mentions in the body text
3. Extract the first 3 paragraphs for display

If no articles have Trump in the headline on a given date (rare post-2016), a "quiet day" message is shown.

### Daily News Caching

The application implements intelligent caching to minimize API calls:

1. **First request of the day**: When a user requests news (e.g., "one week ago"), the application:
   - Checks what day it is today
   - Checks if it has cached news for this specific day
   - If not cached, fetches from The Guardian API and stores it

2. **Automatic cleanup**: When a new day starts, previous day's cache is automatically cleared

3. **What gets cached**:
   - ✅ Today articles
   - ✅ One week ago articles
   - ✅ Two weeks ago articles
   - ✅ One month ago articles
   - ❌ Random articles (always fetched fresh for variety)

This means each cacheable option (today, one_week, two_weeks, one_month) only hits the API once per day, significantly reducing API usage from 300+ requests to typically 4-8 requests per day.

## Rate Limits

The Guardian API free tier provides:
- **300 requests per day**
- Resets at midnight UTC

With the built-in daily caching system, the application typically uses only **4-8 API calls per day** (one for each non-random option when first requested). This leaves plenty of headroom for multiple users and random article requests.

## Future Enhancements

Potential improvements listed in [PLAN.md](PLAN.md):
- ✅ ~~Response caching to reduce API calls~~ (Implemented!)
- Custom date range selector
- Multiple news sources
- LLM-powered summarization
- Usage analytics
- Persistent caching (Redis/database) for distributed deployments

## License

This project is for educational and demonstration purposes.

## Data Attribution

Article data provided by [The Guardian Open Platform](https://open-platform.theguardian.com/).

## Live Demo

- **Frontend**: Deployed on GitHub Pages
- **Backend API**: Deployed on Vercel at `https://past-news.vercel.app/api/index`

The application automatically loads today's news when you visit the page.

## Contributing

This is a personal project, but suggestions and improvements are welcome via issues.
