from pathlib import Path

import pandas as pd

from sfa.tool_runner.base import SASTToolFlag, SASTToolOutput


def read_flags(file: Path) -> SASTToolOutput:
    """Read the SAST tool flags from a CSV file.

    :param file: Path to CSV file
    :return: SAST tool flags
    """
    data = pd.read_csv(file, header=1)

    return set([SASTToolFlag(*row) for row in data.iterrows()])


def write_flags(file: Path, flags: SASTToolOutput) -> None:
    """Write the SAST tool flags to a CSV file.

    :param file: Path to CSV file
    :param flags: SAST tool flags
    :return: None
    """
    df = pd.DataFrame.from_records([flag.as_dict() for flag in flags])

    df.to_csv(file, header=True)
