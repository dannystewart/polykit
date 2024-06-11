# pylint: disable=too-many-branches

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable

from natsort import natsorted
from send2trash import send2trash
from termcolor import colored

from dsutil.shell import confirm_action
from dsutil.text import ColorName

# ==================================================================================================
# List files
# ==================================================================================================


def list_files(
    directory: str,
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
    """
    List all files in a directory that match the given criteria.

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
        - The `extensions` parameter should not include the dot prefix (e.g., 'txt' not '.txt').
        - The `modified_after` and `modified_before` expect datetime.datetime objects.
        - Sorting is performed by modification time in ascending order by default. Customize sorting
            with the 'sort_key' and 'reverse' parameters.
    """
    directory_path = Path(directory)
    if extensions:
        extensions = [f"*.{ext}" for ext in (extensions if isinstance(extensions, list) else [extensions])]
    else:
        extensions = ["*"]
    files_filtered: list = []
    for extension in extensions:
        if recursive:
            files = directory_path.rglob(extension)
        else:
            files = directory_path.glob(extension)
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
        if not include_hidden and file_path.name.startswith("."):
            result = False
        elif exclude_patterns and any(file_path.match(pattern) for pattern in exclude_patterns):
            result = False
        else:
            file_stats = file_path.stat()
            file_mtime = datetime.fromtimestamp(file_stats.st_mtime)
            is_below_min_size = min_size is not None and file_stats.st_size < min_size
            is_above_max_size = max_size is not None and file_stats.st_size > max_size
            is_modified_too_early = modified_after is not None and file_mtime <= modified_after
            is_modified_too_late = modified_before is not None and file_mtime >= modified_before

            if is_below_min_size or is_above_max_size or is_modified_too_early or is_modified_too_late:
                result = False
    except FileNotFoundError:
        print(f"Error accessing file {file_path}: File not found")
        result = False
    return result


# ==================================================================================================
# Delete files
# ==================================================================================================


def delete_files(
    file_paths: str | list[str],
    show_output: bool = True,
    show_individual: bool = True,
    show_total: bool = True,
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    Safely move a list of files to the trash. If that fails, asks for confirmation and
    deletes them directly.

    Args:
        file_paths: The file paths to delete.
        show_output: Whether to print output. (This overrides show_individual and show_total.)
        show_individual: Whether to print output for each individual file.
        show_total: Whether to print the total number of files deleted at the end.
        dry_run: Whether to do a dry run (don't actually delete).

    Returns:
        The number of successful deletions and failed deletions.
    """
    if dry_run and show_output:
        print(colored("NOTE: Dry run, not actually deleting!", "yellow"))

    if not isinstance(file_paths, list):
        file_paths = [file_paths]

    successful_deletions, failed_deletions = 0, 0

    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        if not file_path.exists():
            failed_deletions += 1
            if show_individual and show_output:
                print(colored(f"\nFile {file_path.name} does not exist.", "yellow"))
            continue

        if _handle_file_deletion(file_path, dry_run=dry_run, show_output=show_individual and show_output):
            successful_deletions += 1
        else:
            failed_deletions += 1

    if show_total and show_output and not dry_run:
        message = f"{successful_deletions} file{'s' if successful_deletions != 1 else ''} trashed."
        color: ColorName = "green" if successful_deletions > 0 else "red"
        if failed_deletions > 0:
            message += f" Failed to delete {failed_deletions} file{'s' if failed_deletions != 1 else ''}."
        print(colored(message, color))

    return successful_deletions, failed_deletions


def _handle_file_deletion(file_path: Path, dry_run: bool = False, show_output: bool = True) -> bool:
    """
    Attempt to delete a single file, sending it to trash or permanently deleting it.

    Args:
        file_path: The path of the file to delete.
        dry_run: Whether to perform a dry run.
        show_output: Whether to print output messages.

    Returns:
        True if the deletion was successful, False otherwise.
    """
    try:
        if dry_run:
            if show_output:
                print(colored(f"Would delete: {file_path}", "cyan"))
            return True

        send2trash(str(file_path))
        if show_output:
            print(colored(f"✔ Trashed {file_path.name}", "green"))
        return True
    except Exception as e:
        if show_output:
            print(colored(f"\nFailed to send file to trash: {e}", "red"))
        if confirm_action("Do you want to permanently delete the file?"):
            try:
                file_path.unlink()
                if show_output:
                    print(colored(f"✔ Permanently deleted {file_path.name}", "green"))
                return True
            except OSError as err:
                if show_output:
                    print(colored(f"\nError: Failed to permanently delete {file_path.name} : {err}", "red"))
    return False


# ==================================================================================================
# Copy file
# ==================================================================================================


def copy_file(source, destination, overwrite=True, show_output=True):
    """
    Copy a file from source to destination.

    Args:
        source: The source file path.
        destination: The destination file path.
        overwrite: Whether to overwrite the destination file if it already exists.
        show_output: Whether to print output.
    """
    try:
        if not overwrite and os.path.exists(destination):
            print(
                colored(
                    f"Error: Destination file {destination} already exists. Use overwrite=True to overwrite it.",
                    "yellow",
                )
            )
            return False

        shutil.copy2(source, destination)
        if show_output:
            print(colored(f"Copied {source} to {destination}.", "green"))
        return True
    except Exception as e:
        print(colored(f"Error copying file: {e}", "red"))
        return False


def move_file(source: Path, destination: Path, overwrite: bool = False, show_output: bool = True) -> bool:
    """
    Move a file from source to destination.

    Args:
        source: The source file path.
        destination: The destination file path.
        overwrite: Whether to overwrite the destination file if it already exists.
        show_output: Whether to print output.
    """
    try:
        if not overwrite and os.path.exists(destination):
            print(
                colored(
                    f"Error: Destination file {destination} already exists. Use overwrite=True to overwrite it.",
                    "yellow",
                )
            )
            return False

        shutil.move(source, destination)
        if show_output:
            print(colored(f"Moved {source} to {destination}.", "green"))
        return True
    except Exception as e:
        print(colored(f"Error moving file: {e}", "red"))
        return False


# ==================================================================================================
# File comparison functions
# ==================================================================================================


def sha256_checksum(filename: Path, block_size: int = 65536) -> str:
    """
    Generate SHA-256 hash of a file.

    Args:
        filename: The file path.
        block_size: The block size to use when reading the file. Defaults to 65536.

    Returns:
        str: The SHA-256 hash of the file.
    """
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    return sha256.hexdigest()


def compare_files_by_mtime(file1: Path, file2: Path) -> float:
    """
    Compare two files based on modification time.

    Args:
        file1: The first file path.
        file2: The second file path.

    Returns:
        The difference in modification time between the two files.
    """
    stat1 = os.stat(file1)
    stat2 = os.stat(file2)
    return stat1.st_mtime - stat2.st_mtime


def find_duplicate_files_by_hash(files: list[Path]) -> None:
    """
    Find and print duplicate files by comparing their SHA-256 hashes.

    Args:
        files: A list of file paths.
    """
    hash_map = {}
    duplicates_found = False

    for file_path in files:
        if os.path.isfile(file_path):
            file_hash = sha256_checksum(file_path)
            if file_hash not in hash_map:
                hash_map[file_hash] = [file_path]
            else:
                hash_map[file_hash].append(file_path)
                duplicates_found = True

    for file_hash, file_list in hash_map.items():
        if len(file_list) > 1:
            print("\nHash:", file_hash)
            print(colored("Duplicate files:", "yellow"))
            for duplicate_file in file_list:
                print(f"  - {duplicate_file}")

    if not duplicates_found:
        print(colored("\nNo duplicates found!", "green"))
