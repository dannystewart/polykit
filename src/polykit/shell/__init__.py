"""### System Operations

```python
from polykit.shell import is_root_user, acquire_sudo
from polykit.core import Singleton

# Check permissions and elevate if needed
if not is_root_user() and not acquire_sudo():
    print("This operation requires admin privileges")

# Create thread-safe singleton classes with minimal code
class ConfigManager(metaclass=Singleton):
    \"""Configuration is loaded only once and shared throughout the app.\"""
```

### Development Tools

```python
from polykit.core import deprecated, not_yet_implemented
from polykit.shell import log_traceback

# Mark APIs for future removal
@deprecated("Use new_function() instead.")
def old_function():
    # Users get helpful warning when using this

# Placeholder for planned features
@not_yet_implemented("Coming in version 2.0")
def future_feature():
    # Raises clear error if accidentally called

# Colorized, formatted tracebacks
try:
    risky_operation()
except Exception:
    log_traceback()  # Pretty, syntax-highlighted traceback
```
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .interrupt import async_handle_interrupt, async_with_handle_interrupt, handle_interrupt
from .permissions import acquire_sudo, is_root_user
