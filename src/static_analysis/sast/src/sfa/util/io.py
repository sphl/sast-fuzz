import json
import re
import shutil
from os import linesep, walk
from pathlib import Path
from typing import List, Dict, Optional


def read(file: Path, mode: str = "r") -> str:
    """Read the text of a file.

    :param file: File path
    :param mode: File reading mode
    :return: String
    """
    with file.open(mode) as fh:
        return fh.read()


def write(file: Path, text: str, mode: str = "w") -> None:
    """Write a text to a file.

    :param file: File path
    :param text: Content
    :param mode: File writing mode
    :return: None
    """
    with file.open(mode) as fh:
        fh.write(text)


def append(file: Path, line: str) -> None:
    """Append a line to a file.

    :param file: File path
    :param line: Content
    :return: None
    """
    write(file, line + linesep, "a")


def read_json(file: Path) -> Dict:
    """Read the dictionary of a JSON file.

    :param file: File path
    :return: Dictionary
    """
    return json.loads(read(file))


def write_json(file: Path, data: Dict) -> None:
    """Write a dictionary to a JSON file.

    :param file: File path
    :param data: Content
    :return: None
    """
    write(file, json.dumps(data, sort_keys=False, indent=4))


def copy_dir(source_dir: Path, dest_root: Path) -> Path:
    """Copy the content of a source directory to a destination (root) directory.

    :param source_dir: Source directory path
    :param dest_root: Destination directory path
    :return: None
    """
    src = source_dir
    dst = dest_root / source_dir.name

    shutil.copytree(src, dst)

    return dst


def find_files(root_dir: Path, file_ext: Optional[str] = None, rec_search: bool = True) -> List[Path]:
    """Search for (certain) files in a directory.

    Starting in a root directory, this function returns the (absolute) path of all files that match the specified file
    extension. The search can be performed only in the root directory or recursively in the root directory and all con-
    tained subdirectories.

    :param root_dir: Root directory path
    :param file_ext: File extension
    :param rec_search: Recursive search, or root directory only
    :return: List of file paths
    """
    file_list = []

    if file_ext is None:
        regex = re.compile(r"^.+$")
    else:
        regex = re.compile(r"^.+\.({0})$".format(file_ext))

    for root, _, files in walk(root_dir):
        for file in filter(lambda f: regex.match(f), files):
            file_list.append(Path(root) / Path(file))

        if not rec_search:
            break

    return file_list
