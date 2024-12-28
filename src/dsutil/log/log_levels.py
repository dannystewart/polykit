from __future__ import annotations

import logging
import logging.config

log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_level_name(level: int | str) -> str:
    """Get the name of a log level."""
    if isinstance(level, str):
        level = log_levels.get(level.lower(), logging.DEBUG)
    return logging.getLevelName(level)
