from __future__ import annotations

# polykit/core/imports.py or polykit/deps.py
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


def optional_import[T](import_func: Callable[..., T], *args: Any, **kwargs: Any) -> T | None:
    """Generic function to handle optional imports.

    Args:
        import_func: Function that imports and returns the dependency.
        *args: Arguments to pass to the import function.
        **kwargs: Keyword arguments to pass to the import function.

    Returns:
        The imported object or None if import fails.
    """
    try:
        return import_func(*args, **kwargs)
    except ImportError:
        return None


def get_halo(*args: Any, **kwargs: Any) -> Any | None:
    """Return a Halo instance if available, otherwise None."""

    def _import() -> Any:
        from halo import Halo

        return Halo(*args, **kwargs)

    return optional_import(_import)


def get_logician(*args: Any, **kwargs: Any) -> Any | None:
    """Return a Logician instance if available, otherwise None."""

    def _import() -> Any:
        from logician import Logician

        return Logician.get_logger(*args, **kwargs)

    return optional_import(_import)


def get_enviromancer(*args: Any, **kwargs: Any) -> Any | None:
    """Return an Enviromancer instance if available, otherwise None."""

    def _import() -> Any:
        from enviromancer import Enviromancer

        return Enviromancer(*args, **kwargs)

    return optional_import(_import)


has_halo = optional_import(lambda: __import__("halo")) is not None
has_logician = optional_import(lambda: __import__("logician")) is not None
has_enviromancer = optional_import(lambda: __import__("enviromancer")) is not None
