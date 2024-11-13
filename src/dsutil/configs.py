from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import requests

from dsutil.log import LocalLogger

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


def update_configs() -> None:
    """Pull down latest configs from GitLab, updating both local and package copies."""
    for config in CONFIGS:
        try:
            response = requests.get(config.url)
            response.raise_for_status()
            content = response.text

            config.local_path.write_text(content)  # Update local copy
            logger.info("Updated local %s config at %s.", config.name, config.local_path)

            config.package_path.write_text(content)  # Update package copy
            logger.info("Updated package %s config at %s.", config.name, config.package_path)

        except requests.RequestException:
            if config.package_path.exists():  # If download fails, copy from package to local
                shutil.copy(config.package_path, config.local_path)
                logger.warning(
                    "Failed to download %s config, copied from package version.", config.name
                )
            else:
                logger.error("Failed to update %s config.", config.name)
