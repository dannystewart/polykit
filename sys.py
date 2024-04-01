"""
This module contains utility functions for system operations.
"""

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import wraps
from threading import Thread


def retry_on_exc(exception_to_check, tries=4, delay=3, backoff=2, logger=None):
    """
    A decorator to retry a function if a specified exception occurs.

    Args:
        exception_to_check (Exception): The exception to check for retries.
        tries (int): Maximum number of retries.
        delay (int): Initial delay between retries in seconds.
        backoff (int): Multiplier applied to delay each retry.
        logger (logging.Logger): Logger for logging retries, None if no logging is needed.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal tries, delay
            while tries > 1:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    if logger:
                        logger.warning(f"{e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def popen(*args, **kwargs):
    """
    A general context manager for running subprocesses safely.

    This function abstracts away the setup and teardown logic for running subprocesses,
    handling their cleanup regardless of whether they exit normally or raise an exception.

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


def run_in_thread(func):
    """Decorator to run a function in a separate thread."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def run_in_executor(func):
    """Decorator to run a function in ThreadPoolExecutor."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

    return wrapper
