"""News caching module for Past News application.

This module provides a simple cache that stores fetched news for a specific day.
When a new day starts, old caches are automatically cleared.
"""

from datetime import date
from typing import Optional


class NewsCache:
    """
    Simple in-memory cache for storing news articles by date and option.

    The cache stores articles for each day, with keys for 'one_week', 'two_weeks',
    and 'one_month'. When the date changes, old caches are automatically cleared.

    Note: 'random' option is not cached since it should return different results.
    """

    def __init__(self):
        """Initialize empty cache."""
        self._cache = {}
        self._cache_date = None

    def _check_and_clear_old_cache(self, current_date: date) -> None:
        """
        Check if the date has changed and clear old cache if needed.

        Args:
            current_date: The current date to check against
        """
        if self._cache_date is None:
            self._cache_date = current_date
        elif self._cache_date != current_date:
            # Date has changed, clear old cache
            self._cache.clear()
            self._cache_date = current_date

    def get(self, option: str, current_date: date = None) -> Optional[dict]:
        """
        Get cached article data for a specific option.

        Args:
            option: Time period option ('one_week', 'two_weeks', 'one_month')
            current_date: The current date (default: today)

        Returns:
            Cached article data or None if not found

        Note:
            Returns None for 'random' option since it should not be cached.
        """
        if current_date is None:
            current_date = date.today()

        # Don't cache random options
        if option == 'random':
            return None

        # Check and clear old cache
        self._check_and_clear_old_cache(current_date)

        # Return cached data if available
        return self._cache.get(option)

    def set(self, option: str, data: dict, current_date: date = None) -> None:
        """
        Store article data in cache for a specific option.

        Args:
            option: Time period option ('one_week', 'two_weeks', 'one_month')
            data: Article data to cache
            current_date: The current date (default: today)

        Note:
            Does not cache 'random' option since it should not be cached.
        """
        if current_date is None:
            current_date = date.today()

        # Don't cache random options
        if option == 'random':
            return

        # Check and clear old cache
        self._check_and_clear_old_cache(current_date)

        # Store data
        self._cache[option] = data

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_date = None

    def has(self, option: str, current_date: date = None) -> bool:
        """
        Check if cache has data for a specific option.

        Args:
            option: Time period option to check
            current_date: The current date (default: today)

        Returns:
            True if data is cached, False otherwise
        """
        if current_date is None:
            current_date = date.today()

        # Random is never cached
        if option == 'random':
            return False

        # Check and clear old cache
        self._check_and_clear_old_cache(current_date)

        return option in self._cache


# Global cache instance
_global_cache = NewsCache()


def get_cache() -> NewsCache:
    """
    Get the global cache instance.

    Returns:
        The global NewsCache instance
    """
    return _global_cache
