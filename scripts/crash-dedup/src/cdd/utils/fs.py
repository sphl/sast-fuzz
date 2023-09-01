from os import walk
from pathlib import Path
from typing import List, Optional, Set


def find_files(root_dir: Path, exts: Optional[List[str]] = None, rec: bool = True) -> Set[Path]:
    """
    Search for files in a directory.

    :param root_dir: Directory to start the search from
    :param exts: Allowed file extension
    :param rec: If true, perform recursive search, otherwise, only at top-level
    :return: Set of files
    """
    files: Set[Path] = set()

    for root, _, _files in walk(root_dir):
        files.update([Path(root) / Path(file) for file in _files if (exts is None or Path(file).suffix in exts)])

        if not rec:
            break

    return files
