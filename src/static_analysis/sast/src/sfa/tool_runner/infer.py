import json
import subprocess as proc
from os import path

from sfa import SASTToolFlag, SASTToolOutput
from sfa.config import SHELL, BUILD_SCRIPT_NAME, INFER, INFER_RULE_SET, INFER_NUM_THREADS
from sfa.tool_runner import SASTTool, SASTToolRunner
from sfa.util.io import copy_dir, read


class InferRunner(SASTToolRunner):
    """Infer runner."""

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

    def _format(self, flags: str) -> SASTToolOutput:
        result_set = set()

        for finding in json.loads(flags):
            tool = SASTTool.IFR.value
            file = path.basename(finding["file"])
            line = int(finding["line"])
            vuln = finding["bug_type"]

            result_set.add(SASTToolFlag(tool, file, line, vuln))

        return result_set
