from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from dotenv import load_dotenv

from dsbase.log import LocalLogger

from .env_var import EnvVar, VarAdder, default_env_files

if TYPE_CHECKING:
    from collections.abc import Callable
    from logging import Logger

T = TypeVar("T")


@dataclass
class DSEnv:
    """Manage environment variables in a friendly way."""

    env_file: list[Path] | Path | str | None = field(default_factory=default_env_files)
    log_level: str = "info"

    vars: dict[str, EnvVar] = field(default_factory=dict)
    values: dict[str, Any] = field(default_factory=dict)
    attr_names: dict[str, str] = field(default_factory=dict)

    logger: Logger = field(init=False)

    def __post_init__(self):
        """Initialize with default environment variables."""
        self.logger = LocalLogger().get_logger(level=self.log_level)
        if self.env_file:
            env_files = [self.env_file] if isinstance(self.env_file, str | Path) else self.env_file
            for file in env_files:
                full_path = Path(file).expanduser() if isinstance(file, str) else file.expanduser()
                if full_path.exists():
                    self.logger.debug("Loading environment from: %s", full_path)
                    load_dotenv(str(full_path), override=False)

    def add_var(
        self,
        name: str,
        attr_name: str | None = None,
        required: bool = True,
        default: Any = "",
        var_type: Callable[[str], Any] = str,
        description: str = "",
        secret: bool = False,
    ) -> None:
        """Add an environment variable to track.

        Args:
            name: Environment variable name (e.g. 'SSH_PASSPHRASE').
            attr_name: Optional attribute name override (e.g. 'ssh_pass').
            required: Whether this variable is required.
            default: Default value if not required.
            var_type: Type to convert value to (e.g. int, float, str, bool).
            description: Human-readable description.
            secret: Whether to mask the value in logs.

        Raises:
            ValueError: If the variable is required and not set.
        """
        # Use provided attr_name or convert ENV_VAR_NAME to env_var_name
        attr = attr_name or name.lower()
        self.attr_names[attr] = name

        self.vars[name] = EnvVar(
            name=name.upper(),
            required=required,
            default=default,
            var_type=var_type,
            description=description,
            secret=secret,
        )

        # Validate the variable as soon as it's added
        try:
            self.get(name)
        except Exception as e:
            raise ValueError(str(e)) from e

    def add_bool(
        self,
        name: str,
        attr_name: str | None = None,
        required: bool = False,
        default: bool = False,
        description: str = "",
    ) -> None:
        """Add a boolean environment variable with smart string conversion.

        This is a convenience wrapper around add_var() specifically for boolean values.
        It handles various string representations of boolean values in a case-insensitive way.

        Valid input values (case-insensitive):
        - True: 'true', '1', 'yes', 'on', 't', 'y'
        - False: 'false', '0', 'no', 'off', 'f', 'n'

        Args:
            name: Environment variable name (e.g. "ENABLE_FEATURE")
            attr_name: Optional attribute name override (e.g. "feature_enabled")
            required: Whether this variable is required.
            default: Default boolean value if not required.
            description: Human-readable description.
        """
        self.add_var(
            name=name,
            attr_name=attr_name,
            required=required,
            default=default,
            var_type=self.bool_converter,
            description=description,
            secret=False,
        )

    def add_debug_var(
        self,
        name: str = "DEBUG",
        default: bool = False,
        description: str = "Enable debug mode",
    ) -> None:
        """Simple shortcut to add a consistent boolean DEBUG environment variable."""
        self.add_bool(name=name, required=False, default=default, description=description)

    def get(self, name: str, default: Any = None) -> Any:
        """Get the value of an environment variable.

        Raises:
            KeyError: If the given name is unknown.
            ValueError: If the required variable is missing or has an invalid value.
        """
        if name not in self.vars:
            msg = f"Unknown environment variable: {name}"
            raise KeyError(msg)

        # Return the cached value first if we have it
        if name in self.values:
            return self.values[name]

        var = self.vars[name]

        # Try to get the value from the current environment
        value = os.environ.get(name) or os.getenv(name)

        if value is None:  # If there's no environment value, fall back through defaults
            if default is not None:  # Use get() default if provided
                value = default
            elif var.default is not None:  # Fall back to variable's default if defined
                value = var.default
            elif var.required:  # If there are no defaults and it's required, raise an error
                msg = f"Required environment variable {name} not set"
                if var.description:
                    msg += f" ({var.description})"
                raise ValueError(msg)
            else:  # If it's not required and has no default, return None
                return None

        try:
            converted = var.var_type(value)
            self.values[name] = converted
            return converted
        except ValueError as e:
            msg = f"Invalid value for {name}: {e!s}"
            raise ValueError(msg) from e

    def __getattr__(self, name: str) -> Any:
        """Allow accessing variables as attributes.

        Raises:
            AttributeError: If the given name is unknown.
        """
        if name in self.attr_names:
            return self.get(self.attr_names[name])
        msg = f"'{self.__class__.__name__}' has no attribute '{name}'"
        raise AttributeError(msg)

    def _load_env_file(self) -> None:
        """Load variables from .env file."""
        with Path(self.env_file).open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    @staticmethod
    def bool_converter(value: str) -> bool:
        """Convert various string representations to boolean values.

        Handles common truthy/falsey string values in a case-insensitive way:
            - True values: 'true', '1', 'yes', 'on', 't', 'y'
            - False values: 'false', '0', 'no', 'off', 'f', 'n'

        Raises:
            ValueError: If the string cannot be converted to a boolean.
        """
        value = str(value).lower().strip()

        true_values = {"true", "1", "yes", "on", "t", "y"}
        false_values = {"false", "0", "no", "off", "f", "n"}

        if value in true_values:
            return True
        if value in false_values:
            return False

        msg = (
            f"Cannot convert '{value}' to boolean. "
            f"Valid true values: {', '.join(sorted(true_values))}. "
            f"Valid false values: {', '.join(sorted(false_values))}."
        )
        raise ValueError(msg)

    @classmethod
    def create(cls) -> DSEnvBuilder:
        """Create a new environment configuration."""
        return DSEnvBuilder()


class DSEnvBuilder:
    """Builder class for creating a DSEnv instance with type-checked environment variables.

    NOTE: This is unsupported. It's recommended to use the DSEnv class directly.
    """

    def __init__(self):
        self.vars: dict[str, EnvVar] = {}
        self.attr_names: dict[str, str] = {}
        self.values: dict[str, Any] = {}
        self._var_adder = VarAdder(self)

    @property
    def add_var(self) -> VarAdder:
        """Helper property for adding environment variables with type hints."""
        return self._var_adder

    @classmethod
    def __class_getitem__(cls, item: type[T]) -> type[T]:
        return item

    def build(self) -> DSEnv:
        """Create a DSEnv instance with these variables."""
        from dsbase.env.dsenv import DSEnv

        env = DSEnv()
        env.vars = self.vars
        env.attr_names = self.attr_names
        env.values = self.values

        return env
