from __future__ import annotations

import os
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo


def get_timezone() -> ZoneInfo:
    """Get the timezone and return it as a ZoneInfo object."""
    timezone_str = os.getenv("TZ", "America/New_York")
    return ZoneInfo(timezone_str)


def get_pretty_time(
    time: datetime | timedelta,
    capitalize: bool = False,
    time_only: bool = False,
) -> str:
    """
    Given a timestamp, return a pretty string representation of the time.

    Args:
        time: The timestamp to convert.
        capitalize: If True, the first letter of the string will be capitalized.
        time_only: If True, only the time will be returned, not the date.
    """
    if isinstance(time, datetime):
        now = datetime.now(tz=get_timezone())
        if time_only:
            pretty_time = time.strftime("%-I:%M %p")
        elif time.date() == now.date():
            pretty_time = f"today at {time.strftime('%-I:%M %p')}"
        elif time.date() == (now - timedelta(days=1)).date():
            pretty_time = f"yesterday at {time.strftime('%-I:%M %p')}"
        elif time.date() == (now + timedelta(days=1)).date():
            pretty_time = f"tomorrow at {time.strftime('%-I:%M %p')}"
        else:
            pretty_time = time.strftime("%B %d, %Y at %-I:%M %p")

    elif isinstance(time, timedelta):
        total_seconds = int(time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        pretty_time = f"{hours}h {minutes}m {seconds}s"

    if capitalize:
        pretty_time = pretty_time[0].upper() + pretty_time[1:]

    return pretty_time


def convert_to_12h(hour: int, minutes: int = 0) -> str:
    """
    Convert 24-hour time to 12-hour time format with AM/PM, including minutes.

    Args:
        hour: The hour in 24-hour format.
        minutes: The minutes.
    """
    if not isinstance(hour, int) or not isinstance(minutes, int):
        msg = "Expected integer values for hour and minutes."
        raise TypeError(msg)

    period = "PM" if hour >= 12 else "AM"
    if hour > 12:
        hour -= 12
    elif hour == 0:
        hour = 12

    # Ensure minutes are always two digits
    minutes_formatted = f"{minutes:02d}"

    return f"{hour}:{minutes_formatted} {period}"


def convert_min_to_interval(interval: int) -> str:
    """Convert a time interval in minutes to a human-readable interval string."""
    hours, minutes = divmod(interval, 60)

    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes or not parts:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")

    return " and ".join(parts)


def convert_sec_to_interval(interval: int, omit_one: bool = False) -> str:
    """
    Convert a time interval in seconds to a human-readable interval string.

    Args:
        interval: The time interval in seconds.
        omit_one: If True, the string will not include the unit if the value is 1.

    Returns:
        A human-readable string representation of the time interval.
    """
    days, remainder = divmod(interval, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    if omit_one:
        parts = [p.replace("1 ", "") if p.startswith("1 ") else p for p in parts]

    return " and ".join(parts)


def add_time_to_datetime(
    original_datetime: datetime,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """
    Add hours, minutes, and seconds to a datetime object.

    Args:
        original_datetime: The original datetime object to be adjusted.
        hours: The number of hours to add. Defaults to 0.
        minutes: The number of minutes to add. Defaults to 0.
        seconds: The number of seconds to add. Defaults to 0.
    """
    return original_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds)
