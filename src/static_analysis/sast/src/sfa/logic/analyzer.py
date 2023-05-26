import logging
from functools import reduce
from itertools import chain
from pathlib import Path
from typing import List, Optional

from sfa.logic.filter import SASTFilter, FilterFactory
from sfa.logic.grouping import GroupingMode, GroupingFactory
from sfa.logic.tool_runner import SASTTool, SASTToolFlags, SASTToolRunner, RunnerFactory
from sfa.util.proc import run_with_multi_processing
from sfa.util.timer import get_exec_time


def _starter(runner: SASTToolRunner) -> SASTToolFlags:
    return runner.run()


class Analyzer:
    """
    Main analyzer component.
    """

    def __init__(self, inspec_file: Path, subject_dir: Optional[Path] = None) -> None:
        self._runner_factory = RunnerFactory(subject_dir)
        self._filter_factory = FilterFactory(inspec_file)
        self._grouping_factory = GroupingFactory(inspec_file)

    def analyze(self, tools: List[SASTTool], parallel: bool) -> SASTToolFlags:
        """
        Perform static analysis by running the SAST tools.

        :param tools:
        :param parallel:
        :return:
        """
        logging.info(f"SAST tools: {', '.join([t.value for t in tools])}")

        if not parallel:
            n_jobs = 1
        else:
            n_jobs = len(tools)

        runners = list(self._runner_factory.get_instances(tools))

        nested_flags, exec_time = get_exec_time(lambda: run_with_multi_processing(_starter, runners, n_jobs))
        flags = SASTToolFlags(set(chain(*nested_flags)))

        logging.info(f"Execution time: {exec_time:.2f}s")
        logging.info(f"# Flags: {len(flags)}")

        return flags

    def filter(self, flags: SASTToolFlags, filters: List[SASTFilter]) -> SASTToolFlags:
        """
        Filter SAST tool flags.

        :param flags:
        :param filters:
        :return:
        """
        logging.info(f"Filters: {', '.join([f.value for f in filters])}")

        _filters = self._filter_factory.get_instances(filters)

        filtered_flags = reduce(lambda acc, f: f.filter(acc), _filters, flags)

        logging.info(f"# Flags (filtered): {len(filtered_flags)}")

        return filtered_flags

    def group(self, flags: SASTToolFlags, grouping: GroupingMode) -> SASTToolFlags:
        """
        Group SAST tool flags.

        :param flags:
        :param grouping:
        :return:
        """
        logging.info(f"Grouping: {grouping.value}")

        grouped_flags = self._grouping_factory.get_instance(grouping).group(flags)

        logging.info(f"# Flags (grouped): {len(grouped_flags)}")

        return grouped_flags

    def run(
        self, tools: List[SASTTool], filters: List[SASTFilter], grouping: GroupingMode, parallel: bool
    ) -> SASTToolFlags:
        """
        Run SAST tools, filter their flags and group them in one step.

        :param tools:
        :param filters:
        :param grouping:
        :param parallel:
        :return:
        """
        return self.group(self.filter(self.analyze(tools, parallel), filters), grouping)
