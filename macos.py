import subprocess


def get_timestamps(file):
    """
    Gets file creation and modification timestamps. macOS only, as it relies on GetFileInfo.

    Args:
        file (str): The file to get the timestamps of.

    Returns:
        ctime (str): The creation timestamp.
        mtime (str): The modification timestamp.
    """
    ctime = subprocess.check_output(["GetFileInfo", "-d", file]).decode().strip()
    mtime = subprocess.check_output(["GetFileInfo", "-m", file]).decode().strip()
    return ctime, mtime


def set_timestamps(file, ctime=None, mtime=None):
    """
    Sets file creation and/or modification timestamps. macOS only, as it relies on SetFile.

    Args:
        file (str): The file to set the timestamps of.
        ctime (str, optional): The creation timestamp to set. If None, creation time won't be set.
        mtime (str, optional): The modification timestamp to set. If None, modification time won't be set.
    """
    if ctime is None and mtime is None:
        raise ValueError("At least one of ctime or mtime must be set.")
    if ctime:
        subprocess.run(["SetFile", "-d", ctime, file])
    if mtime:
        subprocess.run(["SetFile", "-m", mtime, file])
