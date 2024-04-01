"""
This module contains async utility functions.
"""

import time
from functools import wraps


def retry_on_exc(exception_to_check, tries=4, delay=3, backoff=2, logger=None):
    """
    A decorator to retry a function if a specified exception occurs. This is an async version of the
    decorator that's in dsutil.sys.

    Args:
        exception_to_check (Exception): The exception to check for retries.
        tries (int): Maximum number of retries.
        delay (int): Initial delay between retries in seconds.
        backoff (int): Multiplier applied to delay each retry.
        logger (logging.Logger): Logger for logging retries, None if no logging is needed.
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
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return await func(*args, **kwargs)

        return wrapper

    return decorator
