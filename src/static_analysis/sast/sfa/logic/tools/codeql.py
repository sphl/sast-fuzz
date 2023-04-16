import subprocess as proc
from os import path

from sfa.config import SHELL, BUILD_SCRIPT_NAME, CODEQL, CODEQL_RULE_SET, CODEQL_NUM_THREADS
from sfa.logic.tools.base import SASTTool, SASTToolOutput, convert_sarif
from sfa.utils.io import copy_dir, read


class CodeQL(SASTTool):
    """CodeQL runner implementation."""

    def __init__(self, subject_dir: str):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: str) -> str:
        assert path.exists(path.join(self._subject_dir, BUILD_SCRIPT_NAME))

        result_dir = path.join(temp_dir, "codeql_res")

        setup_cmd = " ".join(
            [
                f"{CODEQL} database create",
                "--language=cpp",
                "--command=make",
                f"--threads={CODEQL_NUM_THREADS}",
                result_dir
            ]
        )

        proc.run([SHELL, BUILD_SCRIPT_NAME, setup_cmd], cwd=copy_dir(self._subject_dir, temp_dir), env=self._setup_env)

        return result_dir

    def _analyze(self, working_dir: str) -> str:
        result_file = path.join(working_dir, "report.sarif")

        # exec_cmd = " ".join(
        #     [
        #         f"{CODEQL} database analyze",
        #         f"--output={result_file}",
        #         "--format=sarifv2.1.0",
        #         f"--threads={CODEQL_NUM_THREADS}",
        #         working_dir
        #     ] + CODEQL_RULE_SET
        # )
        #
        # proc.run(exec_cmd, shell=True)

        exec_cmd = [
            CODEQL,
            "database",
            "analyze",
            f"--output={result_file}",
            "--format=sarifv2.1.0",
            f"--threads={CODEQL_NUM_THREADS}",
            working_dir
        ] + CODEQL_RULE_SET

        proc.run(exec_cmd)

        assert path.exists(result_file)

        return read(result_file)

    def _format(self, findings: str) -> SASTToolOutput:
        return convert_sarif(findings)
