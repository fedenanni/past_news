"""Date calculation utilities for Past News application.

This module provides functions to calculate target dates while preserving
the day of week for consistent historical comparisons.
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import random


def get_one_week_ago(reference_date: date) -> date:
    """
    Calculate the date exactly one week (7 days) before the reference date.

    Args:
        reference_date: The reference date to calculate from

    Returns:
        Date object representing one week ago
    """
    return reference_date - timedelta(days=7)


def get_two_weeks_ago(reference_date: date) -> date:
    """
    Calculate the date exactly two weeks (14 days) before the reference date.

    Args:
        reference_date: The reference date to calculate from

    Returns:
        Date object representing two weeks ago
    """
    return reference_date - timedelta(days=14)


def get_one_month_ago(reference_date: date) -> date:
    """
    Calculate the date approximately one month before the reference date,
    maintaining the same day of week.

    This function handles month boundaries intelligently. It goes back one month
    using calendar months, then adjusts to find the same day of week.

    Args:
        reference_date: The reference date to calculate from

    Returns:
        Date object representing approximately one month ago with the same weekday
    """
    # Go back one month using relativedelta
    one_month_back = reference_date - relativedelta(months=1)

    # Calculate the difference in weekdays
    weekday_diff = (reference_date.weekday() - one_month_back.weekday()) % 7

    # Adjust to match the same weekday
    result = one_month_back + timedelta(days=weekday_diff)

    # If adjustment pushed us forward past the reference date, go back one week
    if result > reference_date:
        result -= timedelta(days=7)

    return result


def get_random_week_same_day(
    reference_date: date,
    start_date: date = date(2016, 5, 26)
) -> date:
    """
    Generate a random date between start_date and reference_date that falls
    on the same day of week as reference_date.

    This is useful for comparing current news coverage with a random historical
    date (starting from Trump's campaign announcement period).

    Args:
        reference_date: The reference date (typically today)
        start_date: The earliest date to consider (default: May 26, 2016)

    Returns:
        Random date with the same weekday as reference_date

    Raises:
        ValueError: If start_date is after reference_date or dates are too close
    """
    if start_date >= reference_date:
        raise ValueError("start_date must be before reference_date")

    # Get the weekday we're looking for (0 = Monday, 6 = Sunday)
    target_weekday = reference_date.weekday()

    # Find the first valid date from start_date with matching weekday
    current = start_date
    days_ahead = (target_weekday - current.weekday()) % 7
    first_valid = current + timedelta(days=days_ahead)

    # If the first valid date is past the reference date, we can't proceed
    if first_valid >= reference_date:
        raise ValueError("Date range too small to find matching weekday")

    # Calculate how many weeks fit between first_valid and reference_date
    days_between = (reference_date - first_valid).days
    weeks_between = days_between // 7

    if weeks_between < 1:
        raise ValueError("Date range too small to find matching weekday")

    # Pick a random week (0 to weeks_between - 1, so we don't pick reference_date)
    random_week = random.randint(0, weeks_between - 1)

    # Calculate the final date
    result = first_valid + timedelta(weeks=random_week)

    return result
