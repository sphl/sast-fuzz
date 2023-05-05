from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from sfa.tool_runner.base import SASTToolOutput


class SASTFilter(Enum):
    REH = "reachability"


class SASTOutputFilter(ABC):
    """Abstract SAST tool output filter."""

    def __init__(self, sfi_file: Path) -> None:
        self._sfi_file = sfi_file

    @abstractmethod
    def filter(self, flags: SASTToolOutput) -> SASTToolOutput:
        """Filter SAST tool output.

        :param flags: SAST tool output
        :return: Filtered flags
        """
        pass
