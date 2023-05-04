from enum import Enum
from typing import List
from abc import ABC, abstractmethod

from sfa import SASTToolOutput


class SASTFilter(Enum):
    REH = "reachability"

    @classmethod
    def values(cls) -> List[str]:
        return [_filter.value for _filter in cls]


class SASTOutputFilter(ABC):
    """Abstract SAST tool output filter."""

    def __init__(self, sfi_file: str) -> None:
        self._sfi_file = sfi_file

    @abstractmethod
    def filter(self, flags: SASTToolOutput) -> SASTToolOutput:
        """Filter SAST tool output.

        :param flags: SAST tool output
        :return: Filtered flags
        """
        pass
