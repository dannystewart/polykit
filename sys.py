import subprocess
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import wraps
from threading import Thread


@contextmanager
def popen(*args, **kwargs):
    """
    A general context manager for running subprocesses safely.

    This function abstracts away the setup and teardown logic for running subprocesses,
    handling their cleanup regardless of whether they exit normally or raise an exception.

    Usage:
        with general_popen(['command', 'arg1', 'arg2'], stdout=subprocess.PIPE) as proc:
            stdout, stderr = proc.communicate()

    @param args: Positional arguments to pass to subprocess.Popen.
    @param kwargs: Keyword arguments to pass to subprocess.Popen.
    @yield: The Popen process object.
    """
    process = subprocess.Popen(*args, **kwargs)
    try:
        yield process
    finally:
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        if process.stdin:
            process.stdin.close()

        process.terminate()
        try:
            process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def run_in_thread(func):
    """Decorator to run a function in a separate thread."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def run_in_executor(func):
    """Decorator to run a function in ThreadPoolExecutor."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

    return wrapper
