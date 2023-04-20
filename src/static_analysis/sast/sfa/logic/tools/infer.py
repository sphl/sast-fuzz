import json
import subprocess as proc
from os import path

from sfa.config import SHELL, BUILD_SCRIPT_NAME, INFER, INFER_RULE_SET, INFER_NUM_THREADS
from sfa.logic.tools.base import SASTToolRunner, SASTToolFlag, SASTToolOutput
from sfa.utils.io import copy_dir, read


class Infer(SASTToolRunner):
    """Infer runner implementation."""

    def __init__(self, subject_dir: str):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: str) -> str:
        assert path.exists(path.join(self._subject_dir, BUILD_SCRIPT_NAME))

        result_dir = path.join(temp_dir, "infer_res")

        setup_cmd = " ".join(
            [f"{INFER} capture", f"--results-dir {result_dir}", "--", "make"]
        )

        proc.run([SHELL, BUILD_SCRIPT_NAME, setup_cmd], cwd=copy_dir(self._subject_dir, temp_dir), env=self._setup_env)

        return result_dir

    def _analyze(self, working_dir: str) -> str:
        exec_cmd = " ".join(
            [
                f"{INFER} analyze",
                f"--results-dir {working_dir}",
                f"--jobs {INFER_NUM_THREADS}",
                "--keep-going"
            ] + INFER_RULE_SET
        )

        proc.run(exec_cmd, shell=True)

        # By default, Infer writes the results into the 'report.json' file once the analysis is complete.
        result_file = path.join(working_dir, "report.json")

        assert path.exists(result_file)

        return read(result_file)

    def _format(self, findings: str) -> SASTToolOutput:
        result_set = set()

        for finding in json.loads(findings):
            tool_name = "infer"
            file_name = path.basename(finding["file"])
            code_line = int(finding["line"])
            vuln_type = finding["bug_type"]

            result_set.add(SASTToolFlag(tool_name, file_name, code_line, vuln_type))

        return result_set
