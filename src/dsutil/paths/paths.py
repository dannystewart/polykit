r"""
DSPaths is a helper class to manage paths (both platform and user) in a DS-friendly way. Paths to be
created are defined in PATHS at the top of the module.

Platform-specific paths:
    Linux:
        data:      ~/.local/share/app_name
        config:    ~/.config/app_name
        cache:     ~/.cache/app_name
        logs:      ~/.cache/app_name/logs
        state:     ~/.local/state/app_name
        documents: ~/Documents

    macOS (adds app_domain if provided):
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

import os
import sys
from dataclasses import dataclass

from platformdirs import PlatformDirs

from .path_groups import OneDriveGroup, PathGroup

from dsutil.log import LocalLogger

logger = LocalLogger.setup_logger()


@dataclass
class DSPaths:
    """
    Manage paths in a DS-friendly way. Paths to be created are stored in PATHS at the module level.

    Args:
        app_name: Name of the application.
        app_author: Author of the application.
        app_domain: Domain for macOS paths.
        version: Application version.
        create_dirs: Whether to create directories if they don't exist.

    Usage:
        paths = DSPaths("dsmusic")

        db_path = paths.get_data_path("upload_log.db")
        cache_path = paths.get_cache_path("api_responses", "tracks.json")
        log_path = paths.get_log_path("debug.log")
    """

    app_name: str
    app_author: str | None = "Danny Stewart"
    app_domain: str | None = "com.dannystewart"
    version: str | None = None

    def __post_init__(self) -> None:
        """Initialize platform directories."""
        # For macOS, use domain-based path if provided
        if sys.platform == "darwin" and self.app_domain:
            normalized_name = self.app_name.lower().replace(" ", "")
            app_path = f"{self.app_domain}.{normalized_name}"
        else:
            app_path = self.app_name

        self.dirs = PlatformDirs(
            appname=app_path,
            appauthor=self.app_author,
            version=self.version,
        )

        # Set up path groups
        self.data = PathGroup(self, self.dirs.user_data_dir)
        self.cache = PathGroup(self, self.dirs.user_cache_dir)
        self.config = PathGroup(self, self.dirs.user_config_dir)
        self.log = PathGroup(self, self.dirs.user_log_dir)
        self.state = PathGroup(self, self.dirs.user_state_dir)

        # User directories
        home = os.path.expanduser("~")
        self.home = PathGroup(self, home)
        self.documents = PathGroup(self, os.path.join(home, "Documents"))
        self.downloads = PathGroup(self, os.path.join(home, "Downloads"))
        self.music = PathGroup(self, os.path.join(home, "Music"))
        self.pictures = PathGroup(self, os.path.join(home, "Pictures"))
        self.onedrive = OneDriveGroup(self)

    @property
    def onedrive_dir(self) -> str:
        """Get the platform-specific OneDrive base directory."""
        if sys.platform == "darwin":
            return os.path.join(self.home, "Library/CloudStorage/OneDrive-Personal")
        if sys.platform == "win32":
            return os.path.join(self.home, "OneDrive")
        msg = "OneDrive path not supported on this platform."
        raise NotImplementedError(msg)

    def get_onedrive_path(self, *paths: str, ensure_exists: bool = True) -> str:
        """Get a path in the user's OneDrive directory."""
        path = os.path.join(self.onedrive_dir, *paths)
        if ensure_exists:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def get_ssh_key(self, *paths: str) -> str:
        """Get an SSH key from the user's .ssh directory."""
        return os.path.join(self.home.base, ".ssh", *paths)

    @property
    def config_dir(self) -> str:
        """Get config directory for settings."""
        return self.dirs.user_config_dir

    def get_config_path(self, *paths: str, no_create: bool = False, legacy: bool = False) -> str:
        """
        Get a path in the config directory.

        Args:
            *paths: Path components to join.
            no_create: If True, don't create parent directories.
            legacy: If True, use ~/.config instead of platform-specific location.
        """
        if legacy:
            base = os.path.expanduser(f"~/.config/{self.app_name}")
            path = os.path.join(base, *paths)
        else:
            path = os.path.join(self.config_dir, *paths)

        if not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path
