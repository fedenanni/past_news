"""Tests for news_cache module."""

import pytest
from datetime import date, timedelta
from src.news_cache import NewsCache, get_cache


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
        assert cache._cache_date is None


class TestCacheGetAndSet:
    """Tests for cache get and set operations."""

    def test_set_and_get_one_week(self, cache, sample_article_data):
        """Test setting and getting cached data for one_week."""
        today = date(2024, 1, 28)
        cache.set('one_week', sample_article_data, today)

        result = cache.get('one_week', today)
        assert result == sample_article_data

    def test_set_and_get_two_weeks(self, cache, sample_article_data):
        """Test setting and getting cached data for two_weeks."""
        today = date(2024, 1, 28)
        cache.set('two_weeks', sample_article_data, today)

        result = cache.get('two_weeks', today)
        assert result == sample_article_data

    def test_set_and_get_one_month(self, cache, sample_article_data):
        """Test setting and getting cached data for one_month."""
        today = date(2024, 1, 28)
        cache.set('one_month', sample_article_data, today)

        result = cache.get('one_month', today)
        assert result == sample_article_data

    def test_get_nonexistent_key(self, cache):
        """Test getting data that doesn't exist returns None."""
        today = date(2024, 1, 28)
        result = cache.get('one_week', today)
        assert result is None

    def test_multiple_keys(self, cache, sample_article_data):
        """Test storing multiple different keys."""
        today = date(2024, 1, 28)

        data_one_week = {**sample_article_data, 'date': '2024-01-21'}
        data_two_weeks = {**sample_article_data, 'date': '2024-01-14'}

        cache.set('one_week', data_one_week, today)
        cache.set('two_weeks', data_two_weeks, today)

        assert cache.get('one_week', today) == data_one_week
        assert cache.get('two_weeks', today) == data_two_weeks


class TestRandomOptionNotCached:
    """Tests that random option is never cached."""

    def test_set_random_does_nothing(self, cache, sample_article_data):
        """Test that setting random option doesn't cache."""
        today = date(2024, 1, 28)
        cache.set('random', sample_article_data, today)

        result = cache.get('random', today)
        assert result is None

    def test_get_random_always_returns_none(self, cache, sample_article_data):
        """Test that get for random always returns None."""
        today = date(2024, 1, 28)

        # Manually add to cache (bypassing set)
        cache._cache['random'] = sample_article_data
        cache._cache_date = today

        # Should still return None for random
        result = cache.get('random', today)
        assert result is None


class TestCacheDateExpiration:
    """Tests for cache expiration when date changes."""

    def test_cache_clears_when_date_changes(self, cache, sample_article_data):
        """Test that cache clears when date changes."""
        day1 = date(2024, 1, 28)
        day2 = date(2024, 1, 29)

        # Set data for day 1
        cache.set('one_week', sample_article_data, day1)
        assert cache.get('one_week', day1) == sample_article_data

        # Access with day 2 should trigger clear
        result = cache.get('one_week', day2)
        assert result is None

    def test_cache_clears_on_set_with_new_date(self, cache, sample_article_data):
        """Test that cache clears when setting with new date."""
        day1 = date(2024, 1, 28)
        day2 = date(2024, 1, 29)

        # Set data for day 1
        cache.set('one_week', sample_article_data, day1)
        cache.set('two_weeks', sample_article_data, day1)

        # Set data for day 2 should clear old cache
        new_data = {**sample_article_data, 'date': '2024-01-22'}
        cache.set('one_week', new_data, day2)

        # Should only have new data
        assert cache.get('one_week', day2) == new_data
        assert cache.get('two_weeks', day2) is None

    def test_cache_date_updates(self, cache, sample_article_data):
        """Test that cache date is updated when date changes."""
        day1 = date(2024, 1, 28)
        day2 = date(2024, 1, 29)

        cache.set('one_week', sample_article_data, day1)
        assert cache._cache_date == day1

        cache.set('one_week', sample_article_data, day2)
        assert cache._cache_date == day2

    def test_cache_persists_same_date(self, cache, sample_article_data):
        """Test that cache persists when accessing with same date."""
        today = date(2024, 1, 28)

        cache.set('one_week', sample_article_data, today)
        cache.set('two_weeks', sample_article_data, today)

        # Multiple accesses with same date should keep cache
        assert cache.get('one_week', today) == sample_article_data
        assert cache.get('two_weeks', today) == sample_article_data
        assert cache.get('one_week', today) == sample_article_data


class TestCacheHas:
    """Tests for has method."""

    def test_has_returns_true_when_cached(self, cache, sample_article_data):
        """Test that has returns True for cached data."""
        today = date(2024, 1, 28)
        cache.set('one_week', sample_article_data, today)

        assert cache.has('one_week', today) is True

    def test_has_returns_false_when_not_cached(self, cache):
        """Test that has returns False for non-cached data."""
        today = date(2024, 1, 28)
        assert cache.has('one_week', today) is False

    def test_has_returns_false_for_random(self, cache, sample_article_data):
        """Test that has always returns False for random."""
        today = date(2024, 1, 28)
        cache.set('random', sample_article_data, today)

        assert cache.has('random', today) is False

    def test_has_returns_false_after_date_change(self, cache, sample_article_data):
        """Test that has returns False after date changes."""
        day1 = date(2024, 1, 28)
        day2 = date(2024, 1, 29)

        cache.set('one_week', sample_article_data, day1)
        assert cache.has('one_week', day1) is True

        # Should return False for new date
        assert cache.has('one_week', day2) is False


class TestCacheClear:
    """Tests for clear method."""

    def test_clear_removes_all_data(self, cache, sample_article_data):
        """Test that clear removes all cached data."""
        today = date(2024, 1, 28)

        cache.set('one_week', sample_article_data, today)
        cache.set('two_weeks', sample_article_data, today)
        cache.set('one_month', sample_article_data, today)

        cache.clear()

        # Check that cache_date is cleared immediately after clear()
        assert cache._cache_date is None

        # Check that all cached data is gone (note: get() will reinitialize _cache_date)
        assert cache.get('one_week', today) is None
        assert cache.get('two_weeks', today) is None
        assert cache.get('one_month', today) is None


class TestDefaultDateParameter:
    """Tests for default date parameter (using today)."""

    def test_set_without_date_uses_today(self, cache, sample_article_data):
        """Test that set without date parameter uses today."""
        cache.set('one_week', sample_article_data)

        # Should be retrievable with today
        result = cache.get('one_week', date.today())
        assert result == sample_article_data

    def test_get_without_date_uses_today(self, cache, sample_article_data):
        """Test that get without date parameter uses today."""
        today = date.today()
        cache.set('one_week', sample_article_data, today)

        result = cache.get('one_week')
        assert result == sample_article_data

    def test_has_without_date_uses_today(self, cache, sample_article_data):
        """Test that has without date parameter uses today."""
        today = date.today()
        cache.set('one_week', sample_article_data, today)

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
        today = date.today()

        cache1 = get_cache()
        cache1.set('one_week', sample_article_data, today)

        cache2 = get_cache()
        result = cache2.get('one_week', today)

        assert result == sample_article_data

        # Clean up global cache
        cache1.clear()
