from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

SMART_QUOTES_TABLE = str.maketrans(
    {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
)

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

rich_attrs = {
    "bold": "bold",
    "dark": "dim",
    "underline": "underline",
    "blink": "blink",
    "reverse": "reverse",
    "concealed": "hidden",
}
