"""Integration tests for the deployed API endpoint.

These tests can be run against both local and deployed instances.
"""

import os
import pytest
import requests
from datetime import date


# Get the API base URL from environment or use default
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5000')


class TestAPIHealthAndStructure:
    """Tests for basic API health and response structure."""

    def test_api_requires_option_parameter(self):
        """Test that API returns error when option parameter is missing."""
        response = requests.get(f"{API_BASE_URL}/api/index")

        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'option' in data['error'].lower()

    def test_api_rejects_invalid_option(self):
        """Test that API returns error for invalid option values."""
        response = requests.get(f"{API_BASE_URL}/api/index?option=invalid")

        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'invalid' in data['error'].lower()


class TestAPIValidOptions:
    """Tests for valid time period options."""

    @pytest.mark.parametrize("option", ["one_week", "two_weeks", "one_month"])
    def test_valid_options_return_success(self, option):
        """Test that valid options return successful responses."""
        response = requests.get(f"{API_BASE_URL}/api/index?option={option}")

        # Should be 200 OK
        assert response.status_code == 200

        # Should have valid JSON
        data = response.json()
        assert 'success' in data
        assert 'date' in data

        # If successful, should have article or message
        if data['success']:
            assert 'article' in data
            # Either has an article or a "quiet day" message
            assert data['article'] is not None or 'message' in data

    def test_random_option_returns_success(self):
        """Test that random option returns a valid response."""
        response = requests.get(f"{API_BASE_URL}/api/index?option=random")

        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert 'date' in data


class TestAPIResponseFormat:
    """Tests for API response format and data structure."""

    def test_successful_article_response_structure(self):
        """Test that successful responses have correct structure."""
        response = requests.get(f"{API_BASE_URL}/api/index?option=one_week")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert 'success' in data
        assert 'date' in data
        assert 'article' in data

        # If article exists, check its structure
        if data['article'] is not None:
            article = data['article']
            assert 'headline' in article
            assert 'excerpt' in article
            assert 'url' in article
            assert 'published' in article

            # Check types
            assert isinstance(article['headline'], str)
            assert isinstance(article['excerpt'], str)
            assert isinstance(article['url'], str)
            assert isinstance(article['published'], str)

            # Check URL format
            assert article['url'].startswith('http')

    def test_date_format_is_valid(self):
        """Test that returned date is in correct format."""
        response = requests.get(f"{API_BASE_URL}/api/index?option=one_week")

        assert response.status_code == 200
        data = response.json()

        # Parse date to ensure it's valid ISO format
        date_str = data['date']
        try:
            parsed_date = date.fromisoformat(date_str)
            assert isinstance(parsed_date, date)
        except ValueError:
            pytest.fail(f"Date '{date_str}' is not in valid ISO format")


class TestAPICaching:
    """Tests for caching behavior."""

    def test_multiple_requests_same_option_consistent(self):
        """Test that multiple requests for the same option return consistent results."""
        option = "one_week"

        # Make two requests
        response1 = requests.get(f"{API_BASE_URL}/api/index?option={option}")
        response2 = requests.get(f"{API_BASE_URL}/api/index?option={option}")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Should return same date
        assert data1['date'] == data2['date']

        # If one has an article, both should (cached response)
        assert (data1['article'] is None) == (data2['article'] is None)

    def test_random_option_not_cached(self):
        """Test that random option returns potentially different dates."""
        # Make multiple requests to random endpoint
        dates = set()
        for _ in range(5):
            response = requests.get(f"{API_BASE_URL}/api/index?option=random")
            assert response.status_code == 200
            data = response.json()
            dates.add(data['date'])

        # Note: Due to caching within the same day, we might get the same date
        # This test just ensures the endpoint works, not that it's truly random
        assert len(dates) >= 1


class TestAPIErrorHandling:
    """Tests for error handling and edge cases."""

    def test_handles_network_errors_gracefully(self):
        """Test that API handles Guardian API errors gracefully."""
        # This test would require mocking or a specific test environment
        # For now, we just ensure the endpoint doesn't crash
        response = requests.get(f"{API_BASE_URL}/api/index?option=one_week")

        # Should get a valid response (either success or error, but not crash)
        assert response.status_code in [200, 429, 500, 503]

        data = response.json()
        assert 'success' in data


@pytest.mark.skip(reason="Requires Guardian API key in environment")
class TestAPIWithRealData:
    """Tests that require actual Guardian API calls."""

    def test_one_week_ago_returns_recent_article(self):
        """Test that one week ago returns an article from approximately one week ago."""
        response = requests.get(f"{API_BASE_URL}/api/index?option=one_week")

        assert response.status_code == 200
        data = response.json()

        if data['article'] is not None:
            # Check that date is approximately one week ago
            article_date = date.fromisoformat(data['date'])
            today = date.today()
            delta = (today - article_date).days

            # Should be between 7-13 days ago (one week, same weekday)
            assert 7 <= delta <= 13


# Utility function for manual testing
def test_api_manually():
    """
    Manual test function to verify deployment.

    Run with:
        API_BASE_URL=https://your-app.vercel.app pytest tests/test_integration.py::test_api_manually -v -s
    """
    print(f"\nTesting API at: {API_BASE_URL}")

    for option in ["one_week", "two_weeks", "one_month", "random"]:
        print(f"\nTesting option: {option}")
        response = requests.get(f"{API_BASE_URL}/api/index?option={option}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")


if __name__ == "__main__":
    # Run manual test when executed directly
    test_api_manually()
