from abc import ABC, abstractmethod

from sfa.logic import SASTToolFlag, SASTToolOutput


class SASTOutputFilter(ABC):
    """SAST tool output filter skeleton."""

    def __init__(self, sfi_file: str) -> None:
        self._sfi_file = sfi_file

    @abstractmethod
    def filter(self, findings: SASTToolOutput) -> SASTToolOutput:
        """Filter SAST tool output.

        :param findings: SAST tool output
        :return: Filtered findings
        """
        pass
