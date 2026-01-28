"""Tests for date_calculator module."""

import pytest
from datetime import date
from src.date_calculator import (
    get_one_week_ago,
    get_two_weeks_ago,
    get_one_month_ago,
    get_random_week_same_day,
)


class TestGetOneWeekAgo:
    """Tests for get_one_week_ago function."""

    def test_one_week_ago_basic(self):
        """Test basic one week calculation."""
        reference = date(2024, 1, 28)  # Sunday
        result = get_one_week_ago(reference)
        assert result == date(2024, 1, 21)
        assert result.weekday() == reference.weekday()

    def test_one_week_ago_month_boundary(self):
        """Test one week ago crossing month boundary."""
        reference = date(2024, 2, 3)  # Saturday
        result = get_one_week_ago(reference)
        assert result == date(2024, 1, 27)
        assert result.weekday() == reference.weekday()

    def test_one_week_ago_year_boundary(self):
        """Test one week ago crossing year boundary."""
        reference = date(2024, 1, 5)  # Friday
        result = get_one_week_ago(reference)
        assert result == date(2023, 12, 29)
        assert result.weekday() == reference.weekday()


class TestGetTwoWeeksAgo:
    """Tests for get_two_weeks_ago function."""

    def test_two_weeks_ago_basic(self):
        """Test basic two weeks calculation."""
        reference = date(2024, 1, 28)  # Sunday
        result = get_two_weeks_ago(reference)
        assert result == date(2024, 1, 14)
        assert result.weekday() == reference.weekday()

    def test_two_weeks_ago_month_boundary(self):
        """Test two weeks ago crossing month boundary."""
        reference = date(2024, 2, 10)  # Saturday
        result = get_two_weeks_ago(reference)
        assert result == date(2024, 1, 27)
        assert result.weekday() == reference.weekday()


class TestGetOneMonthAgo:
    """Tests for get_one_month_ago function."""

    def test_one_month_ago_basic(self):
        """Test basic one month calculation."""
        reference = date(2024, 2, 15)  # Thursday
        result = get_one_month_ago(reference)
        # Should be around January 15 (also Thursday)
        assert result.weekday() == reference.weekday()
        assert result.month == 1
        assert result.year == 2024

    def test_one_month_ago_same_weekday(self):
        """Test that one month ago preserves weekday."""
        reference = date(2024, 3, 20)  # Wednesday
        result = get_one_month_ago(reference)
        assert result.weekday() == reference.weekday()
        assert result < reference

    def test_one_month_ago_month_boundary_short_month(self):
        """Test one month ago from March (after February)."""
        reference = date(2024, 3, 31)  # Sunday
        result = get_one_month_ago(reference)
        # Should be a Sunday in late February/early March
        assert result.weekday() == reference.weekday()
        assert result < reference

    def test_one_month_ago_year_boundary(self):
        """Test one month ago crossing year boundary."""
        reference = date(2024, 1, 15)  # Monday
        result = get_one_month_ago(reference)
        assert result.weekday() == reference.weekday()
        assert result.year == 2023
        assert result.month == 12

    def test_one_month_ago_leap_year(self):
        """Test one month ago during leap year."""
        reference = date(2024, 3, 1)  # Friday (2024 is leap year)
        result = get_one_month_ago(reference)
        assert result.weekday() == reference.weekday()
        assert result < reference


class TestGetRandomWeekSameDay:
    """Tests for get_random_week_same_day function."""

    def test_random_week_same_weekday(self):
        """Test that random week returns same weekday."""
        reference = date(2024, 1, 28)  # Sunday
        start = date(2016, 5, 26)

        # Run multiple times to test randomness
        for _ in range(10):
            result = get_random_week_same_day(reference, start)
            assert result.weekday() == reference.weekday()

    def test_random_week_in_range(self):
        """Test that random week is within specified range."""
        reference = date(2024, 1, 28)
        start = date(2016, 5, 26)

        for _ in range(10):
            result = get_random_week_same_day(reference, start)
            assert start <= result < reference

    def test_random_week_default_start_date(self):
        """Test random week with default start date."""
        reference = date(2024, 1, 28)
        result = get_random_week_same_day(reference)
        assert result.weekday() == reference.weekday()
        assert date(2016, 5, 26) <= result < reference

    def test_random_week_invalid_start_after_reference(self):
        """Test that start_date after reference_date raises error."""
        reference = date(2024, 1, 28)
        start = date(2024, 2, 1)

        with pytest.raises(ValueError, match="start_date must be before reference_date"):
            get_random_week_same_day(reference, start)

    def test_random_week_start_equals_reference(self):
        """Test that start_date equal to reference_date raises error."""
        reference = date(2024, 1, 28)
        start = date(2024, 1, 28)

        with pytest.raises(ValueError, match="start_date must be before reference_date"):
            get_random_week_same_day(reference, start)

    def test_random_week_range_too_small(self):
        """Test that too small date range raises error."""
        reference = date(2024, 1, 28)  # Sunday
        start = date(2024, 1, 25)  # Thursday (only 3 days apart)

        with pytest.raises(ValueError, match="Date range too small"):
            get_random_week_same_day(reference, start)

    def test_random_week_actually_random(self):
        """Test that function returns different dates (statistical test)."""
        reference = date(2024, 1, 28)
        start = date(2016, 5, 26)

        # Generate 20 random dates
        results = set()
        for _ in range(20):
            result = get_random_week_same_day(reference, start)
            results.add(result)

        # Should have at least a few different dates (allowing for some collision)
        assert len(results) > 5, "Random function not producing varied results"

    def test_random_week_multiple_weekdays(self):
        """Test random week function with different weekdays."""
        start = date(2016, 5, 26)

        # Test with Monday
        reference_monday = date(2024, 1, 22)  # Monday
        result = get_random_week_same_day(reference_monday, start)
        assert result.weekday() == 0  # Monday

        # Test with Friday
        reference_friday = date(2024, 1, 26)  # Friday
        result = get_random_week_same_day(reference_friday, start)
        assert result.weekday() == 4  # Friday
