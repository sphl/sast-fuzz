import logging
import shutil
from os import walk
from pathlib import Path
from typing import List, Optional, Set


def get_parent(path: Path, depth: int = 1) -> Path:
    """
    Return the n-th parent of a path.

    :param path:
    :param depth:
    :return:
    """
    if depth == 0:
        return path

    depth -= 1

    return get_parent(path.parent, depth)


def copy_dir(src_dir: Path, dst_dir: Path, extend_dst: bool = True) -> Optional[Path]:
    """
    Copy the contents of a source to a destination directory.

    :param src_dir: Source directory
    :param dst_dir: Destination directory
    :param extend_dst: If true, extend dest. with source dir name, otherwise, no changes
    :return: Destination directory path if no exception occurred
    """
    if extend_dst:
        dst_dir = dst_dir / src_dir.name

    try:
        shutil.copytree(src_dir, dst_dir)

        return dst_dir

    except Exception as ex:
        logging.error(f"Exception occurred while copying '{src_dir}' to '{dst_dir}'!")
        logging.error(ex)

        return None


def has_extension(file: Path, exts: List[str]) -> bool:
    """
    Check if file has certain extension.

    :param file:
    :param exts:
    :return:
    """
    return file.suffix in exts


def find_files(
    dir: Path, exts: Optional[List[str]] = None, rec: bool = True
) -> Set[Path]:
    """
    Search for files in a directory.

    :param dir: Directory to start the search from
    :param exts: Allowed file extension
    :param rec: If true, perform recursive search, otherwise, only at top-level
    :return:
    """
    files: Set[Path] = set()

    for root, _, _files in walk(dir):
        files.update(
            [
                Path(root) / Path(file)
                for file in _files
                if (exts is None or has_extension(Path(file), exts))
            ]
        )

        if not rec:
            break

    return files
