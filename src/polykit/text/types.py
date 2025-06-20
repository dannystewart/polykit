from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Literal

# Translation table for smart quotes replacement
SMART_QUOTES_TABLE = str.maketrans({
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
})


class Colors(StrEnum):
    """Available types of log formatting."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    WHITE = "\033[37m"
    BLACK = "\033[30m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    GREEN = "\033[32m"
    MAGENTA = "\033[95m"
    PURPLE = "\033[35m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_WHITE = "\033[97m"
    BRIGHT_YELLOW = "\033[93m"


COLOR_MAP: dict[str, Colors] = {
    "black": Colors.BLACK,
    "grey": Colors.GRAY,
    "red": Colors.RED,
    "green": Colors.GREEN,
    "yellow": Colors.YELLOW,
    "blue": Colors.BLUE,
    "magenta": Colors.MAGENTA,
    "cyan": Colors.CYAN,
    "light_grey": Colors.BRIGHT_WHITE,
    "dark_grey": Colors.GRAY,
    "light_red": Colors.BRIGHT_RED,
    "light_green": Colors.BRIGHT_GREEN,
    "light_yellow": Colors.BRIGHT_YELLOW,
    "light_blue": Colors.BRIGHT_BLUE,
    "light_magenta": Colors.MAGENTA,
    "light_cyan": Colors.BRIGHT_CYAN,
    "white": Colors.WHITE,
}

# Color names for termcolor
TextColor = Literal[
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


class Styles(StrEnum):
    """Available types of style formatting."""

    BOLD = "\033[1m"
    DARK = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    CONCEALED = "\033[8m"


STYLE_MAP: dict[str, Styles] = {
    "bold": Styles.BOLD,
    "dark": Styles.DARK,
    "underline": Styles.UNDERLINE,
    "blink": Styles.BLINK,
    "reverse": Styles.REVERSE,
    "concealed": Styles.CONCEALED,
}


# Color attributes for termcolor
TextStyle = Iterable[
    Literal[
        "bold",
        "dark",
        "underline",
        "blink",
        "reverse",
        "concealed",
    ]
]
