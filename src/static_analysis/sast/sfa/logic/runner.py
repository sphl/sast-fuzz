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


def run_sast_tools(runners: List[SASTToolRunner], exec_parallel: bool = True) -> SASTToolOutput:
    """Run multiple SAST tools.

    This function executes the passed SAST tool runners in parallel resp. sequence, followed by merging the tools'
    output into a single result set.

    :param runners: SAST tool runners
    :param exec_parallel: Parallel runner execution
    :return: Output of SAST tools
    """
    assert len(runners) > 0

    if not exec_parallel:
        temp_res = list(map(lambda tool: tool.run(), runners))
    else:
        with Pool(len(runners)) as pool:
            temp_res = pool.map(_starter, runners)

    findings = set(chain(*temp_res))

    return findings
