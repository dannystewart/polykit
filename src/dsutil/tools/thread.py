from __future__ import annotations

import atexit
import concurrent
import concurrent.futures
import logging
import os
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, wait
from typing import TYPE_CHECKING

from dsutil.log import LocalLogger

if TYPE_CHECKING:
    from collections.abc import Callable


class LocalThreader:
    """A class that provides methods for starting threads and checking if a thread is active."""

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.executor = ThreadPoolExecutor(max_workers=10)
            self.logger = LocalLogger.setup_logger(f"{self.__class__.__name__}")
            self.active_threads = {}
            self.simple_threads = []
            self.event_dict = {}
            self._initialized = True
            atexit.register(self.shutdown_executor)

    def start(
        self,
        target: Callable,
        args: tuple = (),
        kwargs: dict | None = None,
        daemon: bool = True,
    ) -> threading.Thread:
        """
        Start a simple thread with the given target function and arguments. This method
        should only be used for simple threads that don't need tracking or cleanup.

        Args:
            target: The function to be executed by the thread.
            args: The arguments to be passed to the target function.
            kwargs: The keyword arguments to be passed to the target function.
            daemon: Whether the thread should be a daemon thread.
        """
        if kwargs is None:
            kwargs = {}
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=daemon)
        thread.start()
        self.simple_threads.append(thread)
        return thread

    def is_thread_active(self, key: str) -> bool:
        """Check if a thread with the given key is active."""
        return future.running() if (future := self.active_threads.get(key)) else False

    def complete(self, key: str) -> None:
        """Mark a thread as completed and remove it from the active threads dictionary."""
        future = self.active_threads.get(key)
        if future and future.running():
            future.result()
            del self.active_threads[key]
            if key in self.event_dict:
                self.event_dict[key].set()  # Set the event to signal task completion

    def start_with_executor(
        self,
        target: Callable,
        args: tuple = (),
        kwargs: dict | None = None,
        key: str | None = None,
        timeout: float | None = None,
        on_complete: Callable | None = None,
        on_error: Callable | None = None,
    ) -> bool:
        """
        Start a new thread with the given target function and arguments.

        Args:
            target: The function to be executed by the thread.
            args: The arguments to be passed to the target function.
            kwargs: The keyword arguments to be passed to the target function.
            key: The key associated with the thread.
            timeout: Maximum time to wait for the thread to finish.
            on_complete: Optional callback function to be called upon successful completion.
            on_error: Optional callback function to be called if an error occurs.

        Returns:
            True if the thread was started successfully, False otherwise.
        """
        if key and key in self.active_threads:
            future = self.active_threads[key]
            if future.running():
                self.logger.debug("Thread with key %s is already running.", key)
                return False

        if kwargs is None:
            kwargs = {}

        event = threading.Event()
        if key:
            self.event_dict[key] = event  # Add the event to the event dictionary

        future = self.executor.submit(
            self._start_thread_wrapper, target, args, kwargs, on_complete, on_error, event
        )

        if key:
            self.active_threads[key] = future

        if timeout is not None:
            try:
                future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                self.logger.warning("Thread %s timed out.", key)
                future.cancel()

        return True

    def _start_thread_wrapper(
        self,
        target: Callable,
        args: tuple,
        kwargs: dict,
        on_complete: Callable | None,
        on_error: Callable | None,
        event: threading.Event,
    ) -> None:
        """Start a thread with error handling."""
        try:
            target(*args, **kwargs)
            if on_complete:
                on_complete()
        except Exception as e:
            self.handle_thread_exception(e, target, *args, **kwargs)
            if on_error:
                on_error(e)
        finally:
            event.set()  # Set the event to signal task completion

    def start_thread_with_error_handling(self, target: Callable, args: tuple, kwargs: dict) -> None:
        """Apply error handling to the thread's target function."""
        try:
            target(*args, **kwargs)
        except Exception as e:
            self.handle_thread_exception(e, target, *args, **kwargs)

    @staticmethod
    def handle_thread_exception(
        e: Exception,
        target: Callable,
        *args: list,  # noqa: ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> None:
        """
        Handle exceptions for functions executed in threads, similar to @catch_errors.

        Args:
            e: The caught exception.
            target: The target function where the exception occurred.
            args: The arguments passed to the target function.
            kwargs: The keyword arguments passed to the target function.
        """
        # Make sure we don't log the same exception more than once
        if getattr(e, "_logged", False):
            return

        # Get the logger from the module of the target function
        logger = logging.getLogger(target.__module__)

        # Format error message with exception type
        exception_type = type(e).__name__
        func_name = target.__name__
        error = str(e)
        error_msg = f"{exception_type}: An error occurred in {func_name}: {error}"

        # Log the error message
        logger.error(error_msg)

        # If enabled and the stderr stream is a TTY, print the traceback
        if os.getenv("LOG_THREAD_TRACEBACK", "0") == 1 and sys.stderr.isatty():
            tb = traceback.format_exc()
            sys.stderr.write(tb)

        # Mark that the exception has been logged to prevent future duplicate logs
        setattr(e, "_logged", True)

    def cleanup(self, cleanup_key: str | None = None) -> int | None:
        """
        Cleanup references to finished threads. If a key is provided, remove the thread with the
        given key if it's no longer active. If no key is provided, clean up all finished threads.

        Args:
            cleanup_key: The key associated with the thread to clean up. Defaults to None.

        Returns:
            The number of threads cleaned up.
        """
        # If a specific key is provided, clean up only that thread
        if cleanup_key:
            future = self.active_threads.get(cleanup_key)
            if future and (future.done() or future.cancelled()):
                del self.active_threads[cleanup_key]
                if cleanup_key in self.event_dict:
                    self.event_dict[cleanup_key].set()  # Set the event to signal task completion
            return

        # No specific key provided, clean up all completed or cancelled futures
        completed_or_cancelled_keys = [
            key
            for key, future in self.active_threads.items()
            if future.done() or future.cancelled()
        ]
        for key in completed_or_cancelled_keys:
            del self.active_threads[key]
            if key in self.event_dict:
                self.event_dict[key].set()  # Set the event to signal task completion

        if threads_cleaned := len(completed_or_cancelled_keys):
            self.logger.debug(
                "Ran thread cleanup. Cleaned up %d thread%s.",
                threads_cleaned,
                "s" if threads_cleaned > 1 else "",
            )

    def wait_for_all_threads(self, timeout: int = 5) -> None:
        """
        Wait for all active threads to finish or until timeout.

        Args:
            timeout: Maximum time to wait for each thread.
        """
        self.logger.info("Waiting for all threads to finish...")

        # Wait for futures
        for key, future in list(self.active_threads.items()):
            try:
                future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                self.logger.warning("Thread %s did not finish in the allotted time.", key)
            except Exception as e:
                self.logger.error("Error while executing thread %s: %s", key, str(e))

        # Wait for simple threads
        for thread in self.simple_threads:
            thread.join(timeout=timeout)
            if thread.is_alive():
                self.logger.warning(
                    "Simple thread %s did not finish in the allotted time.", thread.name
                )

        self.logger.info("Waiting for all event signals to complete...")
        for event in self.event_dict.values():
            event.wait()  # Wait for all events to be set

        self.cleanup()  # After waiting, clean up the active_threads dictionary to remove done futures

    def schedule_callback_after_all_threads(
        self, callback: Callable, *args: list, **kwargs: dict
    ) -> None:
        """Schedules a callback function to be called after all threads have finished."""
        if self.active_threads:
            wait(self.active_threads.values())
        callback(*args, **kwargs)

    def shutdown_executor(self) -> None:
        """Shut down the thread pool executor gracefully."""
        self.logger.info("Shutting down the thread pool executor...")
        self.executor.shutdown(wait=True)
        self.logger.info("Thread pool executor shut down gracefully.")

    def monitor_threads(self, interval: float = 10.0) -> None:
        """Periodically log the status of active threads."""

        def log_status() -> None:
            while True:
                for key, future in self.active_threads.items():
                    status = (
                        "running"
                        if future.running()
                        else "done"
                        if future.done()
                        else "cancelled"
                        if future.cancelled()
                        else "unknown"
                    )
                    self.logger.debug("Thread %s status: %s", key, status)
                time.sleep(interval)

        self.start(target=log_status)
