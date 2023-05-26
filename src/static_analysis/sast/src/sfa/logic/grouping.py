import json
from pathlib import Path
from collections import defaultdict
from abc import ABC, abstractmethod

from typing import Any, Dict

from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory
from sfa.logic import SASTToolFlag, SASTToolFlags

# Character for joining multiple values
CONCAT_CHAR = "-"


class GroupingMode(ExtendedEnum):
    NONE = 0
    BASIC_BLOCK = 1


class Grouping(ABC):
    """
    Abstract SAST flag grouping.
    """

    def __init__(self, inspec_file: Path) -> None:
        self._inspec_file = inspec_file

    @abstractmethod
    def group(self, flags: SASTToolFlags) -> SASTToolFlags:
        """
        Group SAST flags based on to certain heuristics.

        :param flags:
        :return:
        """
        pass


class NoneGrouping(Grouping):
    """
    No grouping.
    """

    def group(self, flags: SASTToolFlags) -> SASTToolFlags:
        """
        Dummy grouping that returns the passed SAST flags unchanged.

        :param flags:
        :return:
        """
        return flags


class BasicBlockGrouping(Grouping):
    """
    Group SAST flags based on basic blocks.
    """

    def __init__(self, inspec_file: Path) -> None:
        super().__init__(inspec_file)
        self._bb_infos: Dict[int, Dict[str, Any]] = {}

        for func in json.loads(inspec_file.read_text())["functions"]:
            for bb in func["basic_blocks"]:
                self._bb_infos[bb["id"]] = {"file": func["file"], "line_range": bb["line"]}

    def group(self, flags: SASTToolFlags) -> SASTToolFlags:
        """
        Group SAST flags based on the source code boundaries (i.e. first and last line number) of basic blocks in the
        target program.

        :param flags:
        :return:
        """
        flags_per_bb = defaultdict(set)

        for flag in flags:
            for bb_id, bb_info in self._bb_infos.items():
                if flag.file == bb_info["file"]:
                    # Check if flagged line is within basic block range
                    if bb_info["line_range"]["start"] <= flag.line <= bb_info["line_range"]["end"]:
                        flags_per_bb[bb_id].add(flag)
                        break

        grouped_flags = SASTToolFlags()

        for bb_id, bb_flags in flags_per_bb.items():
            bb_tools = set([flag.tool for flag in bb_flags])

            tool = CONCAT_CHAR.join(bb_tools)
            file = self._bb_infos[bb_id]["file"]
            line = self._bb_infos[bb_id]["line_range"]["start"]
            vuln = CONCAT_CHAR.join([f"{flag.tool}:{flag.vuln}:{flag.line}" for flag in bb_flags])

            n_flags = len(bb_flags)
            n_tools = len(bb_tools)

            grouped_flags.add(SASTToolFlag(tool, file, line, vuln, n_flags, n_tools))

        return grouped_flags


class GroupingFactory(Factory):
    """
    SAST flag grouping factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {
            GroupingMode.NONE: NoneGrouping(param),
            GroupingMode.BASIC_BLOCK: BasicBlockGrouping(param)
        }
