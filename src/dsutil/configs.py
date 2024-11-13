from __future__ import annotations

import shutil
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import Final

import requests

from dsutil.log import LocalLogger
from dsutil.shell import confirm_action

logger = LocalLogger.setup_logger(__name__)


@dataclass
class ConfigFile:
    """Represents a config file that can be updated from a remote source."""

    name: str
    url: str
    local_path: Path
    package_path: Path

    def __post_init__(self) -> None:
        self.package_path = Path(__file__).parent / "configs" / self.local_path.name
        self.package_path.parent.mkdir(exist_ok=True)


CONFIGS: Final[list[ConfigFile]] = [
    ConfigFile(
        name="ruff",
        url="https://gitlab.dannystewart.com/danny/dsconfigs/raw/main/configs/ruff.toml",
        local_path=Path("ruff.toml"),
        package_path=Path(),
    ),
    ConfigFile(
        name="mypy",
        url="https://gitlab.dannystewart.com/danny/dsconfigs/raw/main/configs/mypy.ini",
        local_path=Path("mypy.ini"),
        package_path=Path(),
    ),
]


def show_diff(current: str, new: str, filename: str) -> None:
    """Show a unified diff between current and new content."""
    diff = list(
        unified_diff(
            new.splitlines(keepends=True),
            current.splitlines(keepends=True),
            fromfile=f"current {filename}",
            tofile=f"new {filename}",
        )
    )

    if diff:
        logger.warning("Changes detected in %s:", filename)
        for line in diff:
            if line.startswith("+"):
                logger.info("  %s", line.rstrip())
            elif line.startswith("-"):
                logger.warning("  %s", line.rstrip())
            else:
                logger.info("  %s", line.rstrip())
    else:
        logger.info("No changes detected in %s.", filename)


def update_config_file(config: ConfigFile, content: str, is_package: bool = False) -> bool:
    """
    Update a config file if changes are detected.

    Args:
        config: The config file to update.
        content: The new content.
        is_package: Whether this is the package version (as opposed to local).

    Returns:
        Whether the file was updated.
    """
    target = config.package_path if is_package else config.local_path
    location = "package" if is_package else "local"

    if not target.exists():
        target.write_text(content)
        logger.info("Created new %s %s config at %s.", location, config.name, target)
        return True

    current = target.read_text()
    if current == content:
        return False

    show_diff(current, content, target.name)
    if confirm_action(f"Update {location} {config.name} config?", prompt_color="yellow"):
        target.write_text(content)
        return True

    return False


def update_configs() -> None:
    """Pull down latest configs from GitLab, updating both local and package copies."""
    for config in CONFIGS:
        try:
            response = requests.get(config.url)
            response.raise_for_status()
            content = response.text

            # Ensure package directory exists
            config.package_path.parent.mkdir(exist_ok=True)

            # Update both copies if needed
            local_updated = update_config_file(config, content)
            package_updated = update_config_file(config, content, is_package=True)

            if not (local_updated or package_updated):
                logger.info("No changes needed for %s config.", config.name)

        except requests.RequestException:
            if config.package_path.exists():  # If download fails, copy from package to local
                shutil.copy(config.package_path, config.local_path)
                logger.warning(
                    "Failed to download %s config, copied from package version.", config.name
                )
            else:
                logger.error("Failed to update %s config.", config.name)
