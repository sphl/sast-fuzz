from collections import defaultdict
from functools import lru_cache
from typing import Set, Dict

from sfa import SASTToolOutput
from sfa.filter import SASTOutputFilter
from sfa.util.io import read_json


class ReachabilityFilter(SASTOutputFilter):
    """Reachability filter."""

    def __init__(self, sfi_file: str) -> None:
        super().__init__(sfi_file)
        self._reachable_code: Dict[str, Set] = defaultdict(set)

        func_list = read_json(sfi_file)["functions"]

        for func in func_list:
            if func["location"]["reachable_from_main"]:
                self._reachable_code[func["location"]["filename"]].add(func["location"]["line"])

    @lru_cache(maxsize=None)
    def _is_reachable(self, line: int, file: str) -> bool:
        """Check if a code location is reachable from the main function.

        :param line: Line number
        :param file: Source filename
        :return: True if reachable, false otherwise
        """
        if file not in self._reachable_code.keys():
            return False

        for r in self._reachable_code[file]:
            if r["start"] <= line <= r["end"]:
                return True

        return False

    def filter(self, flags: SASTToolOutput) -> SASTToolOutput:
        """Filter for SAST tool flags that are reachable from the main function.

        :param flags: SAST tool output
        :return: Filtered findings
        """
        return set(filter(lambda f: self._is_reachable(f.line, f.file), flags))
