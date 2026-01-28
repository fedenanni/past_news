"""Tests for news_cache module."""

import pytest
from datetime import datetime, timedelta
from src.news_cache import NewsCache, get_cache, CACHE_TTL_HOURS


@pytest.fixture
def cache():
    """Create a fresh NewsCache instance for testing."""
    return NewsCache()


@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        'success': True,
        'date': '2024-01-21',
        'article': {
            'headline': 'Trump news',
            'excerpt': 'Article content...',
            'url': 'https://example.com/article',
            'published': '2024-01-21T10:00:00Z'
        }
    }


class TestNewsCacheInit:
    """Tests for NewsCache initialization."""

    def test_cache_initialization(self, cache):
        """Test that cache initializes empty."""
        assert cache._cache == {}
        assert cache._cache_time is None


class TestCacheGetAndSet:
    """Tests for cache get and set operations."""

    def test_set_and_get_one_week(self, cache, sample_article_data):
        """Test setting and getting cached data for one_week."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        cache.set('one_week', sample_article_data, now)

        result = cache.get('one_week', now)
        assert result == sample_article_data

    def test_set_and_get_two_weeks(self, cache, sample_article_data):
        """Test setting and getting cached data for two_weeks."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        cache.set('two_weeks', sample_article_data, now)

        result = cache.get('two_weeks', now)
        assert result == sample_article_data

    def test_set_and_get_one_month(self, cache, sample_article_data):
        """Test setting and getting cached data for one_month."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        cache.set('one_month', sample_article_data, now)

        result = cache.get('one_month', now)
        assert result == sample_article_data

    def test_get_nonexistent_key(self, cache):
        """Test getting data that doesn't exist returns None."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        result = cache.get('one_week', now)
        assert result is None

    def test_multiple_keys(self, cache, sample_article_data):
        """Test storing multiple different keys."""
        now = datetime(2024, 1, 28, 10, 0, 0)

        data_one_week = {**sample_article_data, 'date': '2024-01-21'}
        data_two_weeks = {**sample_article_data, 'date': '2024-01-14'}

        cache.set('one_week', data_one_week, now)
        cache.set('two_weeks', data_two_weeks, now)

        assert cache.get('one_week', now) == data_one_week
        assert cache.get('two_weeks', now) == data_two_weeks


