from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from typing import Literal

ColorName = Literal[
    "black",
    "grey",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "light_grey",
    "dark_grey",
    "light_red",
    "light_green",
    "light_yellow",
    "light_blue",
    "light_magenta",
    "light_cyan",
    "white",
]
ColorAttrs = Iterable[Literal["bold", "dark", "underline", "blink", "reverse", "concealed"]]


def color(text: str, color_name: ColorName, attrs: ColorAttrs | None = None) -> str:
    """
    Use termcolor to return a string in the specified color if termcolor is available.
    Otherwise, gracefully falls back to returning the text as is.

    Args:
        text: The text to colorize.
        color_name: The name of the color.
        attrs: A list of attributes to apply to the text (e.g. ['bold', 'underline']).

    Returns:
        The colorized text.
    """
    try:
        from termcolor import colored
    except ImportError:
        return text

    return colored(text, color_name, attrs=attrs)


def print_colored(
    text: str, color_name: ColorName, end: str = "\n", attrs: ColorAttrs | None = None
) -> None:
    r"""
    Use termcolor to print text in the specified color if termcolor is available.
    Otherwise, gracefully falls back to printing the text as is.

    Args:
        text: The text to print in color.
        color_name: The name of the color.
        end: The string to append after the last value. Defaults to "\n".
        attrs: A list of attributes to apply to the text (e.g. ['bold', 'underline']).
    """
    try:
        from termcolor import colored
    except ImportError:
        print(text, end=end)
        return

    print(colored(text, color_name, attrs=attrs), end=end)


def info(message: str) -> None:
    """Print an informational message."""
    print_colored(message, "blue")


def progress(message: str) -> None:
    """Print a success/progress message."""
    print_colored(f"✔ {message}", "green")


def warning(message: str) -> None:
    """Print a warning message."""
    print_colored(message, "yellow")


def error(message: str, skip_exit: bool = False) -> None:
    """Print an error message and exit the program."""
    print_colored(f"\n{message}", "red")
    if not skip_exit:
        sys.exit(1)


def pluralize(word: str, count: int | None) -> str:
    """Pluralize a word."""
    if count is None or count == 1:
        return word
    return f"{word}es" if word.endswith("s") else f"{word}s"


def format_duration(hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
    """Print a formatted time duration."""
    sec_str = f"{seconds} {pluralize("second", seconds)}"
    min_str = f"{minutes} {pluralize("minute", minutes)}"
    hour_str = f"{hours} {pluralize("hour", hours)}"

    if hours == 0:
        if minutes == 0 and seconds == 0:
            return sec_str
        if seconds == 0:
            return min_str
        return sec_str if minutes == 0 else f"{min_str} and {sec_str}"
    if minutes == 0:
        return hour_str if seconds == 0 else f"{hour_str} and {sec_str}"
    if seconds == 0:
        return f"{hour_str} and {min_str}"
    return f"{hour_str}, {min_str} and {sec_str}"


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub("<[^>]*>", "", text)
