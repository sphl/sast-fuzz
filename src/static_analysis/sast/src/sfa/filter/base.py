from abc import ABC, abstractmethod
from pathlib import Path

from sfa.tool_runner.base import SASTToolOutput
from sfa.util.ext_enum import ExtendedEnum


class SASTFilter(ExtendedEnum):
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
