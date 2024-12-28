r"""
DSPaths is a helper class to manage paths (both platform and user) in a DS-friendly way.

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

from dsutil.log import LocalLogger

logger = LocalLogger.setup_logger()


@dataclass
class DSPaths:
    """Manage paths in a DS-friendly way.

    Args:
        app_name: Name of the application. Required due to the need for a base directory.
        app_author: Author of the application.
        app_domain_prefix: Domain prefix for macOS paths. Application name will be appended.
        version: Application version.

    Usage:
        paths = DSPaths("dsmusic")

        db_path = paths.get_data_path("upload_log.db")
        cache_path = paths.get_cache_path("api_responses", "tracks.json")
        log_path = paths.get_log_path("debug.log")
    """

    app_name: str
    app_author: str | None = "Danny Stewart"
    app_domain_prefix: str | None = "com.dannystewart"
    version: str | None = None
    create_dirs: bool = True

    def __post_init__(self) -> None:
        """Initialize platform directories."""
        # For macOS, use domain-based path if provided
        if sys.platform == "darwin" and self.app_domain_prefix:
            normalized_name = self.app_name.lower().replace(" ", "")
            app_path = f"{self.app_domain_prefix}.{normalized_name}"
        else:
            app_path = self.app_name

        self._dirs = PlatformDirs(
            appname=app_path,
            appauthor=self.app_author,
            version=self.version,
        )
        if self.create_dirs:
            self._ensure_base_dirs()

    @property
    def home_dir(self) -> str:
        """Get user's home directory."""
        return os.path.expanduser("~")

    def get_home_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the user's home directory.

        Args:
            *paths: Path components to join (e.g. 'subfolder', 'file.txt').
            no_create: Whether to avoid creating directories that don't exist.
        """
        path = os.path.join(self.home_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def documents_dir(self) -> str:
        """Get user's Documents directory."""
        return os.path.join(self.home_dir, "Documents")

    def get_documents_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the user's Documents directory."""
        path = os.path.join(self.documents_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def downloads_dir(self) -> str:
        """Get user's Downloads directory."""
        return os.path.join(self.home_dir, "Downloads")

    def get_downloads_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the user's Downloads directory."""
        path = os.path.join(self.downloads_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def music_dir(self) -> str:
        """Get user's Music directory."""
        return os.path.join(self.home_dir, "Music")

    def get_music_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the user's Music directory."""
        path = os.path.join(self.music_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def pictures_dir(self) -> str:
        """Get user's Pictures directory."""
        return os.path.join(self.home_dir, "Pictures")

    def get_pictures_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the user's Pictures directory."""
        path = os.path.join(self.pictures_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def onedrive_dir(self) -> str:
        """Get the platform-specific OneDrive base directory."""
        if sys.platform == "darwin":
            return os.path.join(self.home_dir, "Library/CloudStorage/OneDrive-Personal")
        if sys.platform == "win32":
            return os.path.join(self.home_dir, "OneDrive")
        msg = "OneDrive path not supported on this platform."
        raise NotImplementedError(msg)

    def get_onedrive_path(self, *paths: str, ensure_exists: bool = True) -> str:
        """Get a path in the user's OneDrive directory."""
        path = os.path.join(self.onedrive_dir, *paths)
        if ensure_exists and self.create_dirs:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def get_ssh_key(self, *paths: str) -> str:
        """Get an SSH key from the user's .ssh directory."""
        return os.path.join(self.home_dir, ".ssh", *paths)

    @property
    def data_dir(self) -> str:
        """Get data directory for storing persistent data."""
        return self._dirs.user_data_dir

    def get_data_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the data directory."""
        path = os.path.join(self.data_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def cache_dir(self) -> str:
        """Get cache directory for temporary data."""
        return self._dirs.user_cache_dir

    def get_cache_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the cache directory."""
        path = os.path.join(self.cache_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def config_dir(self) -> str:
        """Get config directory for settings."""
        return self._dirs.user_config_dir

    def get_config_path(self, *paths: str, no_create: bool = False, legacy: bool = False) -> str:
        """Get a path in the config directory.

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

        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def log_dir(self) -> str:
        """Get log directory."""
        return self._dirs.user_log_dir

    def get_log_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the log directory."""
        path = os.path.join(self.log_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @property
    def state_dir(self) -> str:
        """Get state directory for runtime state."""
        return self._dirs.user_state_dir

    def get_state_path(self, *paths: str, no_create: bool = False) -> str:
        """Get a path in the state directory."""
        path = os.path.join(self.state_dir, *paths)
        if self.create_dirs and not no_create:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def _ensure_base_dirs(self) -> None:
        """Create base directories if they don't exist."""
        for dir_path in [
            self.data_dir,
            self.cache_dir,
            self.config_dir,
            self.log_dir,
            self.state_dir,
        ]:
            os.makedirs(dir_path, exist_ok=True)
