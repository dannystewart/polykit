# ruff: noqa: D212, D415
r"""
DSPaths is a helper class to manage paths (both platform and user) in a friendly way.

Platform-specific paths:
    Linux:
        data:      ~/.local/share/app_name
        config:    ~/.config/app_name
        cache:     ~/.cache/app_name
        logs:      ~/.cache/app_name/logs
        state:     ~/.local/state/app_name
        documents: ~/Documents

    macOS (adds `app_domain` if provided):
        data:      ~/Library/Application Support/app_domain/app_name
        config:    ~/Library/Preferences/app_name
        cache:     ~/Library/Caches/app_name
        logs:      ~/Library/Logs/app_name
        state:     ~/Library/Application Support/app_domain/app_name
        documents: ~/Documents

    Windows:
        data:      C:\\Users\\<user>\\AppData\\Local\\app_author\\app_name
        config:    C:\\Users\\<user>\\AppData\\Local\\app_author\\app_name\\Config
        cache:     C:\\Users\\<user>\\AppData\\Local\\app_author\\app_name\\Cache
        logs:      C:\\Users\\<user>\\AppData\\Local\\app_author\\app_name\\Logs
        state:     C:\\Users\\<user>\\AppData\\Local\\app_author\\app_name
        documents: C:\\Users\\<user>\\Documents
"""

from __future__ import annotations

from .dspaths import DSPaths
