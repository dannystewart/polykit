"""Utility functions for working with the shell, such as handling keyboard interrupts, errors, and
colors, as well as reading and writing files.
"""

from __future__ import annotations

import os
import subprocess
import sys
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from dsbase.text import ColorName, color

if TYPE_CHECKING:
    import logging
    from collections.abc import Awaitable, Callable

T = TypeVar("T")


def handle_keyboard_interrupt(
    message: str = "Interrupted by user. Exiting...",
    exit_code: int = 1,
    callback: Callable[..., Any] | None = None,
    use_newline: bool = False,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Handle KeyboardInterrupt exceptions.

    Args:
        message: The message to display when interrupted.
        exit_code: The exit code to use when terminating.
        callback: An optional function to call before exiting.
        use_newline: Whether to print a newline before the message.
        logger: An optional logger to use rather than creating a new one.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                if use_newline:  # Move to next line without clearing current line
                    sys.stdout.write("\n")
                else:  # Clear the current line
                    sys.stdout.write("\r\033[K")
                sys.stdout.flush()

                if callback:  # Check the signature of the callback function
                    import inspect
                    import signal

                    sig = inspect.signature(callback)
                    param_count = len([
                        p
                        for p in sig.parameters.values()
                        if p.default == inspect.Parameter.empty
                        and p.kind
                        not in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
                    ])

                    # Call the callback with appropriate arguments
                    if param_count == 0:
                        callback()
                    elif "signum" in sig.parameters and "frame" in sig.parameters:
                        callback(signal.SIGINT, None)  # Signal handler style callback
                    else:
                        callback(*args, **kwargs)  # Pass the original arguments

                if logger:  # Use supplied logger
                    logger.error(message)
                else:  # Create new logger
                    from dsbase.log import LocalLogger

                    LocalLogger().get_logger(simple=True).error(message)
                sys.exit(exit_code)

        return wrapper

    return decorator


def catch_errors(
    additional_errors: dict[type[Exception], str] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Handle errors. Includes handling for common errors and allows specification of additional,
    more specific errors.

    Args:
        additional_errors: Mapping of additional Exception types to messages. Defaults to None.
    """
    error_map = {
        FileNotFoundError: "Error: File {file} was not found.",
        PermissionError: "Error: Permission denied when accessing {file}.",
        Exception: "An unexpected error occurred: {e}",
    }
    if additional_errors:
        error_map.update(additional_errors)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except tuple(error_map.keys()) as e:
                error_message = error_map[type(e)]
                formatted_message = error_message.format(file=args[0], e=e)
                print(formatted_message, file=sys.stderr)
                sys.exit(1)

        return wrapper

    return decorator


def read_file_content(filepath: str) -> str:
    """Read the contents of a file.

    Args:
        filepath: The path to the file.

    Returns:
        The contents of the file.
    """
    with Path(filepath).open(encoding="utf-8") as file:
        return file.read()


def write_to_file(filepath: str, content: str) -> None:
    """Write content to a file.

    Args:
        filepath: The path to the file.
        content: The content to write.
    """
    with Path(filepath).open("w", encoding="utf-8") as file:
        file.write(content)


def is_root_user() -> bool:
    """Confirm that the script is running as root.

    Returns:
        Whether the script is running as root.
    """
    return False if sys.platform.startswith("win") else os.geteuid() == 0


def acquire_sudo() -> bool:
    """Acquire sudo access.

    Returns:
        Whether sudo access was successfully acquired.
    """
    try:  # Check if we already have sudo privileges
        subprocess.run(
            ["sudo", "-n", "true"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        try:  # If we don't have sudo privileges, try to acquire them
            subprocess.run(["sudo", "-v"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False


def get_single_char_input(prompt: str = "") -> str:
    """Read a single character without requiring the Enter key. Mainly for confirmation prompts.
    Supports Windows using msvcrt and Unix-like systems using termios.

    Args:
        prompt: The prompt to display to the user.

    Returns:
        The character that was entered.
    """
    print(prompt, end="", flush=True)

    if sys.platform.startswith("win"):  # Windows-specific implementation
        import msvcrt

        char = msvcrt.getch().decode()  # type: ignore
    else:  # macOS and Linux (adult operating systems)
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


def confirm_action(
    prompt: str, default_to_yes: bool = False, prompt_color: ColorName = "white"
) -> bool:
    """Ask the user to confirm an action before proceeding.

    Usage:
        if confirm_action("Do you want to proceed?"):

    Args:
        prompt: The prompt to display to the user.
        default_to_yes: Whether to default to "yes" instead of "no".
        prompt_color: The color of the prompt. Defaults to "white".

    Returns:
        Whether the user confirmed the action.
    """
    options = "[Y/n]" if default_to_yes else "[y/N]"
    full_prompt = color(f"{prompt} {options} ", prompt_color)
    sys.stdout.write(full_prompt)

    char = get_single_char_input("").lower()

    sys.stdout.write(char + "\n")
    sys.stdout.flush()

    return char != "n" if default_to_yes else char == "y"


def async_handle_keyboard_interrupt(
    message: str = "Interrupted by user. Exiting...",
    exit_code: int = 1,
    callback: Callable[..., Any] | None = None,
    use_newline: bool = False,
    use_logging: bool = False,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Handle KeyboardInterrupt exceptions in async functions."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except KeyboardInterrupt:
                if use_newline:
                    sys.stdout.write("\n")
                else:
                    sys.stdout.write("\r\033[K")
                sys.stdout.flush()

                if callback:
                    import asyncio

                    if asyncio.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)

                log_message = message  # Assuming color() was imported
                if logger:
                    logger.info(log_message)
                elif use_logging:
                    from dsbase.log import LocalLogger

                    LocalLogger().get_logger().info(log_message)
                else:
                    print(log_message)
                sys.exit(exit_code)

        return wrapper

    return decorator
