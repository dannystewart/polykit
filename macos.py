"""macOS-specific functions and utilities."""

import subprocess


def get_timestamps(file: str) -> tuple[str, str]:
    """
    Get file creation and modification timestamps. macOS only, as it relies on GetFileInfo.

    Args:
        file: The file to get the timestamps of.

    Returns:
        ctime: The creation timestamp.
        mtime: The modification timestamp.
    """
    ctime = subprocess.check_output(["GetFileInfo", "-d", file]).decode().strip()
    mtime = subprocess.check_output(["GetFileInfo", "-m", file]).decode().strip()
    return ctime, mtime


def set_timestamps(file: str, ctime: str | None = None, mtime: str | None = None) -> None:
    """
    Set file creation and/or modification timestamps. macOS only, as it relies on SetFile.

    Args:
        file: The file to set the timestamps of.
        ctime: The creation timestamp to set. If None, creation time won't be set.
        mtime: The modification timestamp to set. If None, modification time won't be set.
    """
    if ctime is None and mtime is None:
        raise ValueError("At least one of ctime or mtime must be set.")
    if ctime:
        subprocess.run(["SetFile", "-d", ctime, file])
    if mtime:
        subprocess.run(["SetFile", "-m", mtime, file])
