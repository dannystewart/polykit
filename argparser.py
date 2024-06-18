import argparse
import textwrap


class CustomHelpFormatter(argparse.HelpFormatter):
    """
    Format a help message for argparse. It allows for customizing the column width of the arguments
    and help text. You would use this class by passing it as the formatter_class argument to the
    ArgumentParser constructor, like the below example.

        parser = argparse.ArgumentParser(description=__doc__, formatter_class=lambda prog: CustomHelpFormatter(prog, max_help_position=24, width=100))

    But to make your life easier, just use the ArgParser class below, which uses this formatter by
    default and allows you to specify the column widths as arguments.
    """

    def __init__(self, prog: str, max_help_position: int = 24, width: int = 120) -> None:
        super().__init__(prog, max_help_position=max_help_position, width=width)
        self.custom_max_help_position = max_help_position

    def _split_lines(self, text: str, width: int) -> list[str]:
        return textwrap.wrap(text, width)

    def _format_action(self, action: str) -> str:
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
    """

    def __init__(self, *args, **kwargs):
        max_help_position = kwargs.pop("arg_width", 24)
        width = kwargs.pop("max_width", 120)
        super().__init__(
            *args,
            **kwargs,
            formatter_class=lambda prog: CustomHelpFormatter(
                prog, max_help_position=max_help_position, width=width
            ),
        )
