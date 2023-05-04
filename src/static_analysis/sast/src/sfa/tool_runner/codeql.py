import subprocess as proc
from pathlib import Path

from sfa.config import SHELL, BUILD_SCRIPT_NAME, CODEQL, CODEQL_RULE_SET, CODEQL_NUM_THREADS
from sfa.tool_runner.base import SASTTool, SASTToolOutput, SASTToolRunner, convert_sarif
from sfa.util.io import copy_dir, read


class CodeQLRunner(SASTToolRunner):
    """CodeQL runner implementation."""

    def __init__(self, subject_dir: Path):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: Path) -> Path:
        assert (self._subject_dir / Path(BUILD_SCRIPT_NAME)).exists()

        result_dir = temp_dir / Path("codeql_res")

        setup_cmd = " ".join(
            [
                f"{CODEQL} database create",
                "--language=cpp",
                "--command=make",
                f"--threads={CODEQL_NUM_THREADS}",
                str(result_dir)
            ]
        )

        proc.run([SHELL, BUILD_SCRIPT_NAME, setup_cmd], cwd=copy_dir(self._subject_dir, temp_dir), env=self._setup_env)

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_file = working_dir / Path("report.sarif")

        exec_cmd = " ".join(
            [
                f"{CODEQL} database analyze",
                f"--output={result_file}",
                "--format=sarifv2.1.0",
                f"--threads={CODEQL_NUM_THREADS}",
                working_dir
            ] + CODEQL_RULE_SET
        )

        proc.run(exec_cmd, shell=True)

        assert result_file.exists()

        return read(result_file)

    def _format(self, flags: str) -> SASTToolOutput:
        return convert_sarif(flags, SASTTool.CQL)
