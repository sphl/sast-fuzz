import itertools
import json
import subprocess as proc
from os import linesep, path

from sfa import SASTToolOutput
from sfa.config import SHELL, BUILD_SCRIPT_NAME, CLANGSA, CLANGSA_RULE_SET
from sfa.tool_runner import SASTTool, SASTToolRunner, convert_sarif
from sfa.util.io import read_json, copy_dir, find_files


class ClangScanRunner(SASTToolRunner):
    """Clang analyzer (scan-build) runner."""

    def __init__(self, subject_dir: str):
        super().__init__(subject_dir)

    def _setup(self, temp_dir: str) -> str:
        assert path.exists(path.join(self._subject_dir, BUILD_SCRIPT_NAME))

        result_dir = path.join(temp_dir, "clangsa_res")

        setup_cmd = " ".join(
            [CLANGSA, f"-o {result_dir}", "--keep-empty", "-sarif"] + CLANGSA_RULE_SET + ["make"]
        )

        proc.run([SHELL, BUILD_SCRIPT_NAME, setup_cmd], cwd=copy_dir(self._subject_dir, temp_dir), env=self._setup_env)

        return result_dir

    def _analyze(self, working_dir: str) -> str:
        result_files = find_files(working_dir, file_ext="sarif")

        assert len(result_files) > 0

        # Clang SA writes the results of each checker into a separate SARIF file. Therefore, we append the results
        # (JSON string) of each file as one line to the return string.
        return linesep.join(map(lambda f: json.dumps(read_json(f), indent=None), result_files))

    def _format(self, flags: str) -> SASTToolOutput:
        result_set = map(lambda s: convert_sarif(s, SASTTool.CLS), flags.split(linesep))

        return set(itertools.chain(*result_set))
