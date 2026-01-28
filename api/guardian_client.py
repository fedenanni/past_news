"""The Guardian API client for fetching Trump-related articles.

This module provides a client for interacting with The Guardian Open Platform API
to search for articles mentioning Trump on specific dates.
"""

from datetime import date
from typing import Optional
import requests
from requests.exceptions import RequestException, Timeout


class GuardianAPIError(Exception):
    """Base exception for Guardian API errors."""
    pass


class GuardianRateLimitError(GuardianAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class GuardianClient:
    """
    Client for The Guardian Open Platform API.

    The client handles searching for articles mentioning Trump on specific dates,
    with proper error handling for rate limits, timeouts, and API errors.
    """

    BASE_URL = "https://content.guardianapis.com/search"
    DEFAULT_TIMEOUT = 10  # seconds

    def __init__(self, api_key: str):
        """
        Initialize the Guardian API client.

        Args:
            api_key: The Guardian API key for authentication
        """
        self.api_key = api_key
        self.session = requests.Session()

    def search_trump_articles(
        self,
        target_date: date,
        page_size: int = 50
    ) -> list[dict]:
        """
        Search for articles mentioning Trump on a specific date.

        Args:
            target_date: The date to search for articles
            page_size: Maximum number of results to return (default: 50)

        Returns:
            List of article dictionaries with the following keys:
            - id: Article ID
            - webTitle: Article headline
            - webUrl: Article URL
            - webPublicationDate: Publication date/time
            - fields: Dictionary containing body, headline, thumbnail if available

        Raises:
            GuardianRateLimitError: If API rate limit (429) is exceeded
            GuardianAPIError: For other API errors (4xx, 5xx)
            Timeout: If request times out
            RequestException: For network-related errors

        Example:
            >>> client = GuardianClient('your-api-key')
            >>> articles = client.search_trump_articles(date(2024, 1, 20))
            >>> len(articles)
            15
        """
        # Format date for API (YYYY-MM-DD)
        date_str = target_date.strftime('%Y-%m-%d')

        # Build query parameters
        params = {
            'q': 'Trump',
            'from-date': date_str,
            'to-date': date_str,
            'page-size': page_size,
            'show-fields': 'body,headline,thumbnail',
            'api-key': self.api_key,
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.DEFAULT_TIMEOUT
            )

            # Handle rate limiting
            if response.status_code == 429:
                raise GuardianRateLimitError(
                    "API rate limit exceeded. The Guardian API allows 300 calls per day."
                )

            # Handle other HTTP errors
            if response.status_code >= 400:
                raise GuardianAPIError(
                    f"Guardian API returned error {response.status_code}: {response.text}"
                )

            # Parse JSON response
            data = response.json()

            # Check API response status
            if data.get('response', {}).get('status') != 'ok':
                raise GuardianAPIError(
                    f"Guardian API returned non-OK status: {data}"
                )

            # Extract and return results
            results = data.get('response', {}).get('results', [])
            return results

        except Timeout:
            raise Timeout(
                f"Request to Guardian API timed out after {self.DEFAULT_TIMEOUT} seconds"
            )
        except RequestException as e:
            raise GuardianAPIError(f"Network error while contacting Guardian API: {e}")

    def close(self):
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
