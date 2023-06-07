import json
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Dict

from sfa.analysis import GroupedSASTFlag, SASTFlags

# Character to concatenate values
CONCAT_CHAR = "-"

# Container for basic block information
BBInfo = namedtuple("BBInfo", ["file", "line_start", "line_end", "n_lines"])


class SASTFlagGrouping(ABC):
    """
    Abstract SAST flag grouping.
    """

    def __init__(self, inspec_file: Path) -> None:
        self._inspec_file = inspec_file

    @abstractmethod
    def group(self, flags: SASTFlags) -> SASTFlags:
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
        self._bb_infos: Dict[int, BBInfo] = {}

        data = json.loads(inspec_file.read_text())

        for func in data["functions"]:
            for bb in func["basic_blocks"]:
                self._bb_infos[bb["id"]] = BBInfo(
                    func["location"]["filename"],
                    bb["location"]["line"]["start"],
                    bb["location"]["line"]["end"],
                    bb["LoC"],
                )

    def group(self, flags: SASTFlags) -> SASTFlags:
        """
        Group SAST flags based on basic block granularity.

        :param flags:
        :return:
        """
        flags_per_bb: Dict = defaultdict(set)

        for flag in flags:
            for bb_id, bb_info in self._bb_infos.items():
                if flag.file == bb_info.file:
                    if bb_info.line_start <= flag.line <= bb_info.line_end:
                        flags_per_bb[bb_id].add(flag)
                        break

        n_tools = len({flag.tool for flag in flags})
        grouped_flags = SASTFlags()

        for bb_id, bb_flags in flags_per_bb.items():
            bb_tools = {flag.tool for flag in bb_flags}
            bb_vulns = {f"{flag.vuln}:{flag.line}" for flag in bb_flags}

            grouped_flags.add(
                GroupedSASTFlag(
                    CONCAT_CHAR.join(bb_tools),
                    self._bb_infos[bb_id].file,
                    self._bb_infos[bb_id].line_start,
                    CONCAT_CHAR.join(bb_vulns),
                    len({flag.line for flag in bb_flags}),
                    self._bb_infos[bb_id].n_lines,
                    len(bb_tools),
                    n_tools,
                )
            )

        return grouped_flags
