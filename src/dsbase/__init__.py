"""
# dsbase: Danny Stewart's Python Utility Library

dsbase provides a collection of utility functions and classes to simplify common programming tasks.

## Installation

```bash
pip install dsbase
```

## Core Features

- **Text Processing**: Color formatting, text manipulation, and pattern matching
- **File Operations**: Simplified file handling, searching, and management
- **Logging**: Customized logging setup with sensible defaults
- **Version Management**: Tools for checking and comparing package versions

See the individual module documentation for more detailed API information.
"""  # noqa: D212, D415

from __future__ import annotations

from dsbase.common import Singleton
from dsbase.log import LocalLogger, TimeAwareLogger
from dsbase.text import Text
from dsbase.time import TZ, TimeParser
from dsbase.tools import configure_traceback
