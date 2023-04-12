import tempfile
from abc import ABC, abstractmethod
from os import environ, path
from typing import Set, Tuple, Dict, TypeAlias, ClassVar

SASTToolOutput: TypeAlias = Set[Tuple[str, str, int, str]]


class SASTTool(ABC):
    """Skeleton for implementing SAST tool runners."""

    # Environment setup for build process
    _setup_env: ClassVar[Dict[str, str]] = {
        **environ.copy(),
        **{
            "CC": "clang",
            "CXX": "clang++",
            "CFLAGS": "-O0 -fno-inline",
            "CXXFLAGS": "-O0 -fno-inline"
        }
    }

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
        assert path.exists(self._subject_dir)

        with tempfile.TemporaryDirectory() as temp_dir:
            working_dir = self._setup(temp_dir)

            assert path.exists(working_dir)

            return self._format(self._analyze(working_dir))
