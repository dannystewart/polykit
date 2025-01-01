"""Utilities for displaying progress messages and spinners."""

from __future__ import annotations

import subprocess
import time
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from halo import Halo

from dsutil.shell import color as colorize
from dsutil.text import ColorName, print_colored

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

T = TypeVar("T")


def with_retries(operation_func: Callable[..., T]) -> Callable[..., T]:
    """Retry operations with a spinner.

    Args:
        operation_func: The operation function to retry.

    Returns:
        callable: The decorated function with retry handling.
    """

    def wrapper(
        *args: Any,
        retries: int = 3,
        wait_time: float = 3,
        spinner: Halo = None,
        **kwargs: Any,
    ) -> T:
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
        msg = f"Operation failed after {retries} attempts: {operation_func.__name__}"
        raise RuntimeError(msg) from last_exception

    return wrapper


def with_spinner(
    text: str = "Processing...",
    success: str | None = None,
    color: ColorName | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Display a spinner while the decorated function is running.

    Args:
        text: The text to display before the spinner. Defaults to "Processing...".
        success: The text to display when the function completes successfully. Defaults to "Done!".
        color: The color of the text. Defaults to "cyan".
    """

    def spinner_decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            spinner_text = colorize(text, color) if color else text
            spinner = Halo(text=spinner_text, spinner="dots", color=color)
            spinner.start()
            try:
                result = func(*args, **kwargs)
                if success:
                    spinner.succeed(colorize(success, color))
                else:
                    spinner.stop()
            except Exception as e:
                spinner.fail(colorize(f"Failed: {e}", "red"))
                raise
            finally:
                spinner.stop()
            return result

        return wrapper

    return spinner_decorator


@contextmanager
def halo_progress(
    filename: str | None = None,
    start_message: str = "Processing",
    end_message: str = "Processed",
    fail_message: str = "Failed",
    show: bool = True,
) -> Generator[Halo | None, None, None]:
    """Context manager to display a Halo spinner while a block of code is executing, with customized
    start and end messages.

    Args:
        filename: The name of the file being processed.
        start_message: The start message to display.
        end_message: The end message to display.
        fail_message: The fail message to display.
        show: Whether to show the Halo spinner output. Defaults to True.

    Usage:
        file_path = "example.txt"
        with halo_progress(filename=file_path) as spinner:
            process_file(file_path)

        You can use spinner.succeed() or spinner.fail() to update the spinner status.

    Yields:
        Halo: The Halo spinner.
    """
    fail_color: ColorName = "red"
    success_color: ColorName = "green"

    if filename:
        start_message = f"{start_message} {filename}"
        end_message = f"{end_message} {filename}"
        fail_message = f"{fail_message} {filename}"

    if show:
        start_color: ColorName = "cyan"
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
def conversion_list_context(file_name: str) -> Generator[None, None, None]:
    """Context manager to print a message at the start and end of an operation.

    Args:
        file_name: The name of the file being converted.
    """
    try:
        print(f"Converting {file_name} ... ", end="")
        yield
    finally:
        print(colorize("done!", "green"))
