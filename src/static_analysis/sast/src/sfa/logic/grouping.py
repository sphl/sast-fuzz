import json
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

from sfa.logic import SASTToolFlag, GroupedSASTToolFlag, SASTToolFlags
from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory

# Character for joining multiple values
CONCAT_CHAR = "-"


class GroupingMode(ExtendedEnum):
    BASIC_BLOCK = "basic_block"


class Grouping(ABC):
    """
    Abstract SAST flag grouping.
    """

    def __init__(self, inspec_file: Path, n_tools: int) -> None:
        self._inspec_file = inspec_file
        self._n_tools = n_tools

    @abstractmethod
    def group(self, flags: SASTToolFlags) -> GroupedSASTToolFlag:
        """
        Group SAST flags based on to certain heuristics.

        :param flags:
        :return:
        """
        pass


class BasicBlockGrouping(Grouping):
    """
    Group SAST flags based on basic blocks.
    """

    def __init__(self, inspec_file: Path, n_tools: int) -> None:
        super().__init__(inspec_file, n_tools)
        self._bb_info: Dict[int, Dict[str, Any]] = {}

        funcs = json.loads(inspec_file.read_text())["functions"]
        for func in funcs:
            for bb in func["basic_blocks"]:
                self._bb_info[bb["id"]] = {"file": func["location"]["filename"], "range": bb["location"]["line"], "LoC": bb["LoC"]}

    def group(self, flags: SASTToolFlags) -> SASTToolFlags:
        """
        Group SAST flags based on the code range of basic blocks in the target program.
        """
        flags_per_bb = defaultdict(set)

        for flag in flags:
            for bb_id, bb_info in self._bb_info.items():
                if flag.file == bb_info["file"]:
                    if bb_info["range"]["start"] <= flag.line <= bb_info["range"]["end"]:
                        flags_per_bb[bb_id].add(flag)
                        # BB found, continue with next flag
                        break

        grouped_flags = SASTToolFlags()

        for bb_id, bb_flags in flags_per_bb.items():
            tools_per_bb = {flag.tool for flag in bb_flags}
            vulns_per_bb = {f"{flag.vuln}:{flag.line}" for flag in bb_flags}

            grouped_flags.add(GroupedSASTToolFlag(CONCAT_CHAR.join(tools_per_bb), self._bb_info[bb_id]["file"], self._bb_info[bb_id]["range"]["start"], CONCAT_CHAR.join(vulns_per_bb), len({flag.line for flag in bb_flags}), self._bb_info[bb_id]["LoC"], len(tools_per_bb), self._n_tools))

        return grouped_flags


class GroupingFactory(Factory):
    """
    SAST flag grouping factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {
            GroupingMode.BASIC_BLOCK: BasicBlockGrouping(*param),
        }
