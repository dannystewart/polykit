# pylint: disable=too-many-branches
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from natsort import natsorted

from dsutil import TZ
from dsutil.text import print_colored

if TYPE_CHECKING:
    from collections.abc import Callable


def list_files(
    directory: str | Path,
    extensions: str | list[str] | None = None,
    recursive: bool = False,
    min_size: int | None = None,
    max_size: int | None = None,
    exclude_patterns: str | list[str] | None = None,
    include_hidden: bool = False,
    modified_after: datetime | None = None,
    modified_before: datetime | None = None,
    sort_key: Callable | None = None,
    reverse_sort: bool = False,
) -> list[str]:
    """List all files in a directory that match the given criteria.

    Args:
        directory: The directory to search.
        extensions: The file extensions to include. If None, all files will be included.
        recursive: Whether to search recursively.
        min_size: The minimum file size in bytes.
        max_size: The maximum file size in bytes.
        exclude_patterns: Glob patterns to exclude.
        include_hidden: Whether to include hidden files.
        modified_after: Only include files modified after this date.
        modified_before: Only include files modified before this date.
        sort_key: A function to use for sorting the files.
        reverse_sort: Whether to reverse the sort order.

    Returns:
        A list of file paths.

    Example usage with custom sort (alphabetical sorting by file name):
        `file_list = list_files(directory, sort_key=os.path.basename)`

    Notes:
        - The `extensions` parameter should not include the dot prefix (e.g. 'txt' not '.txt').
        - The `modified_after` and `modified_before` expect datetime.datetime objects.
        - Sorting is performed by modification time in ascending order by default. Customize sorting
            with the 'sort_key' and 'reverse' parameters.
    """
    directory_path = Path(directory)
    if extensions:
        extensions = [
            ext.lstrip(".")
            for ext in (extensions if isinstance(extensions, list) else [extensions])
        ]
        extensions = [f"*.{ext}" for ext in extensions]
    else:
        extensions = ["*"]
    files_filtered: list = []
    for extension in extensions:
        files = directory_path.rglob(extension) if recursive else directory_path.glob(extension)
        files_filtered.extend(
            file
            for file in files
            if file.is_file()
            and file_matches_criteria(
                file,
                min_size,
                max_size,
                exclude_patterns,
                include_hidden,
                modified_after,
                modified_before,
            )
        )
    sort_function = sort_key or (lambda x: x.stat().st_mtime)
    return natsorted(files_filtered, key=sort_function, reverse=reverse_sort)


def file_matches_criteria(
    file_path: Path,
    min_size: int | None = None,
    max_size: int | None = None,
    exclude_patterns: str | list[str] | None = None,
    include_hidden: bool = False,
    modified_after: datetime | None = None,
    modified_before: datetime | None = None,
) -> bool:
    """Check if a file matches the given criteria."""
    result = True
    try:
        if (not include_hidden and file_path.name.startswith(".")) or (
            exclude_patterns and any(file_path.match(pattern) for pattern in exclude_patterns)
        ):
            result = False
        else:
            file_stats = file_path.stat()
            file_mtime = datetime.fromtimestamp(file_stats.st_mtime, tz=TZ)
            is_below_min_size = min_size is not None and file_stats.st_size < min_size
            is_above_max_size = max_size is not None and file_stats.st_size > max_size
            is_modified_too_early = modified_after is not None and file_mtime <= modified_after
            is_modified_too_late = modified_before is not None and file_mtime >= modified_before

            if (
                is_below_min_size
                or is_above_max_size
                or is_modified_too_early
                or is_modified_too_late
            ):
                result = False
    except FileNotFoundError:
        print_colored(f"Error accessing file {file_path}: File not found", "red")
        result = False
    return result
