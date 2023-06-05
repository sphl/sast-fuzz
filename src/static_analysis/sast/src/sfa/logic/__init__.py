import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, Optional, Set, Tuple

# CSV value separator
CSV_SEP: str = ","

# Supported SARIF version
SARIF_VERSION: str = "2.1.0"

# SAST tool setup environment variables
SAST_SETUP_ENV: Dict[str, str] = {
    **os.environ.copy(),
    **{"CC": "clang", "CXX": "clang++", "CFLAGS": "-O0 -fno-inline", "CXXFLAGS": "-O0 -fno-inline"},
}


class DatatypeVersionException(Exception):
    """
    Exception for unsupported data type versions.
    """

    pass


@dataclass(frozen=True)
class SASTFlag:
    """
    SAST flag information.
    """

    tool: str
    file: str
    line: int
    vuln: str

    def as_tuple(self) -> Tuple:
        return self.tool, self.file, self.line, self.vuln


@dataclass(frozen=True)
class GroupedSASTFlag(SASTFlag):
    """
    Grouped SAST flag information.
    """

    n_flg_lines: int
    n_all_lines: int
    n_run_tools: int
    n_all_tools: int

    def as_tuple(self) -> Tuple:
        return super().as_tuple() + (self.n_flg_lines, self.n_all_lines, self.n_run_tools, self.n_all_tools)


class SASTFlagSet:
    """
    SAST flag container.
    """

    def __init__(self, flags: Optional[Set[SASTFlag]] = None) -> None:
        self._flags = set() if flags is None else flags

    def add(self, flag: SASTFlag) -> None:
        """
        Add a single SAST flag.
        :param flag:
        :return:
        """
        self._flags.add(flag)

    def update(self, *var_flags: "SASTFlagSet") -> None:
        """
        Add multiple SAST flags.

        :param var_flags:
        :return:
        """
        for flags in var_flags:
            self._flags.update(flags._flags)

    def remove(self, flag: SASTFlag) -> None:
        """
        Remove a single SAST flag.

        :param flag:
        :return:
        """
        self._flags.remove(flag)

    def to_csv(self, file: Path) -> None:
        """
        Write SAST flags to a CSV file.

        :param file:
        :return:
        """
        with file.open("w+") as csv_file:
            for flag in self._flags:
                csv_file.write(CSV_SEP.join(map(str, flag.as_tuple())) + os.linesep)

    @classmethod
    def from_csv(cls, file: Path) -> "SASTFlagSet":
        """
        Read SAST flags from a CSV file.

        :param file:
        :return:
        """
        flags = SASTFlagSet()

        with file.open("r") as csv_file:
            for line in csv_file:
                vals = line.strip().split(CSV_SEP)

                if len(vals) == 4:  # Regular SAST flag
                    flags.add(SASTFlag(vals[0], vals[1], int(vals[2]), vals[3]))

                if len(vals) == 8:  # Grouped SAST flag
                    flags.add(
                        GroupedSASTFlag(
                            vals[0],
                            vals[1],
                            int(vals[2]),
                            vals[3],
                            int(vals[4]),
                            int(vals[5]),
                            int(vals[6]),
                            int(vals[7]),
                        )
                    )

        return flags

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SASTFlagSet):
            return False

        return self._flags == o._flags

    def __iter__(self) -> Generator[SASTFlag, None, None]:
        for flag in self._flags:
            yield flag

    def __len__(self) -> int:
        return len(self._flags)


def convert_sarif(string: str) -> SASTFlagSet:
    """
    Convert SARIF data into our SAST flag format.

    :param string:
    :return:
    """
    sarif_data = json.loads(string)

    if sarif_data["version"] != SARIF_VERSION:
        raise DatatypeVersionException(f"SARIF version {sarif_data['version']} is not supported.")

    flags = SASTFlagSet()

    for run in sarif_data["runs"]:
        tool = run["tool"]["driver"]["name"].lower()

        # Create a mapping between rule ID and vulnerability name
        rule_dict = {rule["id"]: rule["name"] for rule in run["tool"]["driver"]["rules"]}

        for flag in run["results"]:
            vuln = rule_dict[flag["ruleId"]]

            for loc in flag["locations"]:
                file = loc["physicalLocation"]["artifactLocation"]["uri"]
                line = loc["physicalLocation"]["region"]["startLine"]

                file = Path(file).name

                flags.add(SASTFlag(tool, file, line, vuln))

    return flags
