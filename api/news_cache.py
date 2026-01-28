"""News caching module for Past News application.

This module provides a simple cache that stores fetched news with a 4-hour TTL.
After 4 hours, the cache is automatically cleared to fetch fresh news.
"""

from datetime import datetime, timedelta
from typing import Optional

# Cache TTL in hours
CACHE_TTL_HOURS = 4


class NewsCache:
    """
    Simple in-memory cache for storing news articles with time-based expiration.

    The cache stores articles with a 4-hour TTL. After 4 hours, the cache
    is automatically cleared when accessed.

    Note: 'random' option is not cached since it should return different results.
    """

    def __init__(self):
        """Initialize empty cache."""
        self._cache = {}
        self._cache_time = None

    def _check_and_clear_expired_cache(self, current_time: datetime) -> None:
        """
        Check if the cache has expired and clear it if needed.

        Args:
            current_time: The current datetime to check against
        """
        if self._cache_time is None:
            self._cache_time = current_time
        else:
            elapsed = current_time - self._cache_time
            if elapsed >= timedelta(hours=CACHE_TTL_HOURS):
                # Cache has expired, clear it
                self._cache.clear()
                self._cache_time = current_time

    def get(self, option: str, current_time: datetime = None) -> Optional[dict]:
        """
        Get cached article data for a specific option.

        Args:
            option: Time period option ('one_week', 'two_weeks', 'one_month')
            current_time: The current datetime (default: now)

        Returns:
            Cached article data or None if not found

        Note:
            Returns None for 'random' option since it should not be cached.
        """
        if current_time is None:
            current_time = datetime.now()

        # Don't cache random options
        if option == 'random':
            return None

        # Check and clear expired cache
        self._check_and_clear_expired_cache(current_time)

        # Return cached data if available
        return self._cache.get(option)

    def set(self, option: str, data: dict, current_time: datetime = None) -> None:
        """
        Store article data in cache for a specific option.

        Args:
            option: Time period option ('one_week', 'two_weeks', 'one_month')
            data: Article data to cache
            current_time: The current datetime (default: now)

        Note:
            Does not cache 'random' option since it should not be cached.
        """
        if current_time is None:
            current_time = datetime.now()

        # Don't cache random options
        if option == 'random':
            return

        # Check and clear expired cache
        self._check_and_clear_expired_cache(current_time)

        # Store data
        self._cache[option] = data

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_time = None

    def has(self, option: str, current_time: datetime = None) -> bool:
        """
        Check if cache has data for a specific option.

        Args:
            option: Time period option to check
            current_time: The current datetime (default: now)

        Returns:
            True if data is cached, False otherwise
        """
        if current_time is None:
            current_time = datetime.now()

        # Random is never cached
        if option == 'random':
            return False

        # Check and clear expired cache
        self._check_and_clear_expired_cache(current_time)

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
