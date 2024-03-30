"""
This module provides utilities for displaying progress messages and spinners.
"""

import subprocess
import time
from contextlib import contextmanager
from functools import wraps

from halo import Halo

from .shell import color as colorize
from .shell import print_colored


def with_retries(operation_func):
    """
    Decorator for retrying operations with a spinner.

    Args:
        operation_func (callable): The operation function to retry.

    Returns:
        callable: The decorated function with retry handling.
    """

    def wrapper(*args, retries=3, wait_time=3, spinner=None, **kwargs):
        last_exception = None
        for attempt in range(retries):
            try:
                if spinner:
                    with Halo(spinner, color="blue"):
                        return operation_func(*args, **kwargs)
                else:
                    return operation_func(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                last_exception = e
                print_colored(
                    f"Failed to complete: {operation_func.__name__}, retrying... ({attempt + 1} out of {retries})",
                    "yellow",
                )
                time.sleep(wait_time)
        raise RuntimeError(
            f"Operation failed after {retries} attempts: {operation_func.__name__}"
        ) from last_exception

    return wrapper


def with_spinner(text="Processing...", success="Done!", color="cyan"):
    """
    Decorator that displays a spinner while the decorated function is running.

    Args:
        text (str): The text to display before the spinner. Defaults to "Processing...".
        success (str): The text to display when the function completes successfully. Defaults to "Done!".
        color (str): The color of the text. Defaults to "cyan".
    """

    def spinner_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            spinner = Halo(text=colorize(text, color), spinner="dots", color=color)
            spinner.start()
            try:
                result = func(*args, **kwargs)
                spinner.succeed(colorize(success, color))
            except Exception as e:
                spinner.fail(colorize(f"Failed: {e}", "red"))
                raise
            finally:
                spinner.stop()
            return result

        return wrapper

    return spinner_decorator


@contextmanager
def halo_progress_context(
    filename=None,
    start_message="Processing",
    end_message="Processed",
    fail_message="Failed",
    show=True,
):
    """
    Context manager to display a Halo spinner while a block of code is executing,
    with customized start and end messages.

    Args:
        filename (str): The name of the file being processed.
        start_message (str): The start message to display.
        end_message (str): The end message to display.
        fail_message (str): The fail message to display.
        show (bool): Whether to show the Halo spinner output. Defaults to True.

    Usage:
        file_path = "example.txt"
        with halo_progress_context(filename=file_path) as spinner:
            process_file(file_path)

        You can use spinner.succeed() or spinner.fail() to update the spinner status.

    Yields:
        Halo: The Halo spinner.

    Raises:
        Exception: If an unexpected error occurs.
    """
    fail_color = "red"
    success_color = "green"

    if filename:
        start_message = f"{start_message} {filename}"
        end_message = f"{end_message} {filename}"
        fail_message = f"{fail_message} {filename}"

    if show:
        start_color = "cyan"
        spinner = Halo(text=colorize(start_message, start_color), spinner="dots")
        spinner.start()
    else:
        spinner = None

    try:
        yield spinner
    except Exception as e:
        if spinner is not None and show:
            spinner.fail(colorize(f"{fail_message}: {e}", fail_color))
        else:
            print(colorize(f"{fail_message}: {e}", fail_color))
        raise
    if spinner and show:
        spinner.succeed(colorize(end_message, success_color))
    elif show:
        print(colorize(end_message, success_color))


@contextmanager
def conversion_list_context(file_name):
    """
    Context manager to print a converting message at the start and a completion message at the end.

    Args:
        file_name (str): The name of the file being converted.
    """
    try:
        print(f"Converting {file_name} ... ", end="")
        yield
    finally:
        print(colorize("done!", "green"))
