"""Utility functions for system operations."""

from __future__ import annotations

import subprocess
import time
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from functools import wraps
from threading import Thread
from typing import TYPE_CHECKING, Any, TypeVar

from dsutil.text import print_colored

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable

T = TypeVar("T")


def retry_on_exc(
    exception_to_check: type[Exception],
    tries: int = 4,
    delay: int = 3,
    backoff: int = 2,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry a function if a specified exception occurs.

    Args:
        exception_to_check: The exception to check for retries.
        tries: Maximum number of retries.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier applied to delay each retry.
        logger: Logger for logging retries. If None, print to stdout instead.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal tries, delay
            while tries > 1:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    if logger:
                        logger.warning("%s. Retrying in %s seconds...", str(e), delay)
                    else:
                        print_colored(f"{e}. Retrying in {delay} seconds...", "yellow")
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def popen(*args: Any, **kwargs: Any):
    """
    Context manager for running subprocesses safely.

    This function abstracts away the setup and teardown logic for running subprocesses, handling
    their cleanup regardless of whether they exit normally or raise an exception.

    Usage:
        with general_popen(['command', 'arg1', 'arg2'], stdout=subprocess.PIPE) as proc:
            stdout, stderr = proc.communicate()

    Args:
        args: Positional arguments to pass to subprocess.Popen.
        kwargs: Keyword arguments to pass to subprocess.Popen.

    Yields:
        process: The Popen object representing the subprocess.
    """
    process = subprocess.Popen(*args, **kwargs)
    try:
        yield process
    finally:
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        if process.stdin:
            process.stdin.close()

        process.terminate()
        try:
            process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def run_in_thread(func: Callable[..., T]) -> Callable[..., Thread]:
    """Run a function in a separate thread."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Thread:
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def run_in_executor(func: Callable[..., T]) -> Callable[..., T]:
    """Run a function in a separate thread using ThreadPoolExecutor."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        with ThreadPoolExecutor() as executor:
            future: Future[T] = executor.submit(func, *args, **kwargs)
            return future.result()

    return wrapper
