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
    changes_made = set()

    for config in CONFIGS:
        try:
            # Get remote version
            response = requests.get(config.url)
            response.raise_for_status()
            remote_content = response.text

            # Always update the package copy first as this is our fallback
            config.package_path.parent.mkdir(exist_ok=True)
            config.package_path.write_text(remote_content)

            if config.local_path.exists():  # Check and update the local copy if needed
                current_content = config.local_path.read_text()
                if current_content != remote_content:
                    show_diff(remote_content, current_content, config.local_path.name)
                    if confirm_action(f"Update local {config.name} config?", default_to_yes=True):
                        config.local_path.write_text(remote_content)
                        logger.info("Updated %s config.", config.name)
                        changes_made.add(config.name)
            else:  # If no local copy exists, create one now
                config.local_path.write_text(remote_content)
                logger.info("Created new %s config.", config.name)
                changes_made.add(config.name)

        except requests.RequestException:
            if config.package_path.exists():
                shutil.copy(config.package_path, config.local_path)
                logger.warning(
                    "Failed to download %s config, copied from package version.", config.name
                )
            else:
                logger.error("Failed to update %s config.", config.name)

    unchanged = [c.name for c in CONFIGS if c.name not in changes_made]
    if unchanged:
        logger.info("No changes needed for: %s", ", ".join(unchanged))
