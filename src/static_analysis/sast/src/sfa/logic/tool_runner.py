import json
import os
from abc import ABC, abstractmethod
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any, ClassVar

from sfa.config import (
    BUILD_SCRIPT_NAME,
    FLAWFINDER,
    FLAWFINDER_FLAG_SET,
    INFER,
    INFER_RULE_SET,
    INFER_NUM_THREADS,
    CODEQL,
    CODEQL_RULE_SET,
    CODEQL_NUM_THREADS,
    CLANG_SCAN,
    CLANG_SCAN_RULE_SET,
)
from sfa.logic import SAST_SETUP_ENV, SASTToolFlag, SASTToolFlags, convert_sarif
from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory
from sfa.util.fs import copy_dir, find_files
from sfa.util.io import read
from sfa.util.proc import run_shell_command


class SASTTool(ExtendedEnum):
    FLF = "flawfinder"
    IFR = "infer"
    CQL = "codeql"
    CLS = "clang-scan"
    ASN = "asan"
    # MSN = "msan"


class SASTToolRunner(ABC):
    """
    Abstract SAST tool runner.
    """

    def __init__(self, subject_dir: Path) -> None:
        self._subject_dir = subject_dir

    @abstractmethod
    def _setup(self, temp_dir: Path) -> Path:
        """
        Run pre-analysis step(s) required by the SAST tool.

        :param temp_dir:
        :return:
        """
        pass

    @abstractmethod
    def _analyze(self, working_dir: Path) -> str:
        """
        Execute SAST tool on target program.

        :param working_dir:
        :return:
        """
        pass

    @abstractmethod
    def _format(self, string: str) -> SASTToolFlags:
        """
        Convert SAST tool-specific output into common data format.

        :param flags:
        :return:
        """
        pass

    def run(self) -> SASTToolFlags:
        """
        Run setup, SAST tool analysis, and output formatting in sequence.

        :return:
        """
        with TemporaryDirectory() as temp_dir:
            working_dir = self._setup(Path(temp_dir))
            flags = self._format(self._analyze(working_dir))

        return flags


