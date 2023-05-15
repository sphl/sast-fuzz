# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
import json
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Set, Dict, Any

from sfa.logic import SASTToolFlags
from sfa.util.factory import Factory


class SASTFilter(Enum):
    REH = "reachability"


class SASTFlagFilter(ABC):
    """
    Abstract SAST flag filter.
    """

    def __init__(self, inspec_file: Path) -> None:
        self._inspec_file = inspec_file

    @abstractmethod
    def filter(self, flags: SASTToolFlags) -> SASTToolFlags:
        pass


class ReachabilityFilter(SASTFlagFilter):
    """
    Filter for sorting out SAST flags that are not reachable from the main function.
    """

    def __init__(self, inspec_file: Path) -> None:
        super().__init__(inspec_file)
        self._reachable_code: Dict[str, Set[Dict]] = defaultdict(set)

        with inspec_file.open("r") as json_file:
            data = json.load(json_file)

        for func in data["functions"]:
            if func["location"]["reachable_from_main"]:
                self._reachable_code[func["location"]["filename"]].add(func["location"]["line"])

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
        return SASTToolFlags(set(filter(lambda f: self._is_reachable(f.file, int(f.line)), flags)))


class FilterFactory(Factory):
    """
    SAST flag filter factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {SASTFilter.REH: ReachabilityFilter(param)}
