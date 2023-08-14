import json
from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Dict

from sfa import ScoreWeights
from sfa.analysis import GroupedSASTFlag, SASTFlags

# Decimal precision of the vulnerability scores
SCORE_PRECISION = 3

# Character to concatenate values
CONCAT_CHAR = "-"

# Container for code block information
CodeBlockInfo = namedtuple("CodeBlockInfo", ["file", "line_start", "line_end", "n_lines"])


class SASTFlagGrouping(ABC):
    """
    Abstract SAST flag grouping.
    """

    def __init__(self, inspec_file: Path, weights: ScoreWeights) -> None:
        self._inspec_file = inspec_file
        self._weights = weights

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

    def __init__(self, inspec_file: Path, weights: ScoreWeights) -> None:
        super().__init__(inspec_file, weights)
        self._bb_infos: Dict[int, CodeBlockInfo] = {}

        data = json.loads(inspec_file.read_text())

        for func in data["functions"]:
            for bb in func["basic_blocks"]:
                self._bb_infos[bb["id"]] = CodeBlockInfo(
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

            n_flg_lines = len({flag.line for flag in bb_flags})
            n_all_lines = self._bb_infos[bb_id].n_lines
            n_run_tools = len(bb_tools)
            n_all_tools = n_tools

            r_flg_lines = n_flg_lines / n_all_lines
            r_run_tools = n_run_tools / n_all_tools

            # Calculate the vulnerability score
            score = round((self._weights.flags * r_flg_lines) + (self._weights.tools * r_run_tools), SCORE_PRECISION)

            grouped_flags.add(
                GroupedSASTFlag(
                    CONCAT_CHAR.join(bb_tools),
                    self._bb_infos[bb_id].file,
                    self._bb_infos[bb_id].line_start,
                    CONCAT_CHAR.join(bb_vulns),
                    n_flg_lines,
                    n_all_lines,
                    n_run_tools,
                    n_all_tools,
                    score,
                )
            )

        return grouped_flags


class FunctionGrouping(SASTFlagGrouping):
    """
    SAST flag function grouping.
    """

    def __init__(self, inspec_file: Path, weights: ScoreWeights) -> None:
        super().__init__(inspec_file, weights)
        self._func_infos: Dict[str, CodeBlockInfo] = {}

        data = json.loads(inspec_file.read_text())

        for func in data["functions"]:
            func_name = f"{func['location']['filename']}:{func['name']}"
            self._func_infos[func_name] = CodeBlockInfo(
                func["location"]["filename"],
                func["location"]["line"]["start"],
                func["location"]["line"]["end"],
                func["LoC"],
            )

    def group(self, flags: SASTFlags) -> SASTFlags:
        """
        Group SAST flags based on basic block granularity.

        :param flags:
        :return:
        """
        flags_per_func: Dict = defaultdict(set)

        for flag in flags:
            for func_name, func_info in self._func_infos.items():
                if flag.file == func_info.file:
                    if func_info.line_start <= flag.line <= func_info.line_end:
                        flags_per_func[func_name].add(flag)
                        break

        n_tools = len({flag.tool for flag in flags})
        grouped_flags = SASTFlags()

        for func_name, bb_flags in flags_per_func.items():
            bb_tools = {flag.tool for flag in bb_flags}
            bb_vulns = {f"{flag.vuln}:{flag.line}" for flag in bb_flags}

            n_flg_lines = len({flag.line for flag in bb_flags})
            n_all_lines = self._func_infos[func_name].n_lines
            n_run_tools = len(bb_tools)
            n_all_tools = n_tools

            r_flg_lines = n_flg_lines / n_all_lines
            r_run_tools = n_run_tools / n_all_tools

            # Calculate the vulnerability score
            score = round((self._weights.flags * r_flg_lines) + (self._weights.tools * r_run_tools), SCORE_PRECISION)

            grouped_flags.add(
                GroupedSASTFlag(
                    CONCAT_CHAR.join(bb_tools),
                    self._func_infos[func_name].file,
                    self._func_infos[func_name].line_start + 1,
                    CONCAT_CHAR.join(bb_vulns),
                    n_flg_lines,
                    n_all_lines,
                    n_run_tools,
                    n_all_tools,
                    score,
                )
            )

        return grouped_flags
