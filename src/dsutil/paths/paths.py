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
from dataclasses import dataclass, field

from platformdirs import PlatformDirs

from .path_types import BasePath, ConfigPath, OneDrivePath, PlatformPath, UserPath

from dsutil.log import LocalLogger

logger = LocalLogger.setup_logger()


# Define list of paths to be created as attributes
PATHS = [
    #
    # Platform directories
    ("data", PlatformPath),
    ("cache", PlatformPath),
    ("log", PlatformPath),
    ("state", PlatformPath),
    #
    # Config directory (supports `legacy` parameter)
    ("config", ConfigPath),
    #
    # User directories
    ("home", UserPath),  # no subfolder = home directory
    ("documents", UserPath, "Documents"),
    ("downloads", UserPath, "Downloads"),
    ("music", UserPath, "Music"),
    ("pictures", UserPath, "Pictures"),
    #
    # Cloud storage
    ("onedrive", OneDrivePath),
]


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
    create_dirs: bool = True
    _path_objects: dict[str, BasePath] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize platform directories."""
        # Initialize platformdirs
        if sys.platform == "darwin" and self.app_domain:
            # For macOS, use domain-based path if provided
            normalized_name = self.app_name.lower().replace(" ", "")
            app_path = f"{self.app_domain}.{normalized_name}"
        else:
            app_path = self.app_name

        self.dirs = PlatformDirs(
            appname=app_path,
            appauthor=self.app_author,
            version=self.version,
        )

        # Create all path objects
        for name, path_class, *args in PATHS:
            self._path_objects[name] = path_class(name, self, self.get_home_dir, *args)

        # Set up properties and methods
        for name in self._path_objects:
            setattr(
                self.__class__,
                f"{name}_dir",
                property(lambda self, n=name: self._path_objects[n].dir),
            )
            setattr(self, f"get_{name}_path", self._path_objects[name].get_path)

        if self.create_dirs:
            self._ensure_base_dirs()

    def get_home_dir(self) -> str:
        """Get user's home directory."""
        return os.path.expanduser("~")

    def get_ssh_key(self, *paths: str) -> str:
        """Get an SSH key from the user's '.ssh' directory."""
        return os.path.join(self.get_home_dir, ".ssh", *paths)

    def _ensure_base_dirs(self) -> None:
        """Create base directories if they don't exist."""
        platform_paths = [
            obj for obj in self._path_objects.values() if isinstance(obj, PlatformPath)
        ]
        for path_obj in platform_paths:
            os.makedirs(path_obj.dir, exist_ok=True)
