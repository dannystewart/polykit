"""
This module contains utility functions for working with the shell, such as handling keyboard
interrupts, errors, and colors, as well as reading and writing files.
"""

import logging
import os
import subprocess
import sys
from functools import wraps


def handle_keyboard_interrupt(message="Interrupted by user. Exiting...", exit_code=1, callback=None):
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


def handle_errors(additional_errors=None):
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


def color(text, color_name):
    """
    Uses termcolor to return a string in the specified color if termcolor is available.
    Otherwise, gracefully falls back to returning the text as is.

    Args:
        text (str): The text to colorize.
        color_name (str): The name of the color.

    Returns:
        str: The colorized text.
    """
    try:
        from termcolor import colored
    except ImportError:
        return text

    return colored(text, color_name)


def print_colored(text, color_name, end="\n"):
    """
    Uses termcolor to print text in the specified color if termcolor is available.
    Otherwise, gracefully falls back to printing the text as is.

    Args:
        text (str): The text to print in color.
        color_name (str): The name of the color.
        end (str, optional): The string to append after the last value. Defaults to "\n".

    Returns:
        None (prints the colored text directly)
    """
    try:
        from termcolor import colored
    except ImportError:
        print(text, end=end)
        return

    print(colored(text, color_name), end=end)


def colorize(text, color_name, out=True, end="\n"):
    """
    Uses termcolor to color a string, if termcolor is available. By default, it prints the
    output, but if out=False, it simply returns the colored string. This is an all-in-one
    function that does what color() and print_colored() do, with the option for either.

    Args:
        text (str): The text to colorize.
        color_name (str): The name of the color to use.
        out (bool): Whether to print the output (default: True).
        end (str): The string to append after the output (default: "\n").

    Returns:
        str | None: None if out=True, otherwise the colored string.
    """
    try:
        from termcolor import colored
    except ImportError:
        if out:
            print(text, end=end)
        return text

    colored_text = colored(text, color_name)
    if out:
        print(colored_text, end=end)
    else:
        return colored_text
    return None


def read_file_content(filepath):
    """
    Read the contents of a file.

    Args:
        filepath (str): The path to the file.

    Returns:
        str: The contents of the file.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def write_to_file(filepath, content):
    """
    Write content to a file.

    Args:
        filepath (str): The path to the file.
        content (str): The content to write.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)


def is_root_user():
    """
    Confirm that the script is running as root.

    Returns:
        bool: Whether the script is running as root.
    """
    if sys.platform.startswith("win"):
        return False
    return os.geteuid() == 0  # pylint: disable=no-member


def acquire_sudo():
    """
    Acquire sudo access.

    Returns:
        bool: Whether sudo access was successfully acquired.
    """
    try:
        subprocess.check_call(["sudo", "-v"])
        return True
    except subprocess.CalledProcessError:
        return False


def get_single_char_input(prompt):
    """
    Reads a single character without requiring the Enter key. Mainly for confirmation prompts.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The character that was entered.
    """
    print(prompt, end="", flush=True)

    # pylint: disable=import-error
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
    # pylint: enable=import-error
    return char


def confirm_action(prompt, default_to_yes=False, prompt_color="white"):
    """
    Asks the user to confirm an action. Usage:
        if confirm_action("Do you want to proceed?"):

    Args:
        prompt (str): The prompt to display to the user.
        default_to_yes (bool): Whether to default to "yes" instead of "no".
        prompt_color (str): The color of the prompt. Defaults to "white".

    Returns:
        bool: Whether the user confirmed the action.
    """
    options = "[Y/n]" if default_to_yes else "[y/N]"
    full_prompt = color(f"{prompt} {options} ", prompt_color)
    sys.stdout.write(full_prompt)

    char = get_single_char_input("").lower()

    sys.stdout.write(char + "\n")
    sys.stdout.flush()

    return char != "n" if default_to_yes else char == "y"
