import json
from dataclasses import dataclass, field
from functools import reduce
from itertools import chain
from pathlib import Path
from typing import List, Dict, Optional

from sfa.logic.filter import SASTFilter, FilterFactory
from sfa.logic.tool_runner import SASTTool, SASTToolFlags, SASTToolRunner, RunnerFactory
from sfa.util.io import read
from sfa.util.proc import run_with_multi_processing
from sfa.util.timer import get_exec_time

# Number of spaces
JSON_INDENT: int = 4


def _starter(runner: SASTToolRunner) -> SASTToolFlags:
    return runner.run()


@dataclass()
class AnalysisInfo:
    """
    Container for analysis information.
    """

    sast_tools: List[str] = field(init=False, default_factory=lambda: [])
    filters: List[str] = field(init=False, default_factory=lambda: [])
    num_jobs: int = field(init=False, default=0)
    exec_time_sast: float = field(init=False, default=0.0)
    exec_time_filtering: float = field(init=False, default=0.0)
    num_lines_subject: int = field(init=False, default=0)
    num_lines_flagged: int = field(init=False, default=0)
    num_lines_removed: int = field(init=False, default=0)

    def as_dict(self) -> Dict:
        return {
            "sast_tools": self.sast_tools,
            "filters": self.filters,
            "num_jobs": self.num_jobs,
            "exec_time": {"sast": self.exec_time_sast, "filtering": self.exec_time_filtering},
            "num_lines": {
                "subject": self.num_lines_subject,
                "flagged": self.num_lines_flagged,
                "removed": self.num_lines_removed,
            },
        }

    def to_json(self, file: Path) -> None:
        with file.open("w") as json_file:
            json.dump(self.as_dict(), json_file, indent=JSON_INDENT)

    def __str__(self) -> str:
        return json.dumps(self.as_dict(), indent=JSON_INDENT)


class Analyzer:
    """
    Main analyzer component.
    """

    def __init__(self, inspec_file: Path, subject_dir: Optional[Path] = None) -> None:
        self.info = AnalysisInfo()
        self.info.num_lines_subject = sum([f["LoC"] for f in json.loads(read(inspec_file))["functions"]])

        self._runner_factory = RunnerFactory(subject_dir)
        self._filter_factory = FilterFactory(inspec_file)

    def analyze(self, tools: List[SASTTool], parallel: bool) -> SASTToolFlags:
        """
        Perform static analysis by running the SAST tools.

        :param tools:
        :param parallel:
        :return:
        """
        if not parallel:
            n_jobs = 1
        else:
            n_jobs = len(tools)

        runners = list(self._runner_factory.get_instances(tools))

        nested_flags, exec_time = get_exec_time(lambda: run_with_multi_processing(_starter, runners, n_jobs))
        flags = SASTToolFlags(set(chain(*nested_flags)))

        self.info.sast_tools = [t.value for t in tools]
        self.info.num_jobs = n_jobs
        self.info.exec_time_sast = exec_time
        self.info.num_lines_flagged = len(flags)

        return flags

    def filter(self, flags: SASTToolFlags, filters: List[SASTFilter]) -> SASTToolFlags:
        """
        Filter SAST tool flags.

        :param flags:
        :param filters:
        :return:
        """
        _filters = self._filter_factory.get_instances(filters)

        filtered_flags, exec_time = get_exec_time(lambda: reduce(lambda acc, f: f.filter(acc), _filters, flags))

        self.info.filters = [f.value for f in filters]
        self.info.exec_time_filtering = exec_time
        self.info.num_lines_flagged = len(flags)
        self.info.num_lines_removed = len(flags) - len(filtered_flags)

        return filtered_flags

    def run(self, tools: List[SASTTool], filters: List[SASTFilter], parallel: bool) -> SASTToolFlags:
        """
        Run SAST tools and filter their flags in one step.

        :param tools:
        :param filters:
        :param parallel:
        :return:
        """
        return self.filter(self.analyze(tools, parallel), filters)
