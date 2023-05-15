# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path


def read(file: Path, mode: str = "r") -> str:
    """
    Read content of a file.

    :param file:
    :param mode:
    :return:
    """
    with file.open(mode) as fh:
        return fh.read()


def write(file: Path, text: str, mode: str = "w") -> None:
    """
    Write text (string) to a file.

    :param file:
    :param text:
    :param mode:
    :return:
    """
    with file.open(mode) as fh:
        fh.write(text)