class FlawfinderRunner(SASTToolRunner):
    """
    Flawfinder runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        # Since Flawfinder doesn't attach to the build process, we run it directly in the subject's directory
        return self._subject_dir

    def _analyze(self, working_dir: Path) -> str:
        return run_shell_command(f"{FLAWFINDER} --dataonly --sarif {' '.join(FLAWFINDER_FLAG_SET)} {working_dir}")

    def _format(self, string: str) -> SASTToolFlags:
        return convert_sarif(string)


class InferRunner(SASTToolRunner):
    """
    Infer runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / Path("infer_res")

        run_shell_command(
            f'./{BUILD_SCRIPT_NAME} "{INFER} capture --results-dir {result_dir} -- make"',
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        run_shell_command(
            f"{INFER} analyze --results-dir {working_dir} --jobs {INFER_NUM_THREADS} --keep-going {' '.join(INFER_RULE_SET)}"
        )

        # By default, Infer writes the results into the 'report.json' file once the analysis is complete.
        result_file = working_dir / Path("report.json")

        if not result_file.exists():
            raise Exception(f"Infer: Failed to create the result file '{result_file}'!")

        return read(result_file)

    def _format(self, string: str) -> SASTToolFlags:
        flags = SASTToolFlags()

        for flag in json.loads(string):
            tool = SASTTool.IFR.value
            file = flag["file"]
            line = flag["line"]
            vuln = flag["bug_type"]

            file = Path(file).name

            flags.add(SASTToolFlag(tool, file, line, vuln))

        return flags


class CodeQLRunner(SASTToolRunner):
    """
    CodeQL runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / Path("codeql_res")

        run_shell_command(
            f'./{BUILD_SCRIPT_NAME} "{CODEQL} database create --language=cpp --command=make --threads={CODEQL_NUM_THREADS} {result_dir}"',
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_file = working_dir / Path("report.sarif")

        run_shell_command(
            f"{CODEQL} database analyze --output={result_file} --format=sarifv2.1.0 --threads={CODEQL_NUM_THREADS} {working_dir} {' '.join(CODEQL_RULE_SET)}"
        )

        if not result_file.exists():
            raise Exception(f"CodeQL: Failed to create the result file '{result_file}'!")

        return read(result_file)

    def _format(self, string: str) -> SASTToolFlags:
        return convert_sarif(string)


class ClangScanRunner(SASTToolRunner):
    """
    Clang analyzer (scan-build) runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / Path("clang-scan_res")

        run_shell_command(
            f"./{BUILD_SCRIPT_NAME} \"{CLANG_SCAN} -o {result_dir} --keep-empty -sarif {' '.join(CLANG_SCAN_RULE_SET)} make\"",
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_files = find_files(working_dir, exts=[".sarif"])

        if len(result_files) == 0:
            raise Exception("Clang-Scan: Failed to create the result file(s)!")

        # Clang analyzer writes the results of each checker into a separate SARIF file. Therefore, we append the results
        # (JSON string) of each file as one line to the return string.
        return os.linesep.join(map(lambda f: json.dumps(json.loads(read(f)), indent=None), result_files))

    def _format(self, string: str) -> SASTToolFlags:
        flags = map(convert_sarif, string.split(os.linesep))

        return SASTToolFlags(set(chain(*flags)))


class SanitizerRunner(SASTToolRunner):
    """
    Abstract sanitizer runner.
    """

    _report_name: ClassVar[str] = "report.csv"

    @abstractmethod
    def _env_vars(self, result_file: Path) -> Dict[str, str]:
        pass

    def _setup(self, temp_dir: Path) -> Path:
        result_file = temp_dir / Path(self._report_name)

        run_shell_command(
            f"./{BUILD_SCRIPT_NAME}", cwd=copy_dir(self._subject_dir, temp_dir), env=self._env_vars(result_file)
        )

        if not result_file.exists():
            raise Exception(f"Sanitizer: Failed to create the result file '{result_file}'!")

        return temp_dir

    def _analyze(self, working_dir: Path) -> str:
        return read(working_dir / Path(self._report_name))

    def _format(self, string: str) -> SASTToolFlags:
        flags = SASTToolFlags()

        for _line in string.split(os.linesep):
            if _line != "":
                vals = _line.split(",")

                tool = vals[0]
                file = vals[1]
                line = vals[3]
                vuln = "-"

                flags.add(SASTToolFlag(tool, file, line, vuln))

        return flags


class AddressSanitizerRunner(SanitizerRunner):
    """
    AddressSanitizer runner.
    """

    def _env_vars(self, result_file: Path) -> Dict[str, str]:
        setup_env = SAST_SETUP_ENV

        for flag in ["CFLAGS", "CXXFLAGS"]:
            setup_env[flag] = f"{setup_env[flag]} -g -fsanitize=address"

        setup_env["ASAN_OUTPUT_FILE"] = str(result_file)

        return setup_env


class MemorySanitizerRunner(SanitizerRunner):
    """
    MemorySanitizer runner.
    """

    def _env_vars(self, result_file: Path) -> Dict[str, str]:
        setup_env = SAST_SETUP_ENV

        for flag in ["CFLAGS", "CXXFLAGS"]:
            setup_env[flag] = f"{setup_env[flag]} -g -fsanitize=memory"

        setup_env["MSAN_OUTPUT_FILE"] = str(result_file)

        return setup_env


class RunnerFactory(Factory):
    """
    SAST tool runner factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {
            SASTTool.FLF: FlawfinderRunner(param),
            SASTTool.IFR: InferRunner(param),
            SASTTool.CQL: CodeQLRunner(param),
            SASTTool.CLS: ClangScanRunner(param),
            SASTTool.ASN: AddressSanitizerRunner(param),
            # SASTTool.MSN: MemorySanitizerRunner(param),
        }
