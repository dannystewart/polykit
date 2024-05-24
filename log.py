"""
This module provides classes for setting up loggers and formatting them. The LocalLogger class
provides a method for setting up a logger with a console handler. The ConsoleColors class defines
console color codes for use in the formatter to colorize messages by log level.
"""

import logging
import logging.config
import os
from datetime import datetime
from typing import Literal

from zoneinfo import ZoneInfo

FormatterLevel = Literal["basic", "advanced"]


class LocalLogger:
    """
    This class is used to set up an easy local logger with a console handler. The level is set to
    INFO by default, but can be set to any level using the log_level parameter. The logger uses a
    custom formatter that includes the time, logger name, function name, and log message.

    Usage:
        from dsutil.log import LocalLogger
        logger = LocalLogger.setup_logger("my_logger")
    """

    LEVEL_COLORS = {
        "DEBUG": "GRAY",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "MAGENTA",
    }

    @staticmethod
    def setup_logger(
        logger_name: str, level: int = logging.INFO, formatter: FormatterLevel = "basic"
    ) -> logging.Logger:
        """Set up a logger with the given name and log level."""
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        log_formatter = (
            LocalLogger.AdvancedFormatter() if formatter == "advanced" else LocalLogger.BasicFormatter()
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

        logger.propagate = False
        return logger

    class FormatterBase(logging.Formatter):
        """Base formatter class that provides a method for formatting time in log records."""

        def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
            """Format the time in a log record."""
            tz = ZoneInfo(os.getenv("TZ", "America/New_York"))
            ct = datetime.fromtimestamp(record.created, tz=tz)
            return ct.strftime(datefmt) if datefmt else ct.isoformat()

    class BasicFormatter(FormatterBase):
        """Basic log formatter including log message only, in the color for that log level."""

        def format(self, record: logging.LogRecord) -> str:
            RESET = ConsoleColors.COLORS["RESET"]
            BOLD = ConsoleColors.COLORS["BOLD"]

            record.asctime = self.formatTime(record, "%I:%M:%S %p")
            level_color = LocalLogger.LEVEL_COLORS.get(record.levelname, "RESET")
            msg_color = ConsoleColors.COLORS.get(level_color, ConsoleColors.COLORS["RESET"])
            return f"{RESET}{BOLD}{msg_color}{record.getMessage()}{RESET}"

    class AdvancedFormatter(FormatterBase):
        """Advanced log formatter including timestamp, log level, and log message."""

        def format(self, record: logging.LogRecord) -> str:
            RESET = ConsoleColors.COLORS["RESET"]
            GRAY = ConsoleColors.COLORS["GRAY"]
            BOLD = ConsoleColors.COLORS["BOLD"]

            record.asctime = self.formatTime(record, "%I:%M:%S %p")
            level_color = ConsoleColors.COLORS.get(
                LocalLogger.LEVEL_COLORS.get(record.levelname, "RESET"), ConsoleColors.COLORS["RESET"]
            )
            timestamp = f"{RESET}{GRAY}{record.asctime}{RESET}"
            msg_color = (
                f"{RESET}{BOLD}{level_color}" if record.levelname not in ["DEBUG", "INFO"] else f"{RESET}"
            )
            return f"{timestamp} {level_color}{record.levelname}: {msg_color}{record.getMessage()}{RESET}"


class ConsoleColors:
    """This class defines console color codes for use in logging."""

    COLORS = {
        "RESET": "\033[0m",
        "BLACK": "\033[30m",
        "RED": "\033[31m",
        "GREEN": "\033[32m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
        "PURPLE": "\033[35m",
        "MAGENTA": "\033[95m",
        "CYAN": "\033[36m",
        "WHITE": "\033[37m",
        "GRAY": "\033[90m",
        "BRIGHT_RED": "\033[91m",
        "BRIGHT_GREEN": "\033[92m",
        "BRIGHT_YELLOW": "\033[93m",
        "BRIGHT_BLUE": "\033[94m",
        "BRIGHT_CYAN": "\033[96m",
        "BRIGHT_WHITE": "\033[97m",
        "BOLD": "\033[1m",
    }
