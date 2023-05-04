import json
import tempfile
from enum import Enum
from abc import ABC, abstractmethod
from os import environ, path
from typing import List, Dict, ClassVar, Optional

from sfa import SASTToolFlag, SASTToolOutput
from sfa.util.error import log_assert


class SASTTool(Enum):
    FLF = "flawfinder"
    IFR = "infer"
    CQL = "codeql"
    CLS = "clang-scan"
    ASN = "asan"
    MSN = "msan"

    @classmethod
    def values(cls) -> List[str]:
        return [tool.value for tool in cls]


def convert_sarif(flags: str, tool: Optional[SASTTool] = None) -> SASTToolOutput:
    """Convert SARIF output into common data format.

    :param flags: SAST tool output
    :param tool: SAST tool name
    :return: Formatted output
    """
    sarif_data = json.loads(flags)

    log_assert(sarif_data["version"] == "2.1.0", "Unsupported SARIF version!")

    result_set = set()

    for run in sarif_data["runs"]:
        if tool is None:
            _tool = run["tool"]["driver"]["name"]
        else:
            _tool = tool.value.lower()

        # Create a mapping from the rule ID to its corresponding name.
        rule_dict = {rule["id"]: rule["name"] for rule in run["tool"]["driver"]["rules"]}

        for finding in run["results"]:
            log_assert(finding["ruleId"] in rule_dict.keys())

            vuln = rule_dict[finding["ruleId"]]

            for loc in finding["locations"]:
                file = path.basename(loc["physicalLocation"]["artifactLocation"]["uri"])
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
        log_assert(path.exists(self._subject_dir))

        with tempfile.TemporaryDirectory() as temp_dir:
            working_dir = self._setup(temp_dir)

            log_assert(path.exists(working_dir))

            return self._format(self._analyze(working_dir))
