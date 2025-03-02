"""Classes for setting up and formatting loggers.

LocalLogger and related classes provide methods for setting up a logger with a console handler,
defining console color codes for use in the formatter to colorize messages by log level, and more.
"""

from __future__ import annotations

import inspect
import logging
import logging.config
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dsutil.common import Singleton
from dsutil.log.log_formatters import CustomFormatter, FileFormatter
from dsutil.log.log_metadata import LogLevel


class LocalLogger(metaclass=Singleton):
    """Set up an easy local logger with a console handler.

    Logs at DEBUG level by default, but can be set to any level using the log_level parameter. Uses
    a custom formatter that includes the time, logger name, function name, and log message.

    Usage:
        from dsutil.log import LocalLogger
        logger = LocalLogger().get_logger(self.__class__.__name__)
        logger = LocalLogger().get_logger("MyClassLogger", advanced=True)
    """

    def get_logger(
        self,
        logger_name: str | None = None,
        level: int | str = "debug",
        simple: bool = False,
        show_context: bool = False,
        color: bool = True,
        log_file: Path | None = None,
    ) -> Logger:
        """Set up a logger with the given name and log level.

        Args:
            logger_name: The name of the logger. If None, the class or module name is used.
            level: The log level. Defaults to 'debug'.
            simple: Use simple format that displays only the log message itself. Defaults to False.
            show_context: Show the class and function name in the log message. Defaults to False.
            color: Use color in the log output. Defaults to True.
            log_file: Path to a desired log file. Defaults to None, which means no file logging.
        """
        logger_name = LocalLogger().get_logger_name(logger_name)
        logger = logging.getLogger(logger_name)

        if not logger.handlers:
            log_level = LogLevel.get_level(level)
            logger.setLevel(log_level)

            log_formatter = CustomFormatter(simple=simple, color=color, show_context=show_context)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            console_handler.setLevel(log_level)
            logger.addHandler(console_handler)

            if log_file:
                self.add_file_handler(logger, log_file)

            logger.propagate = False

        return logger

    @staticmethod
    def get_logger_name(logger_name: str | None = None) -> str:
        """Generate a logger identifier based on the provided parameters and calling context."""
        frame = inspect.currentframe().f_back.f_back  # get_logger's caller

        def get_class_name() -> str:
            if "self" in frame.f_locals:
                return frame.f_locals["self"].__class__.__name__
            if "cls" in frame.f_locals:
                return frame.f_locals["cls"].__name__
            module = inspect.getmodule(frame)
            return module.__name__.split(".")[-1]

        # If no identifier is given, use the class name if provided
        return get_class_name() if logger_name is None else logger_name

    def add_file_handler(self, logger: Logger, log_file: str) -> None:
        """Add a file handler to the given logger.

        Args:
            logger: The logger to add the file handler to.
            log_file: The path to the log file.
        """
        formatter = FileFormatter()
        log_dir = Path(log_file).parent
        log_file_path = Path(log_file)

        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        if not log_file_path.is_file():
            log_file_path.touch()

        file_handler = RotatingFileHandler(log_file, maxBytes=512 * 1024)
        file_handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
