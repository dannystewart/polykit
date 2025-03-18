from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from .dsenv import DSEnvBuilder

T = TypeVar("T")


def default_env_files() -> list[Path]:
    """Default .env files to load."""
    return [Path(".env"), Path("~/.env").expanduser()]


@dataclass
class EnvVar:
    """Represents an environment variable with validation and type conversion.

    Args:
        name: Environment variable name.
        required: Whether this variable is required.
        default: Default value if not required.
        var_type: Type to convert value to (e.g., int, float, str, bool).
        description: Human-readable description of the variable.
        secret: Whether to mask the value in logs.

    NOTE: var_type is used as a converter function to wrap the provided data. This means it can also
          use custom conversion functions to get other types of data with convert(value) -> Any.

    Usage:
        env.add_var(
            "SSH_PASSPHRASE",
            description="Passphrase for SSH key",
            secret=True
        )
        env.add_var(
            "DEBUG_LEVEL",
            required=False,
            default="info",
            description="Logging level"
        )
        env.add_var(
            "MAX_UPLOAD_SIZE",
            var_type=int,
            required=False,
            default=10485760,
            description="Maximum upload size in bytes"
        )
    """

    name: str
    required: bool = False
    default: Any = None
    var_type: Callable[[str], Any] = str
    description: str = ""
    secret: bool = False

    def __post_init__(self) -> None:
        if not self.required and self.default is None:
            msg = f"Non-required variable {self.name} must have a default value"
            raise ValueError(msg)


class VarAdder:
    """Helper class for adding environment variables to a DSEnvBuilder instance."""

    def __init__(self, builder: DSEnvBuilder):
        self.builder = builder

    def __getitem__(self, type_hint: type[T]) -> Callable[..., DSEnvBuilder]:
        def add(
            name: str,
            attr_name: str | None = None,
            required: bool = True,
            default: T | None = None,
            description: str = "",
            secret: bool = False,
        ) -> DSEnvBuilder:
            attr = attr_name or name.lower()
            self.builder.attr_names[attr] = name

            self.builder.vars[name] = EnvVar(
                name=name,
                required=required,
                default=default,
                var_type=type_hint,
                description=description,
                secret=secret,
            )
            return self.builder

        return add
