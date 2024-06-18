"""async utility functions."""

import logging
import time
from functools import wraps
from typing import Callable

from dsutil.text import print_colored


def retry_on_exc(
    exception_to_check: Exception,
    tries: int = 4,
    delay: int = 3,
    backoff: int = 2,
    logger: logging.Logger | None = None,
) -> Callable:
    """
    Retry a function if a specified exception occurs. This is an async version of the decorator
    that's in dsutil.sys.

    Args:
        exception_to_check: The exception to check for retries.
        tries: Maximum number of retries.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier applied to delay each retry.
        logger: Logger for logging retries. If None, print to stdout instead.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal tries, delay
            while tries > 1:
                try:
                    return await func(*args, **kwargs)
                except exception_to_check as e:
                    if logger:
                        logger.warning(f"{e}. Retrying in {delay} seconds...")
                    else:
                        print_colored(f"{e}. Retrying in {delay} seconds...", "yellow")
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return await func(*args, **kwargs)

        return wrapper

    return decorator
