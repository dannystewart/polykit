from __future__ import annotations

from datetime import datetime, timedelta

from dsutil import TZ


class SmartTimeParser:
    """Intelligent time string parser handling various formats and relative time interpretations."""

    def parse(self, time_string: str, reference_time: datetime | None = None) -> datetime | None:
        """Parse a time string into a timezone-aware datetime, relative to the reference time.

        Handles various formats including:
        - 12-hour time (2:30 pm, 2pm, 2:30)
        - 24-hour time (14:30, 1430)
        - Natural language (now, today, tomorrow)

        Args:
            time_string: The time string to parse.
            reference_time: An optional reference time to use (defaults to current time).

        Returns:
            Parsed datetime object or None if parsing fails
        """
        now = reference_time or datetime.now(TZ)
        normalized = time_string.lower().replace("am", " am").replace("pm", " pm").strip()

        # Handle special cases
        if normalized == "now":
            return now

        # Try our custom parsers first
        if parsed := self._parse_simple_time(normalized, now):
            return parsed

        # Fall back to dateutil parser if available
        try:
            from dateutil import parser

            parsed = parser.parse(time_string, fuzzy=True, default=now)
            return self._ensure_future_time(
                self._ensure_timezone(parsed), now, force_future="today" not in normalized
            )
        except (ValueError, ImportError):
            return None

    def _parse_simple_time(self, time_string: str, reference_time: datetime) -> datetime | None:
        """Parse common time formats using simple string manipulation."""
        if time := self._try_12_hour_time(reference_time, time_string):
            return time
        if time := self._try_24_hour_time(reference_time, time_string):
            return time
        if time := self._try_24_hour_without_colon(reference_time, time_string):
            return time
        return None

    def _ensure_timezone(self, dt: datetime) -> datetime:
        """Ensure datetime has the correct timezone."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=TZ)
        return dt.astimezone(TZ)

    def _ensure_future_time(
        self, dt: datetime, reference_time: datetime, force_future: bool = True
    ) -> datetime:
        """Ensure the datetime is in the future relative to the reference time."""
        if dt <= reference_time and force_future:
            return dt + timedelta(days=1)
        return dt

    def _try_12_hour_time(self, now: datetime, time_string: str) -> datetime | None:
        parts = time_string.split()
        time_parts = parts[0].split(":")

        if len(time_parts) in {1, 2} and time_parts[0].isdigit():
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) == 2 else 0

            if 1 <= hour <= 12 and 0 <= minute < 60:  # If AM/PM is explicitly specified
                if len(parts) == 2:
                    if parts[1] == "pm" and hour != 12:
                        hour += 12
                    elif parts[1] == "am" and hour == 12:
                        hour = 0
                else:  # If no AM/PM specified, interpret as the next upcoming time
                    current_hour = now.hour
                    if current_hour < 12:  # It's currently AM
                        if hour < current_hour or (hour == current_hour and minute <= now.minute):
                            # Time has passed for today, assume PM
                            hour += 12
                    elif hour < 12:
                        if hour > current_hour - 12 or (
                            hour == current_hour - 12 and minute > now.minute
                        ):  # Time is still upcoming today
                            hour += 12
                return self.adjust_for_tomorrow_if_needed(now, hour, minute)
        return None

    def _try_24_hour_time(self, now: datetime, time_string: str) -> datetime | None:
        if ":" in time_string:
            parts = time_string.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                hour = int(parts[0])
                minute = int(parts[1])
                if 0 <= hour < 24 and 0 <= minute < 60:
                    return self.adjust_for_tomorrow_if_needed(now, hour, minute)
        return None

    def _try_24_hour_without_colon(self, now: datetime, time_string: str) -> datetime | None:
        if time_string.isdigit() and len(time_string) == 4:
            hour = int(time_string[:2])
            minute = int(time_string[2:])
            if 0 <= hour < 24 and 0 <= minute < 60:
                return self.adjust_for_tomorrow_if_needed(now, hour, minute)
        return None

    @staticmethod
    def adjust_for_tomorrow_if_needed(
        time: datetime | None = None, hour: int | None = None, minute: int | None = None
    ) -> datetime:
        """Adjust the given time to the next occurrence within 24 hours.

        If hour and minute are provided, it sets the time to those values before adjusting. If no
        arguments are provided, it uses the current time.
        """
        now = datetime.now(TZ)

        if hour is not None and minute is not None:
            time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        time = time or now

        if time.tzinfo is None:
            time = time.replace(tzinfo=TZ)

        if time <= now:
            time += timedelta(days=1)

        return time

    @staticmethod
    def get_day_number(day: str) -> int:
        """Convert day name to day number (0-6, where Monday is 0)."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days.index(day)
