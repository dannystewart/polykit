"""
Classes for setting up and formatting loggers. The LocalLogger class provides a method for setting
up a logger with a console handler. The ConsoleColors class defines console color codes for use in
the formatter to colorize messages by log level.
"""

from __future__ import annotations

import inspect
import logging
import logging.config
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from threading import Lock
from typing import TYPE_CHECKING, Any, Literal
from zoneinfo import ZoneInfo

from dsutil.tools import get_pretty_time

if TYPE_CHECKING:
    from types import FrameType

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

    loggers: dict[str, logging.Logger] = {}
    _lock = Lock()

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

    @classmethod
    def setup_logger(
        cls,
        logger_name: str | None = None,
        level: int | str = "debug",
        message_only: bool = False,
        use_color: bool = True,
        show_class: bool = False,
        show_function: bool = False,
        log_file: str | None = None,
        log_file_level: int | str = "debug",
    ) -> logging.Logger:
        """Set up a logger with the given name and log level."""
        with cls._lock:
            frame = inspect.currentframe().f_back
            logger_name = LocalLogger.get_logger_name(frame, logger_name)

            if logger_name in cls.loggers:
                return cls.loggers[logger_name]

            logger = logging.getLogger(logger_name)
            log_level = cls.get_level_name(level)
            logger.setLevel(log_level)

            log_formatter = cls.CustomFormatter(
                message_only=message_only,
                use_color=use_color,
                show_class=show_class,
                show_function=show_function,
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            console_handler.setLevel(log_level)
            logger.addHandler(console_handler)

            if log_file:
                cls.add_file_handler(logger, log_file, log_file_level)

            logger.propagate = False
            cls.loggers[logger_name] = logger
            return logger

    @staticmethod
    def get_logger_name(frame: FrameType, logger_name: str | None = None) -> str:
        """Generate a logger identifier based on the provided parameters and calling context."""

        def get_class_name() -> str:
            if "self" in frame.f_locals:
                return frame.f_locals["self"].__class__.__name__
            if "cls" in frame.f_locals:
                return frame.f_locals["cls"].__name__
            module = inspect.getmodule(frame)
            return module.__name__.split(".")[-1]

        # If no identifier is given, use the class name if provided
        return get_class_name() if logger_name is None else logger_name

    @staticmethod
    def update_level(logger: logging.Logger, level: str, log: bool = False) -> None:
        """
        Update the log level of a specific logger and all of its handlers.

        Usage:
            LocalLogger.update_level(logger, "debug")
        """
        log_level = LocalLogger.get_level_name(level)
        logger.setLevel(log_level)
        for handler in logger.handlers:
            handler.setLevel(log_level)
        if log:
            logger.info("Log level changed to %s.", level)

    @classmethod
    def update_all_levels(cls, new_level: str, log: bool = False) -> None:
        """
        Update log levels for all currently registered loggers.

        Usage:
            LocalLogger.update_all_levels("debug")
        """
        with cls._lock:
            for logger in cls.loggers.values():
                cls.update_level(logger, new_level)
                if log:
                    log_level = LocalLogger.get_level_name(new_level)
                    logger.info("Log level for logger '%s' changed to %s.", logger.name, log_level)

    @staticmethod
    def get_level_name(level: int | str) -> str:
        """Get the name of a log level."""
        if isinstance(level, str):
            level = log_levels.get(level.lower(), logging.DEBUG)
        return logging.getLevelName(level)

    @staticmethod
    def add_file_handler(
        logger: logging.Logger,
        log_file: str,
        level: int | str = logging.DEBUG,
        max_bytes: int = 5 * 1024 * 1024,  # 5 MB
        backup_count: int = 5,
    ) -> None:
        """
        Add a file handler to the given logger.

        Args:
            logger: The logger to add the file handler to.
            log_file: The path to the log file.
            level: The logging level for the file handler.
            max_bytes: The maximum size of the log file before it rolls over.
            backup_count: The number of backup files to keep.
        """
        formatter = LocalLogger.FileFormatter()
        log_dir = os.path.dirname(log_file)
        log_file_path = log_file

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not os.path.isfile(log_file_path):
            with open(log_file_path, "a", encoding="utf-8"):
                os.utime(log_file_path, None)

        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(LocalLogger.get_level_name(level))
        logger.addHandler(file_handler)

    class CustomFormatter(logging.Formatter):
        """Custom log formatter supporting both basic and advanced formats."""

        def __init__(
            self,
            message_only: bool = False,
            use_color: bool = True,
            show_class: bool = False,
            show_function: bool = False,
        ):
            super().__init__()
            self.message_only = message_only
            self.use_color = use_color
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

    class FileFormatter(logging.Formatter):
        """Formatter class for file log messages."""

        def format(self, record: logging.LogRecord) -> str:
            """Format a log record for file output."""
            record.asctime = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
            return f"[{record.asctime}] [{record.levelname}] {record.name}: {record.funcName}: {record.getMessage()}"


class TimeAwareLogger:
    """A logger class that formats datetime objects into human-readable strings."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def __getattr__(self, item: Any) -> Any:
        """
        Delegate attribute access to the underlying logger object. This handles cases where the
        logger's method is called directly on this class instance.
        """
        return getattr(self.logger, item)

    @staticmethod
    def _format_args(*args: Any) -> list[Any]:
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
