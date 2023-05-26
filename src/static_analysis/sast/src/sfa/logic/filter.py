import json
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any

from sfa.logic import SASTToolFlags
from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory


class SASTFilter(ExtendedEnum):
    REH = "reachability"


class SASTFlagFilter(ABC):
    """
    Abstract SAST flag filter.
    """

    def __init__(self, inspec_file: Path) -> None:
        self._inspec_file = inspec_file

    @abstractmethod
    def filter(self, flags: SASTToolFlags) -> SASTToolFlags:
        """
        Filter out certain SAST flags.

        :param flags:
        :return:
        """
        pass


class ReachabilityFilter(SASTFlagFilter):
    """
    Filter for sorting out SAST flags that are not reachable from the main function.
    """

    def __init__(self, inspec_file: Path) -> None:
        super().__init__(inspec_file)
        self._reachable_code: Dict[str, List[Dict]] = defaultdict(list)

        with inspec_file.open("r") as json_file:
            data = json.load(json_file)

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
            for _range in self._reachable_code[file]:
                if _range["start"] <= line <= _range["end"]:
                    return True

        return False

    def filter(self, flags: SASTToolFlags) -> SASTToolFlags:
        """
        Filter out SAST flags that are not reachable from the main function.

        :param flags:
        :return:
        """
        return SASTToolFlags(set(filter(lambda f: self._is_reachable(f.file, f.line), flags)))


class FilterFactory(Factory):
    """
    SAST flag filter factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {SASTFilter.REH: ReachabilityFilter(param)}
