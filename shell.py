"""
This module contains utility functions for working with the shell, such as handling keyboard
interrupts, errors, and colors, as well as reading and writing files.
"""

import logging
import os
import subprocess
import sys
from functools import wraps
from typing import Callable

from dsutil.text import ColorName, color


def handle_keyboard_interrupt(
    message: str = "Interrupted by user. Exiting...", exit_code: int = 1, callback: Callable | None = None
) -> Callable:
    """A decorator for handling KeyboardInterrupt exceptions."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                sys.stdout.write("\r")
                sys.stdout.flush()
                if callback:
                    callback()
                logging.info(message)
                sys.exit(exit_code)

        return wrapper

    return decorator


def catch_errors(additional_errors: dict | None = None) -> Callable:
    """
    A decorator for handling errors. Includes handling for common errors and allows
    specification of additional, more specific errors.

    Args:
        additional_errors (dict, optional):
            - Mapping of Exception types to messages for more specific errors.
            - Defaults to None.
    """
    error_map = {
        FileNotFoundError: "Error: File {file} was not found.",
        PermissionError: "Error: Permission denied when accessing {file}.",
        Exception: "An unexpected error occurred: {e}",
    }
    if additional_errors:
        error_map.update(additional_errors)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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
    """
    Read the contents of a file.

    Args:
        filepath: The path to the file.

    Returns:
        The contents of the file.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def write_to_file(filepath: str, content: str) -> None:
    """
    Write content to a file.

    Args:
        filepath: The path to the file.
        content: The content to write.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)


def is_root_user() -> bool:
    """
    Confirm that the script is running as root.

    Returns:
        Whether the script is running as root.
    """
    return False if sys.platform.startswith("win") else os.geteuid() == 0


def acquire_sudo() -> bool:
    """
    Acquire sudo access.

    Returns:
        Whether sudo access was successfully acquired.
    """
    try:
        subprocess.check_call(["sudo", "-v"])
        return True
    except subprocess.CalledProcessError:
        return False


def get_single_char_input(prompt: str) -> str:
    """
    Reads a single character without requiring the Enter key. Mainly for confirmation prompts.

    Args:
        prompt: The prompt to display to the user.

    Returns:
        The character that was entered.
    """
    print(prompt, end="", flush=True)

    if sys.platform.startswith("win"):  # Windows-specific implementation
        import msvcrt

        char = msvcrt.getch().decode()
    else:  # Unix-like OS implementation
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


def confirm_action(prompt, default_to_yes: bool = False, prompt_color: ColorName = "white") -> bool:
    """
    Asks the user to confirm an action. Usage:
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
