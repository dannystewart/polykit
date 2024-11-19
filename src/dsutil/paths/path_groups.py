from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dsutil.log import LocalLogger

if TYPE_CHECKING:
    from .paths import DSPaths

logger = LocalLogger.setup_logger()


@dataclass
class PathGroup:
    """Group of related paths (platform, user, etc)."""

    paths: DSPaths
    base: str

    def __call__(self, *parts: str, no_create: bool = False) -> str:
        """Get a path within this group."""
        path = os.path.join(self.base, *parts)
        if not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path


@dataclass
class ConfigGroup(PathGroup):
    """Handle config paths with legacy support."""

    def __call__(self, *parts: str, no_create: bool = False, legacy: bool = False) -> str:
        """Get a path within the config group."""
        base = os.path.expanduser(f"~/.config/{self.paths.app_name}") if legacy else self.base
        path = os.path.join(base, *parts)
        if not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path


@dataclass
class OneDriveGroup:
    """Handle OneDrive paths with platform-specific base directories."""

    paths: DSPaths

    def __call__(self, *parts: str, no_create: bool = False) -> str:
        """Get a path within the OneDrive directory."""
        path = os.path.join(self.base, *parts)
        if not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def base(self) -> str:
        """Get the platform-specific OneDrive base directory."""
        if sys.platform == "darwin":
            return os.path.join(self.paths.home.base, "Library/CloudStorage/OneDrive-Personal")
        if sys.platform == "win32":
            return os.path.join(self.paths.home.base, "OneDrive")
        msg = "OneDrive path not supported on this platform."
        raise NotImplementedError(msg)
