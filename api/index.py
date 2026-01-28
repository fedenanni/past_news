"""Vercel serverless function for Past News API endpoint.

This module provides the main API endpoint for fetching Trump-related news
from different time periods.
"""

import os
from datetime import date
from flask import Flask, request, jsonify

from api.date_calculator import (
    get_one_week_ago,
    get_two_weeks_ago,
    get_one_month_ago,
    get_random_week_same_day,
)
from api.guardian_client import GuardianClient, GuardianAPIError, GuardianRateLimitError
from api.article_selector import select_most_relevant_article
from api.news_cache import get_cache

app = Flask(__name__)


def get_target_date(option: str, reference_date: date = None) -> date:
    """
    Calculate target date based on option parameter.

    Args:
        option: One of "one_week", "two_weeks", "one_month", "random"
        reference_date: Reference date to calculate from (default: today)

    Returns:
        Target date

    Raises:
        ValueError: If option is invalid
    """
    if reference_date is None:
        reference_date = date.today()

    if option == "one_week":
        return get_one_week_ago(reference_date)
    elif option == "two_weeks":
        return get_two_weeks_ago(reference_date)
    elif option == "one_month":
        return get_one_month_ago(reference_date)
    elif option == "random":
        return get_random_week_same_day(reference_date)
    else:
        raise ValueError(f"Invalid option: {option}. Must be one of: one_week, two_weeks, one_month, random")


@app.route('/', methods=['GET'])
def get_news():
    """
    API endpoint to fetch Trump news from a specific time period.

    Query Parameters:
        option: Time period option ("one_week", "two_weeks", "one_month", "random")

    Returns:
        JSON response with article data or error message

    Response Format (success):
        {
            "success": true,
            "date": "2024-01-21",
            "article": {
                "headline": "...",
                "excerpt": "...",
                "url": "...",
                "published": "..."
            }
        }

    Response Format (quiet day):
        {
            "success": true,
            "date": "2024-01-21",
            "article": null,
            "message": "No Trump coverage found on this day"
        }

    Response Format (error):
        {
            "success": false,
            "error": "Error message"
        }
    """
    try:
        # Get and validate option parameter
        option = request.args.get('option')
        if not option:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: option'
            }), 400

        # Get today's date for cache key
        today = date.today()

        # Get cache instance
        cache = get_cache()

        # Check if we have cached data for this option and today
        cached_data = cache.get(option, today)
        if cached_data is not None:
            # Return cached response
            return jsonify(cached_data)

        # Calculate target date
        try:
            target_date = get_target_date(option)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

        # Get Guardian API key from environment
        api_key = os.environ.get('GUARDIAN_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Server configuration error: GUARDIAN_API_KEY not set'
            }), 500

        # Search for articles
        try:
            client = GuardianClient(api_key)
            articles = client.search_trump_articles(target_date)
        except GuardianRateLimitError as e:
            return jsonify({
                'success': False,
                'error': 'API rate limit exceeded. Please try again later.'
            }), 429
        except GuardianAPIError as e:
            return jsonify({
                'success': False,
                'error': f'Unable to fetch articles: {str(e)}'
            }), 503

        # Select best article
        selected_article = select_most_relevant_article(articles)

        # Format response
        if selected_article:
            response_data = {
                'success': True,
                'date': target_date.strftime('%Y-%m-%d'),
                'article': selected_article
            }
        else:
            response_data = {
                'success': True,
                'date': target_date.strftime('%Y-%m-%d'),
                'article': None,
                'message': 'No Trump coverage found on this day'
            }

        # Cache the response for non-random options
        cache.set(option, response_data, today)

        return jsonify(response_data)

    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=5001)
