import json
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import environ, path
from typing import Set, Dict, TypeAlias, ClassVar, Optional
from sfa.utils.error import log_assert


@dataclass(frozen=True)
class SASTToolFlag:
    """Container for SAST tool flag information."""
    tool_name: str
    file_name: str
    code_line: int
    vuln_type: str


SASTToolOutput: TypeAlias = Set[SASTToolFlag]


def convert_sarif(findings: str, tool_name: Optional[str] = None) -> SASTToolOutput:
    """Convert SARIF output into common data format.

    :param findings: SAST tool output
    :param tool_name: SAST tool name
    :return: Formatted output
    """
    sarif_data = json.loads(findings)

    log_assert(sarif_data["version"] == "2.1.0", "Unsupported SARIF version!")

    result_set = set()

    for run in sarif_data["runs"]:
        if tool_name is None:
            tool_name = run["tool"]["driver"]["name"]

        tool_name = tool_name.lower()

        # Create a mapping from the rule ID to its corresponding name.
        rule_dict = {rule["id"]: rule["name"] for rule in run["tool"]["driver"]["rules"]}

        for finding in run["results"]:
            log_assert(finding["ruleId"] in rule_dict.keys())

            rule_name = rule_dict[finding["ruleId"]]

            for loc in finding["locations"]:
                file_name = path.basename(loc["physicalLocation"]["artifactLocation"]["uri"])
                code_line = int(loc["physicalLocation"]["region"]["startLine"])

                result_set.add(SASTToolFlag(tool_name, file_name, code_line, rule_name))

    return result_set


class SASTToolRunner(ABC):
    """SAST tool runner skeleton."""

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

    def __init__(self, subject_dir: str) -> None:
        self._subject_dir = subject_dir

    @abstractmethod
    def _setup(self, temp_dir: str) -> str:
        """Run pre-processing step(s) required by SAST tool.

        :param temp_dir: Temp directory path
        :return: Working directory path
        """
        pass

    @abstractmethod
    def _analyze(self, working_dir: str) -> str:
        """Execute SAST tool on target program.

        :param working_dir: Working directory path
        :return: SAST tool output
        """
        pass

    @abstractmethod
    def _format(self, findings: str) -> SASTToolOutput:
        """Convert SAST tool-specific output into common data format.

        :param findings: SAST tool output
        :return: Formatted output
        """
        pass

    def run(self) -> SASTToolOutput:
        """Run pre-processing, SAST tool analysis, and output formatting in sequence.

        :return: None
        """
        log_assert(path.exists(self._subject_dir))

        with tempfile.TemporaryDirectory() as temp_dir:
            working_dir = self._setup(temp_dir)

            log_assert(path.exists(working_dir))

            return self._format(self._analyze(working_dir))
