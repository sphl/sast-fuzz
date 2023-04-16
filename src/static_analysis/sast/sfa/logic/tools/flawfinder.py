import subprocess as proc

from sfa.config import FLAWFINDER, FLAWFINDER_RULE_SET
from sfa.logic.tools.base import SASTTool, SASTToolOutput, convert_sarif


class Flawfinder(SASTTool):

    def __init__(self, subject_dir: str):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: str) -> str:
        return self._subject_dir

    def _analyze(self, working_dir: str) -> str:
        exec_cmd = " ".join(
            [FLAWFINDER, "--dataonly", "--sarif"] + FLAWFINDER_RULE_SET + [working_dir]
        )

        return proc.run(exec_cmd, shell=True, capture_output=True, text=True, encoding="utf-8").stdout

    def _format(self, findings: str) -> SASTToolOutput:
        return convert_sarif(findings)
