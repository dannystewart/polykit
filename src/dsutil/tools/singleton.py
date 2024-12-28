from __future__ import annotations

from threading import Lock
from typing import Any


class Singleton(type):
    """Thread-safe metaclass for creating singleton classes.

    This metaclass ensures only one instance of a class is created even when accessed from multiple
    threads. Use it by setting it as the metaclass in the class definition.

    Example:
        class MyService(metaclass=Singleton):
            def __init__(self, config: str = "default"):
                self.config = config
                self._initialized = False

            def initialize(self) -> None:
                if not self._initialized:
                    # Perform one-time initialization
                    self._initialized = True

        # Usage:
        service1 = MyService(config="custom")  # Creates new instance
        service2 = MyService(config="other")   # Returns existing instance
        assert service1 is service2            # True
        assert service1.config == "custom"     # True

    Notes:
        - The first call to the class constructor creates the singleton instance.
        - Subsequent calls return the same instance regardless of arguments.
        - Constructor arguments are only used for the first instantiation.
        - Thread-safe implementation prevents race conditions during instantiation.
    """

    __instances = {}
    __locks: dict[type, Lock] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create a new instance of the class if one does not already exist."""
        if cls not in cls.__locks:
            cls.__locks[cls] = Lock()

        with cls.__locks[cls]:
            if cls not in cls.__instances:
                instance = super().__call__(*args, **kwargs)
                cls.__instances[cls] = instance
        return cls.__instances[cls]
