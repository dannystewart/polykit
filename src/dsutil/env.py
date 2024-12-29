from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

from dotenv import load_dotenv

from dsutil.log import LocalLogger

if TYPE_CHECKING:
    from collections.abc import Callable
    from logging import Logger

T = TypeVar("T")


def default_env_files() -> list[str]:
    """Default .env files to load."""
    return [".env", "~/.env"]


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


@dataclass
class DSEnv:
    """Manage environment variables in a DS-friendly way.

    This class allows you to add environment variables with type conversion, validation, and secret
    masking. Variables can be accessed as attributes. Defaults to loading environment variables from
    .env and ~/.env, but also uses the current environment and allows specifying custom files.

    Usage:
        # Basic usage with default values of .env and ~/.env
            env = DSEnv()

        # Custom .env file
            env = DSEnv(env_file="~/.env.local")

        # Multiple .env files (processed in order, so later files take precedence)
            env = DSEnv(env_file=["~/.env", "~/.env.local"])

        # Add variables with automatic attribute names
            env.add_var(
                "SSH_PASSPHRASE",
                description="SSH key passphrase",
                secret=True,
            )
        # Access as env.ssh_passphrase

        # Add variables with custom attribute names
            env.add_var(
                "MYSQL_PASSWORD",
                attr_name="db_password",
                description="MySQL password for upload user",
                secret=True,
            )
        # Access as env.db_password

        # Add boolean variable with smart string conversion
            env.add_bool("DEBUG_MODE", description="Enable debug mode")

        # Validate all variables
            if errors := env.validate():
                for error in errors:
                    raise ValueError(error)

        # Use variables through attributes
            ssh_pass = env.ssh_passphrase
            db_pass = env.db_password

        # Or use traditional get() method (with optional default value)
            ssh_pass = env.get("DEBUG_MODE", False)

        # Print status (with secrets masked)
            env.print_status()
    """

    env_file: str | list[str] | None = field(default_factory=default_env_files)
    log_level: str = "info"
    validate_on_add: bool = True

    _vars: dict[str, EnvVar] = field(default_factory=dict)
    _values: dict[str, Any] = field(default_factory=dict)
    _attr_names: dict[str, str] = field(default_factory=dict)

    logger: Logger = field(init=False)

    def __post_init__(self):
        """Initialize with default environment variables."""
        self.logger = LocalLogger.setup_logger(level=self.log_level)
        if self.env_file:
            env_files = [self.env_file] if isinstance(self.env_file, str) else self.env_file
            for file in env_files:
                expanded_path = os.path.expanduser(file)
                if os.path.exists(expanded_path):
                    self.logger.debug("Loading environment from: %s", expanded_path)
                    load_dotenv(expanded_path, override=False)

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
            name: Environment variable name (e.g. "SSH_PASSPHRASE").
            attr_name: Optional attribute name override (e.g. "ssh_pass").
            required: Whether this variable is required.
            default: Default value if not required.
            var_type: Type to convert value to (e.g. int, float, str, bool).
            description: Human-readable description.
            secret: Whether to mask the value in logs.
        """
        # Use provided attr_name or convert ENV_VAR_NAME to env_var_name
        attr = attr_name or name.lower()
        self._attr_names[attr] = name

        self._vars[name] = EnvVar(
            name=name,
            required=required,
            default=default,
            var_type=var_type,
            description=description,
            secret=secret,
        )

        # Validate immediately if enabled
        if self.validate_on_add:
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

    def validate(self) -> list[str]:
        """Validate all environment variables.

        Returns:
            List of error messages, empty if all valid
        """
        errors = []
        for name, _ in self._vars.items():
            try:
                self.get(name)
            except Exception as e:
                errors.append(str(e))
        return errors

    def get(self, name: str, default: Any = None) -> Any:
        """Get the value of an environment variable.

        Args:
            name: The environment variable's name.
            default: Default value if not found (overrides variable's default).

        Raises:
            KeyError: If the given name is unknown.
            ValueError: If the required variable is missing or has an invalid value.

        Returns:
            The value of the environment variable.
        """
        if name not in self._vars:
            msg = f"Unknown environment variable: {name}"
            raise KeyError(msg)

        # Return the cached value first if we have it
        if name in self._values:
            return self._values[name]

        var = self._vars[name]

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
            self._values[name] = converted
            return converted
        except ValueError as e:
            msg = f"Invalid value for {name}: {str(e)}"
            raise ValueError(msg) from e

    def __getattr__(self, name: str) -> Any:
        """Allow accessing variables as attributes."""
        if name in self._attr_names:
            return self.get(self._attr_names[name])
        msg = f"'{self.__class__.__name__}' has no attribute '{name}'"
        raise AttributeError(msg)

    def _load_env_file(self) -> None:
        """Load variables from .env file."""
        with open(self.env_file) as f:
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

        Args:
            value: String value to convert to boolean

        Raises:
            ValueError: If the string cannot be converted to a boolean.

        Returns:
            Converted boolean value.
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
