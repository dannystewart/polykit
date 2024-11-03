"""async utility functions."""

from __future__ import annotations

import time
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from dsutil.text import print_colored

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Coroutine

T = TypeVar("T")
P = ParamSpec("P")


def retry_on_exc(
    exception_to_check: type[Exception],
    tries: int = 4,
    delay: float = 3,
    backoff: float = 2,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
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

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            """Wrap the function with retry logic."""
            nonlocal tries, delay
            while tries > 1:
                try:
                    return await func(*args, **kwargs)
                except exception_to_check as e:
                    if logger:
                        logger.warning("%s. Retrying in %s seconds...", str(e), delay)
                    else:
                        print_colored(f"{e}. Retrying in {delay} seconds...", "yellow")
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return await func(*args, **kwargs)

        return wrapper

    return decorator
