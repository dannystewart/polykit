"""A delightful Python utility library to bring power and personality to your toolkit.

DSBase contains various tools and utilities refined through years of practical development, including a path helper, database interfaces, file and media processing, and various other helpers that make common tasks a little easier or more joyful. Developed for personal use, but always to high standards of quality and flexibility.

## Installation

```bash
pip install dsbase
```

## Features

Some of the features include:

- Simple helper for comparing files and showing diffs
- Database helper interfaces for MySQL and SQLite
- Helpers for highly customizable copying, deleting, and listing of files
- Media helpers for audio and video transcoding using `ffmpeg`
- Notification helpers for email and Telegram
- Simple progress indicators and helpers for common shell tasks
- Loading animations that are both simple and charming
- Comprehensive collection of text manipulation tools
- Various time parsers and utilities
"""  # noqa: D415, W505

from __future__ import annotations

from dsbase.files import FileManager
from dsbase.media import MediaManager
