import json
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import Set, Dict, ClassVar, Optional, TypeAlias

from sfa.util.ext_enum import ExtendedEnum


class SASTTool(ExtendedEnum):
    FLF = "flawfinder"
    IFR = "infer"
    CQL = "codeql"
    CLS = "clang-scan"
    ASN = "asan"
    MSN = "msan"


@dataclass(frozen=True)
class SASTToolFlag:
    """Container for a SAST tool flag."""
    tool: str
    file: str
    line: int
    vuln: str


SASTToolOutput: TypeAlias = Set[SASTToolFlag]


def convert_sarif(flags: str, tool: Optional[SASTTool] = None) -> SASTToolOutput:
    """Convert SARIF output into common data format.

    :param flags: SAST tool output
    :param tool: SAST tool name
    :return: Formatted output
    """
    sarif_data = json.loads(flags)

    assert sarif_data["version"] == "2.1.0", "Unsupported SARIF version!"

    result_set = set()

    for run in sarif_data["runs"]:
        if tool is None:
            _tool = run["tool"]["driver"]["name"]
        else:
            _tool = tool.value.lower()

        # Create a mapping from the rule ID to its corresponding name.
        rule_dict = {rule["id"]: rule["name"] for rule in run["tool"]["driver"]["rules"]}

        for finding in run["results"]:
            assert finding["ruleId"] in rule_dict.keys()

            vuln = rule_dict[finding["ruleId"]]

            for loc in finding["locations"]:
                file = Path(loc["physicalLocation"]["artifactLocation"]["uri"]).name
                line = int(loc["physicalLocation"]["region"]["startLine"])

                result_set.add(SASTToolFlag(_tool, file, line, vuln))

    return result_set


class SASTToolRunner(ABC):
    """Abstract SAST tool runner."""

    _setup_env: ClassVar[Dict[str, str]] = {
        **environ.copy(),
        **{
            "CC": "clang",
            "CXX": "clang++",
            "CFLAGS": "-O0 -fno-inline",
            "CXXFLAGS": "-O0 -fno-inline"
        }
    }
    """Environment setup for build process."""

    def __init__(self, subject_dir: Path) -> None:
        self._subject_dir = subject_dir

    @abstractmethod
    def _setup(self, temp_dir: Path) -> Path:
        """Run pre-processing step(s) required by SAST tool.

        :param temp_dir: Temp directory path
        :return: Working directory path
        """
        pass

    @abstractmethod
    def _analyze(self, working_dir: Path) -> str:
        """Execute SAST tool on target program.

        :param working_dir: Working directory path
        :return: SAST tool flags
        """
        pass

    @abstractmethod
    def _format(self, flags: str) -> SASTToolOutput:
        """Convert SAST tool-specific output into common data format.

        :param flags: SAST tool flags
        :return: Formatted output
        """
        pass

    def run(self) -> SASTToolOutput:
        """Run pre-processing, SAST tool analysis, and output formatting in sequence.

        :return: None
        """
        assert self._subject_dir.exists()

        with tempfile.TemporaryDirectory() as temp_dir:
            working_dir = self._setup(Path(temp_dir))

            assert working_dir.exists()

            return self._format(self._analyze(working_dir))
