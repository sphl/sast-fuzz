from itertools import chain
from multiprocessing import Pool
from typing import List

from sfa.logic.tools.base import SASTToolRunner, SASTToolOutput


def _starter(tool: SASTToolRunner) -> SASTToolOutput:
    """Run a single SAST tool.

    :param tool: SAST tool runner
    :return: SAST tool output
    """
    return tool.run()


def run_sast_tools(tools: List[SASTToolRunner], run_parallel: bool = True) -> SASTToolOutput:
    """Run multiple SAST tools.

    Given a list of SAST tools, this function executes the corresponding runners in parallel resp. sequence, followed by
    merging the tools' output into a single result set.

    :param tools: SAST tool runners
    :param run_parallel: Parallel runner exec.
    :return: Output of SAST tools
    """
    assert len(tools) > 0

    if not run_parallel:
        temp_res = list(map(lambda tool: tool.run(), tools))
    else:
        with Pool(len(tools)) as pool:
            temp_res = pool.map(_starter, tools)

    findings = set(chain(*temp_res))

    return findings
