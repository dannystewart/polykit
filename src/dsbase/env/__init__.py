# ruff: noqa: D212, D415

"""
# EnvManager

EnvManager is a utility class that manages environment variables in a friendly way.

This class allows you to add environment variables with type conversion, validation, and secret
masking. Variables can be accessed as attributes.

Environment Loading Strategy:
1. Loads from .env files in parent directories (up to user's home directory)
2. Loads from the current directory's .env file
3. Loads from ~/.env (user's home directory)
4. Uses current environment variables
5. Allows specifying custom files that override all of the above

This hierarchical approach means more specific configurations (closer to the current directory)
override broader ones. For example, if you have /home/user/.env and /home/user/project/.env,
variables in the project-specific file will take precedence.

For detailed logging for EnvManager itself, set the ENV_DEBUG environment variable to '1'.

## Usage

```python
# Basic usage with default values
env_man = EnvManager()

# Custom .env file
env_man = EnvManager(env_file="~/.env_man.local")

# Multiple .env files (processed in order, so later files take precedence)
env_man = EnvManager(env_file=["~/.env", "~/.env.local"])

# Add variables with automatic attribute names
env_man.add_var(
    "SSH_PASSPHRASE",  # Access as env_man.ssh_passphrase
    description="SSH key passphrase",
    secret=True,
)

# Add variables with custom attribute names
env_man.add_var(
    "MYSQL_PASSWORD",
    attr_name="db_password",  # Access as env_man.db_password
    description="MySQL password for upload user",
    secret=True,
)

# Add boolean variable with smart string conversion
env_man.add_bool("DEBUG_MODE", description="Enable debug mode")

# Add a standard debug flag
env_man.add_debug_var()

# Validate all variables - raises ValueError if any are invalid
try:
    env_man.validate_all()
except ValueError as e:
    print(f"Environment validation failed: {e}")
    # Handle error appropriately

# Use variables through attributes
ssh_pass = env_man.ssh_passphrase
db_pass = env_man.db_password

# Or use traditional get() method (with optional default value)
debug_mode = env_man.get("DEBUG_MODE", False)

# Get all values (with secrets masked)
all_values = env_man.get_all_values()
print(all_values)

# Check if debug is enabled and get appropriate log level
if env_man.debug_enabled:
    print(f"Debug is enabled, log level: {env_man.log_level}")
```

## Features

- Type conversion and validation
- Secret masking for sensitive values
- Attribute-style access to variables
- Smart boolean conversion
- Default value handling
- Multiple .env file support
- Debug mode detection
"""

from __future__ import annotations

from .env_manager import EnvManager
