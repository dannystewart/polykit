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


@dataclass
class EnvVar:
    """
    Represents an environment variable with validation and type conversion.

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
    required: bool = True
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
    """
    Manage environment variables in a DS-friendly way.

    This class allows you to add environment variables with type conversion, validation, and secret
    masking. Variables can be accessed as attributes. Defaults to loading environment variables from
    ~/.env, but also uses the current environment and allows specifying custom files.

    Usage:
        # Basic usage with default ~/.env
            env = DSEnv("dsmusic")

        # Custom .env file
            env = DSEnv("dsmusic", env_file="~/.env.local")

        # Multiple .env files (processed in order)
            env = DSEnv("dsmusic", env_file=["~/.env", "~/.env.local"])

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

        # Validate all variables
            if errors := env.validate():
                for error in errors:
                    raise ValueError(error)

        # Use variables through attributes
            ssh_pass = env.ssh_passphrase
            db_pass = env.db_password

        # Or use traditional get() method
            ssh_pass = env.get("SSH_PASSPHRASE")

        # Print status (with secrets masked)
            env.print_status()
    """

    app_name: str
    env_file: str | list[str] | None = "~/.env"
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
        """
        Add an environment variable to track.

        Args:
            name: Environment variable name (e.g., "SSH_PASSPHRASE").
            attr_name: Optional attribute name override (e.g., "ssh_pass").
            required: Whether this variable is required.
            default: Default value if not required.
            var_type: Type to convert value to (e.g., int, float, str, bool).
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

    def validate(self) -> list[str]:
        """
        Validate all environment variables.

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

    def get(self, name: str) -> Any:
        """Get the value of an environment variable."""
        if name not in self._vars:
            msg = f"Unknown environment variable: {name}"
            raise KeyError(msg)

        # Return cached value if we have it
        if name in self._values:
            return self._values[name]

        var = self._vars[name]

        # First, try to get the value from the current environment
        value = os.environ.get(name)

        # If not found in the current environment, use the value from .env file (if any)
        if value is None:
            value = os.getenv(name)

        if value is None:
            if var.required:
                msg = f"Required environment variable {name} not set"
                if var.description:
                    msg += f" ({var.description})"
                raise ValueError(msg)
            value = var.default

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
