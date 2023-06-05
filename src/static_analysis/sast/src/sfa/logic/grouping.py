import json
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Set

from sfa.logic import GroupedSASTFlag, SASTFlag, SASTFlagSet
from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory

# Character for joining multiple values
CONCAT_CHAR = "-"


class SASTFlagGroupingMode(ExtendedEnum):
    BASIC_BLOCK = "basic-block"


class SASTFlagGroupingFactory(Factory):
    """
    SAST flag grouping factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {SASTFlagGroupingMode.BASIC_BLOCK: BasicBlockGrouping(param)}


class SASTFlagGrouping(ABC):
    """
    Abstract SAST flag grouping.
    """

    def __init__(self, inspec_file: Path) -> None:
        self._inspec_file = inspec_file

    @abstractmethod
    def group(self, flags: SASTFlagSet) -> SASTFlagSet:
        """
        Group SAST flags based on a certain code granularity.

        :param flags:
        :return:
        """
        pass


class BasicBlockGrouping(SASTFlagGrouping):
    """
    SAST flag basic block grouping.
    """

    def __init__(self, inspec_file: Path) -> None:
        super().__init__(inspec_file)
        self._bb_infos: Dict = {}

        data = json.loads(inspec_file.read_text())

        for func in data["functions"]:
            for bb in func["basic_blocks"]:
                self._bb_infos[bb["id"]] = {
                    "file": func["location"]["filename"],
                    "line_range": bb["location"]["line"],
                    "LoC": bb["LoC"],
                }

    def group(self, flags: SASTFlagSet) -> SASTFlagSet:
        """
        Group SAST flags based on basic block granularity.

        :param flags:
        :return:
        """
        flags_per_bb: Dict = defaultdict(set)

        for flag in flags:
            for bb_id, bb_info in self._bb_infos.items():
                if flag.file == bb_info["file"]:
                    line_range = bb_info["line_range"]
                    if line_range["start"] <= flag.line <= line_range["end"]:
                        flags_per_bb[bb_id].add(flag)
                        break

        n_tools = len({flag.tool for flag in flags})

        grouped_flags = SASTFlagSet()

        for bb_id, bb_flags in flags_per_bb.items():
            bb_tools = {flag.tool for flag in bb_flags}
            bb_vulns = {f"{flag.vuln}:{flag.line}" for flag in bb_flags}

            grouped_flags.add(
                GroupedSASTFlag(
                    CONCAT_CHAR.join(bb_tools),
                    self._bb_infos[bb_id]["file"],
                    self._bb_infos[bb_id]["line_range"]["start"],
                    CONCAT_CHAR.join(bb_vulns),
                    len({flag.line for flag in bb_flags}),
                    self._bb_infos[bb_id]["LoC"],
                    len(bb_tools),
                    n_tools,
                )
            )

        return grouped_flags
