from __future__ import annotations

from enum import StrEnum


class LogColors(StrEnum):
    """Available types of log formatting."""

    RESET = "\033[0m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[95m"


LEVEL_COLORS: dict[str, str] = {
    "DEBUG": LogColors.GRAY,
    "INFO": LogColors.GREEN,
    "WARNING": LogColors.YELLOW,
    "ERROR": LogColors.RED,
    "CRITICAL": LogColors.MAGENTA,
}
