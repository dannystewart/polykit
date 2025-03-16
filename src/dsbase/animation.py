# ruff: noqa: PLW0603

from __future__ import annotations

import sys
import time
from contextlib import AbstractContextManager, contextmanager, nullcontext
from threading import Thread
from typing import TYPE_CHECKING

from dsbase.shell import handle_keyboard_interrupt
from dsbase.text import ColorName
from dsbase.text import color as colorize

if TYPE_CHECKING:
    from types import TracebackType

# Animation character width
ANIMATION_WIDTH = 30

animation_running = False


class AnimationManager:
    """Manage a cute and entertaining walking animation for actions that take time to complete."""

    def __init__(
        self,
        loading_text: str | None = None,
        color: str | None = None,
        width: int = ANIMATION_WIDTH,
    ):
        self.loading_text = loading_text
        self.color = color
        self.width = width
        self.animation_thread = None

    def __enter__(self):
        """Start the walking animation when entering the context manager."""
        self.animation_thread = start_animation(self.loading_text, self.color, self.width)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Stop the walking animation when exiting the context manager."""
        stop_animation(self.animation_thread)
        if self.loading_text:
            sys.stdout.write("\033[F")  # Move cursor up one line
            sys.stdout.write("\033[K")  # Clear the line
            sys.stdout.flush()


@contextmanager
def walking_animation(
    loading_text: str | None = None,
    color: ColorName | None = None,
    width: int = ANIMATION_WIDTH,
):
    """Manage a walking animation as a context manager. All arguments are optional.

    Args:
        loading_text: Text to print before starting the animation. Defaults to None.
        color: Color to print the animation in. Defaults to None.
        width: The width of the screen for the animation. Defaults to ANIMATION_WIDTH.

    Usage:
        with walking_animation("Loading...", "yellow", 30):
            long_running_function()
    """
    manager = AnimationManager(loading_text, color, width)
    with manager:
        yield


def conditional_animation(
    condition: bool,
    message: str | None = None,
    color: ColorName | None = None,
    width: int = ANIMATION_WIDTH,
) -> AbstractContextManager[None]:
    """Run the walking animation if the condition is met.

    Args:
        condition: The condition that must be met for the animation to display.
        message: The message to display during the animation. Defaults to None.
        color: The color of the animation. Defaults to None.
        width: The width of the screen for the animation. Defaults to ANIMATION_WIDTH.

    Usage:
        with conditional_animation(condition, "Loading..."):
            long_running_function()
    """
    return walking_animation(message, color, width) if condition else nullcontext()


@handle_keyboard_interrupt()
def show_walking_animation(
    loading_text: str | None = None,
    color: ColorName | None = None,
    width: int = ANIMATION_WIDTH,
) -> None:
    """Print a walking animation until the animation_running flag is set to False."""
    character_right = " (>'-')>"
    character_left = "<('-'<) "
    character = character_right
    position = 0
    direction = 1  # 1 for right, -1 for left

    if loading_text:
        if color:
            print(colorize(loading_text, color))
        else:
            print(loading_text)

    while animation_running:
        print_animation_frame(character, position, color)
        position += direction

        if position in {0, width}:
            direction *= -1
            character = character_left if direction == -1 else character_right


@handle_keyboard_interrupt()
def start_animation(
    loading_text: str | None = None,
    color: ColorName | None = None,
    width: int = ANIMATION_WIDTH,
) -> Thread:
    """Start the walking animation.

    Usage (all arguments optional):
        from dsbase.animation import start_animation, stop_animation

        animation_thread = start_animation("Loading...", "yellow", 30)
        stop_animation(animation_thread)

    Args:
        loading_text: Text to print before starting the animation.
        color: Color to print the animation in.
        width: The width of the screen for the animation.

    Returns:
        The thread running the animation.
    """
    global animation_running
    animation_running = True

    animation_thread = Thread(target=show_walking_animation, args=(loading_text, color, width))
    animation_thread.daemon = True  # This makes it killable with Ctrl-C
    animation_thread.start()

    return animation_thread


@handle_keyboard_interrupt()
def stop_animation(animation_thread: Thread) -> None:
    """Stop the walking animation."""
    global animation_running

    animation_running = False

    animation_thread.join()


@handle_keyboard_interrupt()
def print_animation_frame(character: str, position: int, color: ColorName | None = None) -> None:
    """Print a single frame of the walking animation."""
    colored_character = colorize(character, color) if color else character
    print(" " * position + colored_character, end="\r")
    time.sleep(0.2)
