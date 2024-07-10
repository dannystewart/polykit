"""Loggers for the notifiers."""

import logging


class LogHelper:
    """Helper class for setting up logging."""

    loggers = {}

    @staticmethod
    def setup_logger(logger_identifier, level="INFO"):
        """
        Set up a logger with the given identifier.

        Args:
            logger_identifier (str): The identifier to use for the logger.
            level (str, optional): The logging level to use. Defaults to 'INFO'.

        Returns:
            logging.Logger: The logger that was set up.
        """
        level = LogHelper.get_log_level(level)

        if logger_identifier in LogHelper.loggers:
            logger = LogHelper.loggers[logger_identifier]
            logger.setLevel(level)
            return logger

        logger = logging.getLogger(logger_identifier)
        logger.setLevel(level)
        logger.propagate = False

        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            LogHelper.add_console_handler(logger, level)

        LogHelper.loggers[logger_identifier] = logger
        return logger

    @staticmethod
    def add_console_handler(logger, level=logging.INFO):
        """
        Add a console handler to the given logger.

        Args:
            logger (logging.Logger): The logger to add the console handler to.
            level (int, optional): The logging level to use. Defaults to logging.INFO.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(format_str, date_fmt)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    @staticmethod
    def get_log_level(level):
        """
        Convert a string to a log level.

        Args:
            level (str): The log level to convert.

        Returns:
            int: The log level as an integer.

        Raises:
            ValueError: If the log level is invalid.
        """
        levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }

        if level not in levels:
            raise ValueError(f"Invalid log level: {level}")

        return levels[level.upper()]
