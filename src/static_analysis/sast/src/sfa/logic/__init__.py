import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Dict, Tuple, Optional, Generator

from sfa.config import BUILD_SCRIPT_NAME

# CSV value separator
CSV_SEP: str = ","

# Supported SARIF version
SARIF_VERSION: str = "2.1.0"

# SAST tool setup environment variables
SAST_SETUP_ENV: Dict[str, str] = {
    **os.environ.copy(),
    **{"CC": "clang", "CXX": "clang++", "CFLAGS": "-O0 -fno-inline", "CXXFLAGS": "-O0 -fno-inline"},
}


@dataclass(frozen=True)
class SASTToolFlag:
    """
    Information of a SAST tool flag.
    """

    tool: str
    file: str
    line: int
    vuln: str

    n_flags: int = field(default=1)
    n_tools: int = field(default=1)

    def as_tuple(self) -> Tuple:
        return self.tool, self.file, self.line, self.vuln, self.n_flags, self.n_tools


class SASTToolFlags:
    """
    Container for SAST tool output.
    """

    def __init__(self, flags: Optional[Set[SASTToolFlag]] = None) -> None:
        if flags is None:
            self._flags = set()
        else:
            self._flags = flags

    def add(self, flag: SASTToolFlag) -> None:
        self._flags.add(flag)

    def remove(self, flag: SASTToolFlag) -> None:
        self._flags.remove(flag)

    def to_csv(self, file: Path) -> None:
        with file.open("w+") as csv_file:
            for flag in self._flags:
                csv_file.write(CSV_SEP.join(map(str, flag.as_tuple())) + os.linesep)

    @classmethod
    def from_csv(cls, file: Path) -> "SASTToolFlags":
        flags = set()

        with file.open("r") as csv_file:
            for line in csv_file:
                vals = line.strip().split(CSV_SEP)
                flags.add(SASTToolFlag(vals[0], vals[1], int(vals[2]), vals[3], int(vals[4]), int(vals[5])))

        return SASTToolFlags(flags)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SASTToolFlags):
            return False

        return self._flags == o._flags

    def __iter__(self) -> Generator[SASTToolFlag, None, None]:
        for flag in self._flags:
            yield flag

    def __len__(self) -> int:
        return len(self._flags)


def has_build_script(dir: Path) -> bool:
    """
    Check if the directory contains the SASTFuzz-specific shell-script to build the target program.

    :param dir:
    :return:
    """
    return (dir / Path(BUILD_SCRIPT_NAME)).exists()


def convert_sarif(string: str) -> SASTToolFlags:
    """
    Convert SARIF output into common data format.

    :param string:
    :return:
    """
    sarif_data = json.loads(string)

    if sarif_data["version"] != SARIF_VERSION:
        raise Exception(f"Unsupported SARIF version ({sarif_data['version']})!")

    flags = SASTToolFlags()

    for run in sarif_data["runs"]:
        tool = run["tool"]["driver"]["name"].lower()

        # Create a mapping between rule ID and rule/vuln. name
        rule_dict = {rule["id"]: rule["name"] for rule in run["tool"]["driver"]["rules"]}

        for flag in run["results"]:
            vuln = rule_dict[flag["ruleId"]]

            for loc in flag["locations"]:
                file = loc["physicalLocation"]["artifactLocation"]["uri"]
                line = loc["physicalLocation"]["region"]["startLine"]

                # We're only interested in the filename
                file = Path(file).name

                flags.add(SASTToolFlag(tool, file, line, vuln))

    return flags
