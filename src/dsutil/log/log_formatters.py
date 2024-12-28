"""
Classes for setting up and formatting loggers. The LocalLogger class provides a method for setting
up a logger with a console handler. The ConsoleColors class defines console color codes for use in
the formatter to colorize messages by log level.
"""

from __future__ import annotations

import logging
import logging.config
import os
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from zoneinfo import ZoneInfo

from .log_colors import LEVEL_COLORS, LogColors


class FormatterLevel(StrEnum):
    """Available types of log formatting."""

    basic = "basic"
    advanced = "advanced"


@dataclass
class CustomFormatter(logging.Formatter):
    """Custom log formatter supporting both basic and advanced formats."""

    message_only: bool = False
    use_color: bool = True
    show_class: bool = False
    show_function: bool = False

    def __post_init__(self):
        super().__init__()

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:  # noqa
        """Format the time in a log record."""
        tz = ZoneInfo(os.getenv("TZ", "America/New_York"))
        ct = datetime.fromtimestamp(record.created, tz=tz)
        return ct.strftime(datefmt) if datefmt else ct.isoformat()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record based on the formatter style."""
        level_color = LEVEL_COLORS.get(record.levelname, LogColors.RESET)
        reset = LogColors.RESET
        bold = LogColors.BOLD
        gray = LogColors.GRAY
        blue = LogColors.BLUE

        # Add the timestamp to the record
        record.asctime = self.formatTime(record, "%I:%M:%S %p")

        if self.message_only:  # Messages above INFO show in bold
            bold = "" if record.levelname in ["DEBUG", "INFO"] else bold
            return f"{reset}{bold}{level_color}{record.getMessage()}{reset}"

        # Format the timestamp
        timestamp_color = gray if self.use_color else reset
        timestamp = f"{reset}{timestamp_color}{record.asctime}{reset} "

        # Format the log level text
        level_texts = {
            "CRITICAL": "[CRITICAL]",
            "ERROR": "[ERROR]",
            "WARNING": "[WARN]",
            "INFO": "[INFO]",
            "DEBUG": "[DEBUG]",
        }
        level_text = level_texts.get(record.levelname, "")
        line_color = level_color if self.use_color else reset
        log_level = f"{bold}{line_color}{level_text}{reset}"

        # Note whether we've above INFO level and use level color if so
        above_info = record.levelname not in ["DEBUG", "INFO"]
        reset = f"{line_color}{reset}" if above_info else f"{reset}"

        # Format the function color and name
        class_color = blue if self.use_color else reset
        class_name = f" {class_color}{record.name}:{reset} " if self.show_class else ""
        function = f"{reset}{record.funcName}: " if self.show_function else " "

        # Format the message color and return the formatted message
        message = f"{line_color}{record.getMessage()}{reset}"
        return f"{timestamp}{log_level}{class_name}{function}{message}"


@dataclass
class FileFormatter(logging.Formatter):
    """Formatter class for file log messages."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record for file output."""
        record.asctime = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"[{record.asctime}] [{record.levelname}] {record.name}: {record.funcName}: {record.getMessage()}"
