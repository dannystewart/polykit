from __future__ import annotations

import argparse
import textwrap
from typing import Any


class ArgParser(argparse.ArgumentParser):
    """Drop-in replacement for ArgumentParser with easier adjustment of column widths.

    Args:
        arg_width: The width of the argument column in the help text.
        max_width: The maximum width of the help text.

    Example:
        parser = ArgParser(description=__doc__, arg_width=24, max_width=120)
    """

    def __init__(self, *args: Any, **kwargs: Any):
        self.arg_width = kwargs.pop("arg_width", 24)
        self.max_width = kwargs.pop("max_width", 120)
        super().__init__(
            *args,
            **kwargs,
            formatter_class=lambda prog: CustomHelpFormatter(
                prog,
                max_help_position=self.arg_width,
                width=self.max_width,
            ),
        )


class CustomHelpFormatter(argparse.HelpFormatter):
    """Format a help message for argparse.

    This help formatter allows for customizing the column widths of arguments and help text in an
    argument parser. You can use it by passing it as the formatter_class to ArgumentParser, but it's
    designed for the custom ArgParser class and not intended to be used directly.
    """

    def __init__(self, prog: str, max_help_position: int = 24, width: int = 120):
        super().__init__(prog, max_help_position=max_help_position, width=width)
        self.custom_max_help_position = max_help_position

    def _split_lines(self, text: str, width: int) -> list[str]:
        return textwrap.wrap(text, width)

    def _format_action(self, action: argparse.Action) -> str:
        parts = super()._format_action(action)
        if action.help:
            help_position = parts.find(action.help)
            space_to_insert = max(self.custom_max_help_position - help_position, 0)
            parts = parts[:help_position] + (" " * space_to_insert) + parts[help_position:]
        return parts
