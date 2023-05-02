from collections import defaultdict
from functools import lru_cache
from typing import Set, Dict

from sfa.logic.filters.base import SASTToolOutputFilter, SASTToolOutput
from sfa.utils.io import read_json


class ReachabilityFilter(SASTToolOutputFilter):
    """Reachability filter implementation."""

    def __init__(self, sfi_file: str) -> None:
        super().__init__(sfi_file)
        self._reachable_code: Dict[str, Set] = defaultdict(set)

        func_list = read_json(sfi_file)["functions"]

        for func in func_list:
            if func["location"]["reachable_from_main"]:
                self._reachable_code[func["location"]["filename"]].add(func["location"]["line"])

    @lru_cache(maxsize=None)
    def _is_reachable(self, code_line: int, file_name: str) -> bool:
        """Check if a code location is reachable from the main function.

        :param code_line: Line number
        :param file_name: Source filename
        :return: True if reachable, false otherwise
        """
        if file_name not in self._reachable_code.keys():
            return False

        for r in self._reachable_code[file_name]:
            if r["start"] <= code_line <= r["end"]:
                return True

        return False

    def filter(self, findings: SASTToolOutput) -> SASTToolOutput:
        """Filter SAST tool findings that are reachable from the main function.

        :param findings: SAST tool output
        :return: Filtered findings
        """
        return set(filter(lambda f: self._is_reachable(f.code_line, f.file_name), findings))
