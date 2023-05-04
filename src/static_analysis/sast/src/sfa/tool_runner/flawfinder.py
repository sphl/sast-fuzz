import subprocess as proc
from pathlib import Path

from sfa.config import FLAWFINDER, FLAWFINDER_FLAG_SET
from sfa.tool_runner.base import SASTTool, SASTToolOutput, SASTToolRunner, convert_sarif


class FlawfinderRunner(SASTToolRunner):
    """Flawfinder runner."""

    def __init__(self, subject_dir: Path):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: Path) -> Path:
        # Since Flawfinder does not attach itself to the build process, we directly perform the analysis in the
        # subject's source directory.
        return self._subject_dir

    def _analyze(self, working_dir: Path) -> str:
        exec_cmd = " ".join(
            [FLAWFINDER, "--dataonly", "--sarif"] + FLAWFINDER_FLAG_SET + [working_dir]
        )

        return proc.run(exec_cmd, shell=True, capture_output=True, text=True, encoding="utf-8").stdout

    def _format(self, flags: str) -> SASTToolOutput:
        return convert_sarif(flags, SASTTool.FLF)
