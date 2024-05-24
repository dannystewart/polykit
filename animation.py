import threading
import time

from termcolor import colored

from dsutil.shell import handle_keyboard_interrupt

ANIMATION_RUNNING = False


@handle_keyboard_interrupt()
def print_animation_frame(character, position, color):
    """Print a single frame of the walking animation."""
    colored_character = colored(character, color) if color else character
    print(" " * position + colored_character, end="\r")
    time.sleep(0.2)


@handle_keyboard_interrupt()
def show_walking_animation(loading_text=None, color=None, width=40):
    """Print a walking animation until the animation_running flag is set to False."""
    character_right = " (>'-')>"
    character_left = "<('-'<) "
    character = character_right
    position = 0
    direction = 1  # 1 for right, -1 for left

    if loading_text:
        print(loading_text)

    while ANIMATION_RUNNING:
        print_animation_frame(character, position, color)
        position += direction

        if position in (0, width):
            direction *= -1
            character = character_left if direction == -1 else character_right


@handle_keyboard_interrupt()
def start_animation(loading_text=None, color=None, width=40):
    """
    Start the walking animation.

    Usage (all arguments optional):
        from dsutil import animation
        animation_thread = animation.start_animation("Loading...", "yellow", 40)
        animation.stop_animation(animation_thread)

    Args:
        loading_text (str): Text to print before starting the animation.
        color (str): Color to print the animation in.
        width (int): The width of the screen for the animation.

    Returns:
        threading.Thread: The thread running the animation.
    """
    global ANIMATION_RUNNING  # pylint: disable=global-statement
    ANIMATION_RUNNING = True

    animation_thread = threading.Thread(target=show_walking_animation, args=(loading_text, color, width))
    animation_thread.daemon = True  # This makes it killable with Ctrl-C
    animation_thread.start()

    return animation_thread


@handle_keyboard_interrupt()
def stop_animation(animation_thread):
    """Stop the walking animation."""
    global ANIMATION_RUNNING  # pylint: disable=global-statement

    ANIMATION_RUNNING = False

    animation_thread.join()
