"""
Path type implementations for DSPaths.

This module provides different path types for handling various directory structures:

BasePath:
    Base class that provides common path operations and directory creation logic.
    All other path types inherit from this.

PlatformPath:
    Handles platform-specific directories managed by platformdirs:
    - data: Application data
    - cache: Temporary cache files
    - log: Log files
    - state: Application state

UserPath:
    Handles user directories in the home folder:
    - home: User's home directory (~)
    - documents: ~/Documents
    - downloads: ~/Downloads
    - music: ~/Music
    - pictures: ~/Pictures
    Can also handle custom subfolders in home directory.

ConfigPath:
    Extended PlatformPath that adds support for legacy ~/.config locations.
    Allows switching between platform-specific and legacy paths with
    the 'legacy' parameter.

OneDrivePath:
    Handles OneDrive cloud storage paths:
    - macOS: ~/Library/CloudStorage/OneDrive-Personal
    - Windows: ~/OneDrive
    Raises NotImplementedError on unsupported platforms.

Usage:
    These classes are used internally by DSPaths and shouldn't need to be
    instantiated directly. See DSPaths documentation for usage examples.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .paths import DSPaths


@dataclass
class BasePath:
    """Base class for path operations."""

    name: str
    parent: DSPaths
    home_dir: str

    @property
    def dir(self) -> str:
        """Get the base directory."""
        raise NotImplementedError

    def get_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path within this directory."""
        path = os.path.join(self.dir, *paths)
        if self.parent.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path


@dataclass
class PlatformPath(BasePath):
    """Platform-specific paths from platformdirs."""

    @property
    def dir(self) -> str:
        """Get the platform-specific directory."""
        return getattr(self.parent.dirs, f"user_{self.name}_dir")


@dataclass
class UserPath(BasePath):
    """User directory paths like Documents, Downloads, etc."""

    subfolder: str = ""

    @property
    def dir(self) -> str:
        """Get the user directory."""
        if self.subfolder:
            return os.path.join(self.parent.get_home_dir(), self.subfolder)
        return self.parent.get_home_dir()


@dataclass
class ConfigPath(PlatformPath):
    """Config paths with legacy ~/.config support."""

    def get_path(self, *paths: str, no_create: bool = False, legacy: bool = False) -> str:
        """Get a path in the config directory with legacy support."""
        if legacy:
            base = os.path.expanduser(f"~/.config/{self.parent.app_name}")
            path = os.path.join(base, *paths)
        else:
            path = os.path.join(self.dir, *paths)

        if self.parent.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path


@dataclass
class OneDrivePath(BasePath):
    """OneDrive paths with platform-specific base directories."""

    @property
    def dir(self) -> str:
        """Get the OneDrive directory."""
        if sys.platform == "darwin":
            return os.path.join(
                self.parent.get_home_dir(), "Library/CloudStorage/OneDrive-Personal"
            )
        if sys.platform == "win32":
            return os.path.join(self.parent.get_home_dir(), "OneDrive")
        msg = "OneDrive path not supported on this platform."
        raise NotImplementedError(msg)
