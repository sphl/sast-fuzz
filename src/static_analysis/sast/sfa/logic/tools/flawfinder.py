import subprocess as proc

from sfa.config import FLAWFINDER, FLAWFINDER_FLAG_SET
from sfa.logic.tools.base import SASTToolRunner, SASTToolOutput, convert_sarif


class Flawfinder(SASTToolRunner):
    """Flawfinder runner implementation."""

    def __init__(self, subject_dir: str):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: str) -> str:
        # Since Flawfinder does not attach itself to the build process, we directly perform the analysis in the
        # subject's source directory.
        return self._subject_dir

    def _analyze(self, working_dir: str) -> str:
        exec_cmd = " ".join(
            [FLAWFINDER, "--dataonly", "--sarif"] + FLAWFINDER_FLAG_SET + [working_dir]
        )

        return proc.run(exec_cmd, shell=True, capture_output=True, text=True, encoding="utf-8").stdout

    def _format(self, findings: str) -> SASTToolOutput:
        return convert_sarif(findings)
