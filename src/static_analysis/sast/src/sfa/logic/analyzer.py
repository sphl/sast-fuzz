from functools import reduce
from itertools import chain
from pathlib import Path
from typing import List, Optional

from sfa.logic.filter import SASTFilter, FilterFactory
from sfa.logic.tool_runner import SASTTool, SASTToolFlags, RunnerFactory
from sfa.util.proc import run_with_multi_processing


class Analyzer:
    """
    Main analyzer component.
    """

    def __init__(self, inspec_file: Path, subject_dir: Optional[Path] = None) -> None:
        self._runner_factory = RunnerFactory(subject_dir)
        self._filter_factory = FilterFactory(inspec_file)

    def analyze(self, tools: List[SASTTool], n_jobs: int) -> SASTToolFlags:
        """
        Perform static analysis by running the SAST tools.

        :param tools:
        :param n_jobs:
        :return:
        """
        runners = self._runner_factory.get_instances(tools)

        nested_flags = run_with_multi_processing(lambda r: r.run(), runners, n_jobs)
        flags = set(chain(*nested_flags))

        return flags

    def filter(self, flags: SASTToolFlags, filters: List[SASTFilter]) -> SASTToolFlags:
        """
        Filter SAST tool flags.

        :param flags:
        :param filters:
        :return:
        """
        filters = self._filter_factory.get_instances(filters)

        return reduce(lambda acc, f: f.filter(acc), filters, flags)

    def run(self, tools: List[SASTTool], filters: List[SASTFilter], n_jobs: int) -> SASTToolFlags:
        """
        Run SAST tools and filter their flags in one step.

        :param tools:
        :param filters:
        :param n_jobs:
        :return:
        """
        return self.filter(self.analyze(tools, n_jobs), filters)
