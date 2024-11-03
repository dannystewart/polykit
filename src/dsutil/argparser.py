from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass
from typing import Any


@dataclass
class ArgInfo:
    """Information for a command-line argument."""

    help: str
    type: type | None = None
    default: Any = None
    action: str | None = None
    nargs: str | None = None
    dest: str | None = None
    required: bool = False


class ArgumentsBase:
    """Base class for command-line arguments."""

    @classmethod
    def as_dict(cls) -> dict[str, ArgInfo]:
        """Return a dictionary of argument names and ArgInfo instances in the class."""
        return {name: value for name, value in cls.__dict__.items() if isinstance(value, ArgInfo)}


class CustomHelpFormatter(argparse.HelpFormatter):
    """
    Format a help message for argparse. It allows for customizing the column width of the arguments
    and help text. You would use this class by passing it as the formatter_class argument to the
    ArgumentParser constructor, like the below example.

        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=lambda prog: CustomHelpFormatter(
                prog, max_help_position=24, width=100
            ),
        )

    But to make your life easier, just use the ArgParser class below, which uses this formatter by
    default and allows you to specify the column widths as arguments.
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


class ArgParser(argparse.ArgumentParser):
    """
    Custom ArgumentParser that uses the CustomHelpFormatter by default and makes it easier to
    specify the column widths. After importing it, just use this instead of argparse.ArgumentParser,
    like the example below.

        parser = ArgParser(description=__doc__, arg_width=24, max_width=120)

    The arg_width and max_width arguments are optional and default to 24 and 120, respectively. They
    map to max_help_position and width in CustomHelpFormatter.

    This class also provides methods for defining and adding arguments in a more structured way:
        - add_argument_from_info: Adds a single argument based on an ArgInfo instance.
        - add_args_from_class: Adds multiple arguments based on a class of ArgInfo instances.
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

    def add_argument_from_info(self, name: str, arg_info: ArgInfo) -> None:
        """
        Add an argument to the parser based on ArgInfo.

        This method simplifies the process of adding arguments by using an ArgInfo instance, which
        encapsulates all the necessary information for an argument. It automatically sets up the
        appropriate argparse parameters based on the ArgInfo properties.

        Args:
            name: The name of the argument. For positional arguments, this is used as is. For
                optional arguments, it's converted to the appropriate format (e.g. --name).
            arg_info: An instance of ArgInfo containing the argument's properties.

        The method handles different cases:
            - For 'file' argument, it's added as a positional argument.
            - For 'creation' and 'modification', both short (-c, -m) and long (--creation,
                --modification) forms are added.
            - For other arguments, they're added as long-form optional arguments (e.g.
                --argument-name).
        """
        kwargs: dict[str, Any] = {"help": arg_info.help}

        if arg_info.action in ["store_true", "store_false"]:
            kwargs["action"] = arg_info.action
        else:
            if arg_info.type is not None:
                kwargs["type"] = arg_info.type
            if arg_info.default is not None:
                kwargs["default"] = arg_info.default
            if arg_info.action:
                kwargs["action"] = arg_info.action
            if arg_info.nargs:
                kwargs["nargs"] = arg_info.nargs

        if arg_info.dest:
            kwargs["dest"] = arg_info.dest
        if arg_info.required:
            kwargs["required"] = arg_info.required

        if name == "file":
            self.add_argument(name, **kwargs)
        elif name in {"creation", "modification"}:
            self.add_argument(f"-{name[0]}", f"--{name}", **kwargs)
        else:
            self.add_argument(f"--{name.replace('_', '-')}", **kwargs)

    def add_args_from_class(self, arg_class: type[ArgumentsBase]) -> None:
        """
        Automatically add arguments to the parser based on a class of ArgInfo instances.

        This method simplifies the process of adding multiple arguments by using a class that
        contains ArgInfo instances as class attributes. It iterates through all ArgInfo instances in
        the provided class and adds them to the parser using `add_argument_from_info`.

        Args:
            arg_class: A class that inherits from ArgumentsBase and contains ArgInfo instances as
                class attributes.

        Example usage:
            class MyArguments(ArgumentsBase):
                file = ArgInfo(help="Input file path", type=str, required=True)
                verbose = ArgInfo(help="Increase output verbosity", action="store_true")

            parser = ArgParser(description="My program description")
            parser.add_args_from_class(MyArguments)
        """
        for field_name, arg_info in arg_class.as_dict().items():
            self.add_argument_from_info(field_name, arg_info)
