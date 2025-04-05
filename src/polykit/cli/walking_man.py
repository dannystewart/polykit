from __future__ import annotations

import sys
from contextlib import AbstractContextManager, nullcontext
from threading import Event, Thread
from typing import TYPE_CHECKING, ClassVar

from polykit.formatters import color as colorize
from polykit.shell import handle_interrupt

if TYPE_CHECKING:
    from types import TracebackType

    from polykit.formatters.types import TextColor


class WalkingMan:
    """A cute and entertaining Walking Man <('-'<) animation for tasks that take time.

    Walking Man is the unsung hero who brings a bit of joy to operations that would otherwise be
    frustrating or tedious. He's a simple character, but he's always there when you need him.
    """

    # The ASCII, the myth, the legend: it's Walking Man himself
    CHARACTER_LEFT: ClassVar[str] = "<('-'<) "
    CHARACTER_RIGHT: ClassVar[str] = " (>'-')>"

    # Default color for Walking Man (cyan is his favorite)
    COLOR: ClassVar[TextColor | None] = "cyan"

    # Width in characters before Walking Man turns around
    WIDTH: ClassVar[int] = 25

    # Default animation speed (seconds between frames)
    SPEED: ClassVar[float] = 0.2

    def __init__(
        self,
        loading_text: str | None = None,
        color: TextColor | None = COLOR,
        speed: float = SPEED,
    ):
        self.loading_text: str | None = loading_text
        self.color: TextColor | None = color
        self.speed: float = speed
        self.width: int = self.WIDTH
        self.animation_thread: Thread | None = None
        self._stop_event: Event = Event()

    def __enter__(self):
        """Start Walking Man when entering the context manager."""
        self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Stop Walking Man when exiting the context manager."""
        self.stop()

        # Clear Walking Man when done
        WalkingMan.clear(line_above=bool(self.loading_text))

    @handle_interrupt()
    def start(self) -> None:
        """Start the Walking Man animation."""
        self._stop_event.clear()

        self.animation_thread = Thread(target=self._show_animation)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    @handle_interrupt()
    def stop(self) -> None:
        """Stop the Walking Man animation."""
        if self.animation_thread and self.animation_thread.is_alive():
            self._stop_event.set()
            self.animation_thread.join()

    @handle_interrupt()
    def _show_animation(self) -> None:
        """Run the Walking Man animation until stopped."""
        character = self.CHARACTER_RIGHT
        position = 0
        direction = 1  # 1 for right, -1 for left

        if self.loading_text:
            if self.color:
                print(colorize(self.loading_text, self.color))
            else:
                print(self.loading_text)

        while not self._stop_event.is_set():
            self._print_frame(character, position)
            position += direction

            if position in {0, self.width}:
                direction *= -1
                character = self.CHARACTER_LEFT if direction == -1 else self.CHARACTER_RIGHT

    @handle_interrupt()
    def _print_frame(self, character: str, position: int) -> None:
        """Print a single frame of the Walking Man animation."""
        colored_character = colorize(character, self.color) if self.color else character
        print(" " * position + colored_character, end="\r")

        # Use the customizable speed for the animation
        self._stop_event.wait(self.speed)

    @staticmethod
    def clear(line_above: bool = False) -> None:
        """Clear Walking Man if he gets stuck."""
        if line_above:
            sys.stdout.write("\033[F")  # Move cursor up one line
        sys.stdout.write("\033[K")  # Clear the line
        sys.stdout.flush()


def walking_man(
    loading_text: str | None = None,
    color: TextColor | None = WalkingMan.COLOR,
    speed: float = WalkingMan.SPEED,
) -> WalkingMan:
    """Create a Walking Man animation as a context manager. All arguments are optional.

    Args:
        loading_text: Text to print before starting the animation. Defaults to None.
        color: Color to print the animation in. Defaults to cyan.
        speed: Animation speed (seconds between frames). Lower is faster. Defaults to 0.2.

    Usage:
        with walking_man("Loading...", "yellow", 0.1):  # Walking Man go fast
            long_running_function()
    """
    return WalkingMan(loading_text, color, speed)


def conditional_walking_man(
    condition: bool,
    message: str | None = None,
    color: TextColor | None = WalkingMan.COLOR,
    speed: float = WalkingMan.SPEED,
) -> AbstractContextManager[None]:
    """Run the Walking Man animation if the condition is met.

    Args:
        condition: The condition that must be met for the animation to display.
        message: The message to display during the animation. Defaults to None.
        color: The color of the animation. Defaults to cyan.
        speed: Animation speed (seconds between frames). Lower is faster. Defaults to 0.2.

    Usage:
        with conditional_walking_man(verbose, "Loading...", speed=0.05):  # Walking Man go faster
            long_running_function()
    """
    if condition:
        return WalkingMan(message, color, speed)
    return nullcontext()