class TestRandomOptionNotCached:
    """Tests that random option is never cached."""

    def test_set_random_does_nothing(self, cache, sample_article_data):
        """Test that setting random option doesn't cache."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        cache.set('random', sample_article_data, now)

        result = cache.get('random', now)
        assert result is None

    def test_get_random_always_returns_none(self, cache, sample_article_data):
        """Test that get for random always returns None."""
        now = datetime(2024, 1, 28, 10, 0, 0)

        # Manually add to cache (bypassing set)
        cache._cache['random'] = sample_article_data
        cache._cache_time = now

        # Should still return None for random
        result = cache.get('random', now)
        assert result is None


class TestCacheTimeExpiration:
    """Tests for cache expiration after 4 hours."""

    def test_cache_clears_after_4_hours(self, cache, sample_article_data):
        """Test that cache clears after 4 hours."""
        time1 = datetime(2024, 1, 28, 10, 0, 0)
        time2 = time1 + timedelta(hours=4)

        # Set data at time1
        cache.set('one_week', sample_article_data, time1)
        assert cache.get('one_week', time1) == sample_article_data

        # Access after 4 hours should trigger clear
        result = cache.get('one_week', time2)
        assert result is None

    def test_cache_persists_before_4_hours(self, cache, sample_article_data):
        """Test that cache persists within 4 hour window."""
        time1 = datetime(2024, 1, 28, 10, 0, 0)
        time2 = time1 + timedelta(hours=3, minutes=59)

        # Set data at time1
        cache.set('one_week', sample_article_data, time1)
        assert cache.get('one_week', time1) == sample_article_data

        # Access just before 4 hours should keep cache
        result = cache.get('one_week', time2)
        assert result == sample_article_data

    def test_cache_clears_on_set_after_4_hours(self, cache, sample_article_data):
        """Test that cache clears when setting after 4 hours."""
        time1 = datetime(2024, 1, 28, 10, 0, 0)
        time2 = time1 + timedelta(hours=5)

        # Set data at time1
        cache.set('one_week', sample_article_data, time1)
        cache.set('two_weeks', sample_article_data, time1)

        # Set data at time2 should clear old cache
        new_data = {**sample_article_data, 'date': '2024-01-22'}
        cache.set('one_week', new_data, time2)

        # Should only have new data
        assert cache.get('one_week', time2) == new_data
        assert cache.get('two_weeks', time2) is None

    def test_cache_time_updates(self, cache, sample_article_data):
        """Test that cache time is updated when cache expires."""
        time1 = datetime(2024, 1, 28, 10, 0, 0)
        time2 = time1 + timedelta(hours=5)

        cache.set('one_week', sample_article_data, time1)
        assert cache._cache_time == time1

        cache.set('one_week', sample_article_data, time2)
        assert cache._cache_time == time2

    def test_cache_persists_within_window(self, cache, sample_article_data):
        """Test that cache persists when accessing within 4 hours."""
        now = datetime(2024, 1, 28, 10, 0, 0)

        cache.set('one_week', sample_article_data, now)
        cache.set('two_weeks', sample_article_data, now)

        # Multiple accesses within window should keep cache
        later = now + timedelta(hours=2)
        assert cache.get('one_week', later) == sample_article_data
        assert cache.get('two_weeks', later) == sample_article_data
        assert cache.get('one_week', later) == sample_article_data

    def test_cache_ttl_constant(self):
        """Test that CACHE_TTL_HOURS is set to 4."""
        assert CACHE_TTL_HOURS == 4


class TestCacheHas:
    """Tests for has method."""

    def test_has_returns_true_when_cached(self, cache, sample_article_data):
        """Test that has returns True for cached data."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        cache.set('one_week', sample_article_data, now)

        assert cache.has('one_week', now) is True

    def test_has_returns_false_when_not_cached(self, cache):
        """Test that has returns False for non-cached data."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        assert cache.has('one_week', now) is False

    def test_has_returns_false_for_random(self, cache, sample_article_data):
        """Test that has always returns False for random."""
        now = datetime(2024, 1, 28, 10, 0, 0)
        cache.set('random', sample_article_data, now)

        assert cache.has('random', now) is False

    def test_has_returns_false_after_expiration(self, cache, sample_article_data):
        """Test that has returns False after cache expires."""
        time1 = datetime(2024, 1, 28, 10, 0, 0)
        time2 = time1 + timedelta(hours=5)

        cache.set('one_week', sample_article_data, time1)
        assert cache.has('one_week', time1) is True

        # Should return False after expiration
        assert cache.has('one_week', time2) is False


class TestCacheClear:
    """Tests for clear method."""

    def test_clear_removes_all_data(self, cache, sample_article_data):
        """Test that clear removes all cached data."""
        now = datetime(2024, 1, 28, 10, 0, 0)

        cache.set('one_week', sample_article_data, now)
        cache.set('two_weeks', sample_article_data, now)
        cache.set('one_month', sample_article_data, now)

        cache.clear()

        # Check that cache_time is cleared immediately after clear()
        assert cache._cache_time is None

        # Check that all cached data is gone (note: get() will reinitialize _cache_time)
        assert cache.get('one_week', now) is None
        assert cache.get('two_weeks', now) is None
        assert cache.get('one_month', now) is None


class TestDefaultTimeParameter:
    """Tests for default time parameter (using now)."""

    def test_set_without_time_uses_now(self, cache, sample_article_data):
        """Test that set without time parameter uses now."""
        cache.set('one_week', sample_article_data)

        # Should be retrievable with current time
        result = cache.get('one_week', datetime.now())
        assert result == sample_article_data

    def test_get_without_time_uses_now(self, cache, sample_article_data):
        """Test that get without time parameter uses now."""
        now = datetime.now()
        cache.set('one_week', sample_article_data, now)

        result = cache.get('one_week')
        assert result == sample_article_data

    def test_has_without_time_uses_now(self, cache, sample_article_data):
        """Test that has without time parameter uses now."""
        now = datetime.now()
        cache.set('one_week', sample_article_data, now)

        assert cache.has('one_week') is True


class TestGlobalCacheInstance:
    """Tests for global cache instance."""

    def test_get_cache_returns_same_instance(self):
        """Test that get_cache returns the same instance."""
        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2

    def test_global_cache_persists_data(self, sample_article_data):
        """Test that global cache persists data across get_cache calls."""
        now = datetime.now()

        cache1 = get_cache()
        cache1.set('one_week', sample_article_data, now)

        cache2 = get_cache()
        result = cache2.get('one_week', now)

        assert result == sample_article_data

        # Clean up global cache
        cache1.clear()
