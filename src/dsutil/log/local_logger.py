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
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import TYPE_CHECKING, Any

from dsutil.log.log_formatters import CustomFormatter, FileFormatter
from dsutil.log.log_levels import get_level_name
from dsutil.tools import Singleton

if TYPE_CHECKING:
    from types import FrameType


class LocalLogger(metaclass=Singleton):
    """Set up an easy local logger with a console handler.

    Logs at INFO level by default, but can be set to any level using the log_level parameter. Uses a
    custom formatter that includes the time, logger name, function name, and log message.

    Usage:
        from dsutil.log import LocalLogger
        logger = LocalLogger().get_logger(self.__class__.__name__)
        logger = LocalLogger().get_logger("MyClassLogger", advanced=True)
    """

    def get_logger(
        self,
        logger_name: str | None = None,
        level: int | str = "debug",
        message_only: bool = False,
        use_color: bool = True,
        show_class: bool = False,
        show_function: bool = False,
        log_file: str | None = None,
        log_file_level: int | str = "debug",
    ) -> Logger:
        """Set up a logger with the given name and log level."""
        frame = inspect.currentframe().f_back
        logger_name = LocalLogger().get_logger_name(frame, logger_name)

        logger = logging.getLogger(logger_name)
        log_level = get_level_name(level)
        logger.setLevel(log_level)

        log_formatter = CustomFormatter(
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
            self.add_file_handler(logger, log_file, log_file_level)

        logger.propagate = False
        return logger

    @staticmethod
    def setup_logger(*args: Any, **kwargs: Any) -> Logger:
        """Static method that calls get_logger for backward compatibility."""
        return LocalLogger().get_logger(*args, **kwargs)

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

    def add_file_handler(
        self,
        logger: Logger,
        log_file: str,
        level: int | str = logging.DEBUG,
        max_bytes: int = 512 * 1024,  # 500 KB
        backup_count: int = 2,
    ) -> None:
        """Add a file handler to the given logger.

        Args:
            logger: The logger to add the file handler to.
            log_file: The path to the log file.
            level: The logging level for the file handler.
            max_bytes: The maximum size of the log file before it rolls over.
            backup_count: The number of backup files to keep.
        """
        formatter = FileFormatter()
        log_dir = os.path.dirname(log_file)
        log_file_path = log_file

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not os.path.isfile(log_file_path):
            with open(log_file_path, "a", encoding="utf-8"):
                os.utime(log_file_path, None)

        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(LocalLogger().get_level_name(level))
        logger.addHandler(file_handler)
