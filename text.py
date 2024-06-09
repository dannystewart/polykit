import re
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
ColorAttrs = list[Literal["bold", "dark", "underline", "blink", "reverse", "concealed"]]


def color(text: str, color_name: ColorName) -> str:
    """
    Use termcolor to return a string in the specified color if termcolor is available.
    Otherwise, gracefully falls back to returning the text as is.

    Args:
        text: The text to colorize.
        color_name: The name of the color.

    Returns:
        The colorized text.
    """
    try:
        from termcolor import colored
    except ImportError:
        return text

    return colored(text, color_name)


def print_colored(text: str, color_name: ColorName, end: str = "\n", attrs: ColorAttrs | None = None) -> None:
    r"""
    Use termcolor to print text in the specified color if termcolor is available.
    Otherwise, gracefully falls back to printing the text as is.

    Args:
        text: The text to print in color.
        color_name: The name of the color.
        end: The string to append after the last value. Defaults to "\n".
        attrs: A list of attributes to apply to the text (e.g., ['bold', 'underline']).
    """
    try:
        from termcolor import colored
    except ImportError:
        print(text, end=end)
        return

    print(colored(text, color_name, attrs=attrs), end=end)


def colorize(text: str, color_name: ColorName, out: bool = True, end: str = "\n") -> str | None:
    r"""
    Use termcolor to color a string, if termcolor is available. By default, it prints the
    output, but if out=False, it simply returns the colored string. This is an all-in-one
    function that does what color() and print_colored() do, with the option for either.

    Args:
        text: The text to colorize.
        color_name: The name of the color to use.
        out: Whether to print the output (default: True).
        end: The string to append after the output (default: "\n").

    Returns:
        None if out=True, otherwise the colored string.
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


def remove_html_tags(text):
    """Remove HTML tags from a string."""
    return re.sub("<[^>]*>", "", text)
