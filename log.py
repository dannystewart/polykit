"""
Classes for setting up and formatting loggers. The LocalLogger class provides a method for setting
up a logger with a console handler. The ConsoleColors class defines console color codes for use in
the formatter to colorize messages by log level.
"""

import logging
import os
from datetime import datetime
from typing import Any, Literal

from zoneinfo import ZoneInfo

from dsutil.time_utils import get_pretty_time

FormatterLevel = Literal["basic", "advanced"]

log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class LocalLogger:
    """
    Set up an easy local logger with a console handler. The level is set to INFO by default, but can
    be set to any level using the log_level parameter. The logger uses a custom formatter that
    includes the time, logger name, function name, and log message.

    Usage:
        from dsutil.log import LocalLogger
        logger = LocalLogger.setup_logger(self.__class__.__name__)
        logger = LocalLogger.setup_logger("MyClassLogger", advanced=True)
    """

    LEVEL_COLORS = {
        "DEBUG": "\033[90m",  # Gray
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GRAY = "\033[90m"
    BLUE = "\033[34m"

    @staticmethod
    def setup_logger(
        logger_name: str,
        level: int | str = "debug",
        message_only: bool = False,
        message_in_color: bool = True,
        show_class: bool = False,
        show_function: bool = False,
    ) -> logging.Logger:
        """Set up a logger with the given name and log level."""
        logger = logging.getLogger(logger_name)

        if isinstance(level, str):
            level = log_levels.get(level, logging.DEBUG)

        logger.setLevel(level)

        log_formatter = LocalLogger.CustomFormatter(
            message_only=message_only,
            message_in_color=message_in_color,
            show_class=show_class,
            show_function=show_function,
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

        logger.propagate = False
        return logger

    class CustomFormatter(logging.Formatter):
        """Custom log formatter supporting both basic and advanced formats."""

        def __init__(
            self,
            message_only: bool = False,
            message_in_color: bool = True,
            show_class: bool = False,
            show_function: bool = False,
        ) -> None:
            super().__init__()
            self.message_only = message_only
            self.message_in_color = message_in_color
            self.show_class = show_class
            self.show_function = show_function

        def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:  # noqa
            """Format the time in a log record."""
            tz = ZoneInfo(os.getenv("TZ", "America/New_York"))
            ct = datetime.fromtimestamp(record.created, tz=tz)
            return ct.strftime(datefmt) if datefmt else ct.isoformat()

        def format(self, record: logging.LogRecord) -> str:
            """Format the log record based on the formatter style."""
            level_color = LocalLogger.LEVEL_COLORS.get(record.levelname, LocalLogger.RESET)
            reset = LocalLogger.RESET
            bold = LocalLogger.BOLD
            gray = LocalLogger.GRAY
            blue = LocalLogger.BLUE

            # Add the timestamp to the record
            record.asctime = self.formatTime(record, "%I:%M:%S %p")

            # For basic logging, return the message only
            if self.message_only:
                bold = "" if record.levelname == "DEBUG" else bold
                return f"{reset}{bold}{level_color}{record.getMessage()}{reset}"

            # Format the timestamp
            timestamp = f"{reset}{gray}{record.asctime}{reset} "

            # Format the log level text
            level_texts = {
                "CRITICAL": "[CRITICAL]",
                "ERROR": "[ERROR]",
                "WARNING": "[WARN]",
                "INFO": "[INFO]",
                "DEBUG": "[DEBUG]",
            }
            level_text = level_texts.get(record.levelname, "")
            log_level = f"{bold}{level_color}{level_text}{reset}"

            # Note whether we've above INFO level and use level color if so
            above_info = record.levelname not in ["DEBUG", "INFO"]
            reset = f"{level_color}" if above_info else f"{reset}"

            # Format the function color and name
            class_name = f" {blue}{record.name}:{reset} " if self.show_class else ""
            function = f"{reset}{record.funcName}: " if self.show_function else " "

            # Format the message color and return the formatted message
            msg_color = f"{level_color}" if self.message_in_color else ""
            message = f"{msg_color}{record.getMessage()}{reset}"
            return f"{timestamp}{log_level}{class_name}{function}{message}"


class TimeAwareLogger:
    """A logger class that formats datetime objects into human-readable strings."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def __getattr__(self, item: Any) -> Any:
        """
        Delegate attribute access to the underlying logger object. This handles cases where the
        logger's method is called directly on this class instance.
        """
        return getattr(self.logger, item)

    def _format_args(self, *args: Any) -> list[Any]:
        return [get_pretty_time(arg) if isinstance(arg, datetime) else arg for arg in args]

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message with time formatted arguments."""
        formatted_args = self._format_args(*args)
        kwargs.setdefault("stacklevel", 2)
        self.logger.debug(msg, *formatted_args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message with time formatted arguments."""
        formatted_args = self._format_args(*args)
        kwargs.setdefault("stacklevel", 2)
        self.logger.info(msg, *formatted_args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message with time formatted arguments."""
        formatted_args = self._format_args(*args)
        kwargs.setdefault("stacklevel", 2)
        self.logger.warning(msg, *formatted_args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message with time formatted arguments."""
        formatted_args = self._format_args(*args)
        kwargs.setdefault("stacklevel", 2)
        self.logger.error(msg, *formatted_args, **kwargs)
