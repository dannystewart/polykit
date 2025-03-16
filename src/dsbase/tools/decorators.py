from __future__ import annotations

import functools
import logging
import types
import warnings
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])
C = TypeVar("C", bound=type[Any])


def deprecated(reason: str) -> Callable[[F | C], F | C]:
    """Mark a function or class as deprecated by emitting a warning when used."""

    def decorator(obj: F | C) -> F | C:
        """Decorate a function or class with a warning message and optional category."""
        message = f"{obj.__name__} is deprecated and will be removed in the future. {reason}"
        if isinstance(obj, type):
            return _decorate_class(obj, message, DeprecationWarning)  # type: ignore
        return _decorate_function(obj, message, DeprecationWarning)  # type: ignore

    return decorator


def not_yet_implemented(reason: str) -> Callable[[F | C], F | C]:
    """Mark a function or class as not yet implemented by raising a NotImplementedError."""

    def decorator(obj: F | C) -> F | C:
        """Decorate a function or class with a warning message and optional category."""
        message = f"{obj.__name__} is not yet implemented and cannot be used. {reason}"
        if isinstance(obj, type):
            return _decorate_class(obj, message, UserWarning)  # type: ignore
        return _decorate_function(obj, message, UserWarning)  # type: ignore

    return decorator


def _decorate_function(
    func: Callable[..., Any], message: str, category: type[Warning]
) -> Callable[..., Any]:
    """Decorate a function with a warning message and optional category."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Log a message and emit a warning."""
        instance = args[0] if args and not isinstance(args[0], types.ModuleType) else None
        _log_and_warn(instance, func, message, category)
        if category is UserWarning:
            raise NotImplementedError(message)
        return func(*args, **kwargs)

    return wrapper


def _decorate_class[T](cls: type[T], message: str, category: type[Warning]) -> type[T]:
    """Decorate a class with a warning message and optional category."""

    orig_init = cls.__init__

    @functools.wraps(orig_init)
    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        """Log a message and emit a warning."""
        _log_and_warn(self, orig_init, message, category)
        if category is UserWarning:
            raise NotImplementedError(message)
        orig_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


def _log_and_warn(
    instance: Any | None, func: Callable[..., Any], message: str, category: type[Warning]
) -> None:
    """Log a message and emit a warning."""
    logger = getattr(instance, "logger", None) or logging.getLogger(func.__module__)

    # Temporarily enable the specified warning category for our own code
    with warnings.catch_warnings():
        warnings.simplefilter("always", category)
        warnings.warn(message, category=category, stacklevel=3)

    # Log the message
    logger.log(logging.WARNING if category is DeprecationWarning else logging.ERROR, message)
