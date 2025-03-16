from __future__ import annotations

from dataclasses import dataclass
from difflib import unified_diff
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

from dsbase.log import LocalLogger

if TYPE_CHECKING:
    from logging import Logger

logger = LocalLogger().get_logger(__name__)


class DiffStyle(StrEnum):
    """Style of diff output."""

    COLORED = "colored"
    SIMPLE = "simple"
    MINIMAL = "minimal"


@dataclass
class DiffResult:
    """Result of a diff comparison."""

    has_changes: bool
    changes: list[str]
    additions: list[str]
    deletions: list[str]


def diff_files(
    file1_path: str | Path,
    file2_path: str | Path,
    style: DiffStyle = DiffStyle.COLORED,
) -> DiffResult:
    """Show diff between two files.

    Args:
        file1_path: Path to first file.
        file2_path: Path to second file.
        style: Styling to use for displaying the diff output. Defaults to colored.

    Returns:
        DiffResult containing the changes found.
    """
    return show_diff(
        old=Path(file1_path).read_text(encoding="utf-8"),
        new=Path(file2_path).read_text(encoding="utf-8"),
        filename=str(file2_path),
        style=style,
    )


def show_diff(
    old: str,
    new: str,
    filename: str | None = None,
    *,
    style: DiffStyle = DiffStyle.COLORED,
    logger: Logger | None = None,
) -> DiffResult:
    """Show a unified diff between current and new content.

    Args:
        old: Old content.
        new: New content.
        filename: Optional filename for context.
        style: Styling to use for displaying the diff output. Defaults to colored.
        logger: Optional external logger to use. Defaults to internal logger.

    Returns:
        DiffResult containing the changes found.
    """
    logger = logger or LocalLogger().get_logger(__name__)
    changes: list[str] = []
    additions: list[str] = []
    deletions: list[str] = []

    diff = list(
        unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"current {filename}" if filename else "current",
            tofile=f"new {filename}" if filename else "new",
        )
    )

    if not diff:
        if filename:
            logger.info("No changes detected in %s.", filename)
        return DiffResult(False, [], [], [])

    if filename:
        logger.info("Changes detected in %s:", filename)

    for line in diff:
        changes.append(line.rstrip())
        _process_diff_line(line, style, logger, additions, deletions)

    return DiffResult(True, changes, additions, deletions)


def _process_diff_line(
    line: str,
    style: DiffStyle,
    log_func: Logger,
    additions: list[str],
    deletions: list[str],
) -> None:
    """Process a single line of diff output."""
    if not _should_show_line(line, style):
        return

    if style == DiffStyle.COLORED:
        if line.startswith("+"):
            log_func.info("  %s", line.rstrip())
        elif line.startswith("-"):
            log_func.warning("  %s", line.rstrip())
        else:
            log_func.debug("  %s", line.rstrip())
    else:
        log_func.info("  %s", line.rstrip())

    if line.startswith("+"):
        additions.append(line.rstrip())
    elif line.startswith("-"):
        deletions.append(line.rstrip())


def _should_show_line(line: str, style: DiffStyle) -> bool:
    """Determine if a line should be shown based on the diff style."""
    return style in {DiffStyle.COLORED, DiffStyle.SIMPLE} or (
        style == DiffStyle.MINIMAL and line.startswith(("+", "-"))
    )
