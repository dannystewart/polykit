# ruff: noqa: D212, D415
"""
# DSEnv

DSEnv is a utility class that manages environment variables in a friendly way.

This class allows you to add environment variables with type conversion, validation, and secret
masking. Variables can be accessed as attributes. Defaults to loading environment variables from
`.env` and `~/.env`, but also uses the current environment and allows specifying custom files.

## Usage

```python
# Basic usage with default values of .env and ~/.env
env = DSEnv()

# Custom .env file
env = DSEnv(env_file="~/.env.local")

# Multiple .env files (processed in order, so later files take precedence)
env = DSEnv(env_file=["~/.env", "~/.env.local"])

# Add variables with automatic attribute names
env.add_var(
    "SSH_PASSPHRASE",  # Access as env.ssh_passphrase
    description="SSH key passphrase",
    secret=True,
)

# Add variables with custom attribute names
env.add_var(
    "MYSQL_PASSWORD",
    attr_name="db_password",  # Access as env.db_password
    description="MySQL password for upload user",
    secret=True,
)

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
```
"""

from __future__ import annotations

from .dsenv import DSEnv
from .env_var import EnvVar
