import json
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from sfa.logic import SASTFlagSet
from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory


class SASTFlagFilterMode(ExtendedEnum):
    REH = "reachability"


class SASTFlagFilterFactory(Factory):
    """
    SAST flag filter factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {SASTFlagFilterMode.REH: ReachabilityFilter(param)}


class SASTFlagFilter(ABC):
    """
    Abstract SAST flag filter.
    """

    def __init__(self, inspec_file: Path) -> None:
        self._inspec_file = inspec_file

    @abstractmethod
    def filter(self, flags: SASTFlagSet) -> SASTFlagSet:
        """
        Filter out certain SAST flags.

        :param flags:
        :return:
        """
        pass


class ReachabilityFilter(SASTFlagFilter):
    """
    SAST flag reachability filter.
    """

    def __init__(self, inspec_file: Path) -> None:
        super().__init__(inspec_file)
        self._reachable_code: Dict[str, List[Dict]] = defaultdict(list)

        data = json.loads(inspec_file.read_text())

        for func in data["functions"]:
            if func["location"]["reachable_from_main"]:
                self._reachable_code[func["location"]["filename"]].append(func["location"]["line"])

    @lru_cache(maxsize=None)
    def _is_reachable(self, file: str, line: int) -> bool:
        """
        Check if a code location is reachable from the main function.

        :param file:
        :param line:
        :return:
        """
        if file in self._reachable_code.keys():
            for line_range in self._reachable_code[file]:
                if line_range["start"] <= line <= line_range["end"]:
                    return True

        return False

    def filter(self, flags: SASTFlagSet) -> SASTFlagSet:
        """
        Filter out SAST flags unreachable from the main function.

        :param flags:
        :return:
        """
        return SASTFlagSet(set(filter(lambda flag: self._is_reachable(flag.file, flag.line), flags)))
