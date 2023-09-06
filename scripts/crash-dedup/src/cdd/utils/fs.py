from os import walk
from pathlib import Path
from typing import List, Optional, Set


def find_files(
    root_dirs: List[Path], exts: Optional[List[str]] = None, rec: bool = False, blacklist: Optional[List[str]] = None
) -> Set[Path]:
    """
    Search for files in various directories.

    :param root_dirs: List of directories to start the search from
    :param exts: Allowed file extension
    :param rec: If true, perform recursive search, otherwise, only at top-level
    :param blacklist: List of filenames to be excluded from the result
    :return: Set of files
    """

    def include(f: Path) -> bool:
        return (exts is None or f.suffix in exts) and (blacklist is None or not f.name in blacklist)

    files: Set[Path] = set()

    for root_dir in root_dirs:
        for root, _, _files in walk(root_dir):
            files.update([Path(root) / Path(file) for file in _files if include(Path(file))])

            if not rec:
                break

    return files
