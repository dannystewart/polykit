"""This is a delightful Python utility library that brings power and personality to your toolkit.

It contains various helpers refined through years of practical development, including an elegant
logger, an environment variable manager, a path helper, database interfaces, file and media
processing, and various other helpers that make common tasks a little easier or more joyful.
Developed for personal use, but always to high standards of quality and flexibility.

**Note:** This library is constantly evolving, so for stability you may want to pin specific
versions for now. I try to be careful about breaking changes but development is still very active.

## Features

Some of the features include:

- `LocalLogger` for elegant and sophisticated logging that you'll love
- `EnvManager` for clear setup and access to environment variables
- `PathKeeper` for convenient cross-platform access to common paths
- Thread-safe `Singleton` metaclass for use in any project
- Drop-in `argparse` replacement with easier formatting
- Simple helper for comparing files and showing diffs
- Database helper interfaces for MySQL and SQLite
- Helpers for highly customizable copying, deleting, and listing of files
- Media helpers for audio and video transcoding using `ffmpeg`
- Notification helpers for email and Telegram
- Simple progress indicators and helpers for common shell tasks
- Loading animations that are both simple and charming
- Comprehensive collection of text manipulation tools
- Various time parsers and utilities, including a time-aware logger

## Installation

To install the library, simply run:

```bash
pip install dsbase
```

## Personal Scripts

If you want to peruse my expansive collection of personal scripts, please head over to the
[**dsbin**](https://github.com/dannystewart/dsbin/) library.
"""  # noqa: D415

from __future__ import annotations

from dsbase.animate import WalkingMan
from dsbase.env import EnvManager
from dsbase.files import FileManager
from dsbase.log import LocalLogger, TimeAwareLogger
from dsbase.media import MediaManager
from dsbase.paths import PathKeeper
from dsbase.text import Text
from dsbase.time import Time
from dsbase.util import ArgParser, Singleton
