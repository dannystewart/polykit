from __future__ import annotations

from .color import info, progress
from .text import Text
from .types import ColorAttrs, ColorName

# NOTE: Consider removing these for 0.4.0
color = Text.color
print_colored = Text.print_colored
