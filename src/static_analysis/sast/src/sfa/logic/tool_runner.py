import json
import os
from abc import ABC, abstractmethod
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, ClassVar, Dict

from sfa.config import app_config
from sfa.logic import SAST_SETUP_ENV, SASTFlag, SASTFlagSet, convert_sarif
from sfa.util.ext_enum import ExtendedEnum
from sfa.util.factory import Factory
from sfa.util.fs import copy_dir, find_files
from sfa.util.proc import run_shell_command


class SASTToolException(Exception):
    """
    SAST tool exception.
    """

    pass


class SASTTool(ExtendedEnum):
    FLF = "flawfinder"
    SGR = "semgrep"
    IFR = "infer"
    CQL = "codeql"
    CLS = "clang-scan"
    ASN = "asan"
    MSN = "msan"


class SASTToolRunnerFactory(Factory):
    """
    SAST tool runner factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {
            SASTTool.FLF: FlawfinderRunner(param),
            SASTTool.SGR: SemgrepRunner(param),
            SASTTool.IFR: InferRunner(param),
            SASTTool.CQL: CodeQLRunner(param),
            SASTTool.CLS: ClangScanRunner(param),
            SASTTool.ASN: AddressSanitizerRunner(param),
            SASTTool.MSN: MemorySanitizerRunner(param),
        }


class SASTToolRunner(ABC):
    """
    Abstract SAST tool runner.
    """

    def __init__(self, subject_dir: Path) -> None:
        self._subject_dir = subject_dir

    @abstractmethod
    def _setup(self, temp_dir: Path) -> Path:
        """
        Run certain pre-analysis step(s).

        :param temp_dir:
        :return:
        """
        pass

    @abstractmethod
    def _analyze(self, working_dir: Path) -> str:
        """
        Analyze target program using SAST tool.

        :param working_dir:
        :return:
        """
        pass

    @abstractmethod
    def _format(self, string: str) -> SASTFlagSet:
        """
        Format SAST tool output.

        :param flags:
        :return:
        """
        pass

    def run(self) -> SASTFlagSet:
        """
        Setup target program, run SAST tool, and format output.

        :return:
        """
        with TemporaryDirectory() as temp_dir:
            working_dir = self._setup(Path(temp_dir))
            flags = self._analyze(working_dir)

        return self._format(flags)


class FlawfinderRunner(SASTToolRunner):
    """
    Flawfinder runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        return self._subject_dir

    def _analyze(self, working_dir: Path) -> str:
        return run_shell_command(
            f"{app_config.FLAWFINDER} --dataonly --sarif {' '.join(app_config.FLAWFINDER_CHECKS)} {working_dir}"
        )

    def _format(self, string: str) -> SASTFlagSet:
        return convert_sarif(string)


class SemgrepRunner(SASTToolRunner):
    """
    Semgrep runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        return self._subject_dir

    def _analyze(self, working_dir: Path) -> str:
        return run_shell_command(
            f"{app_config.SEMGREP} scan --quiet --jobs {app_config.SEMGREP_NUM_THREADS} {' '.join([f'--config {check}' for check in app_config.SEMGREP_CHECKS])} --sarif {working_dir}"
        )

    def _format(self, string: str) -> SASTFlagSet:
        return convert_sarif(string)


class InferRunner(SASTToolRunner):
    """
    Infer runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / "infer_res"

        run_shell_command(
            f'./{app_config.BUILD_SCRIPT_NAME} "{app_config.INFER} capture --results-dir {result_dir} -- make"',
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        run_shell_command(
            f"{app_config.INFER} analyze --results-dir {working_dir} --jobs {app_config.INFER_NUM_THREADS} --keep-going {' '.join(app_config.INFER_CHECKS)}"
        )

        # By default, Infer writes the results into the 'report.json' file once the analysis is complete.
        result_file = working_dir / "report.json"

        if not result_file.exists():
            raise SASTToolException("Infer failed to create the analysis report.")

        return result_file.read_text()

    def _format(self, string: str) -> SASTFlagSet:
        flags = SASTFlagSet()

        for flag in json.loads(string):
            tool = SASTTool.IFR.value
            file = flag["file"]
            line = flag["line"]
            vuln = flag["bug_type"]

            file = Path(file).name

            flags.add(SASTFlag(tool, file, line, vuln))

        return flags


class CodeQLRunner(SASTToolRunner):
    """
    CodeQL runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / "codeql_res"

        run_shell_command(
            f'./{app_config.BUILD_SCRIPT_NAME} "{app_config.CODEQL} database create --language=cpp --command=make --threads={app_config.CODEQL_NUM_THREADS} {result_dir}"',
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_file = working_dir / "report.sarif"

        run_shell_command(
            f"{app_config.CODEQL} database analyze --output={result_file} --format=sarifv2.1.0 --threads={app_config.CODEQL_NUM_THREADS} {working_dir} {' '.join(app_config.CODEQL_CHECKS)}"
        )

        if not result_file.exists():
            raise SASTToolException("CodeQL failed to create the analysis report.")

        return result_file.read_text()

    def _format(self, string: str) -> SASTFlagSet:
        return convert_sarif(string)


class ClangScanRunner(SASTToolRunner):
    """
    Clang analyzer (scan-build) runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / "clang-scan_res"

        run_shell_command(
            f"./{app_config.BUILD_SCRIPT_NAME} \"{app_config.CLANG_SCAN} -o {result_dir} --keep-empty -sarif {' '.join(app_config.CLANG_SCAN_CHECKS)} make\"",
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_files = find_files(working_dir, exts=[".sarif"])

        if len(result_files) == 0:
            raise SASTToolException("Clang-Scan failed to create any analysis reports.")

        # Clang analyzer writes the results of each checker into a separate SARIF file. Therefore, we append the results
        # (JSON string) of each file as one line to the return string.
        return os.linesep.join(map(lambda f: json.dumps(json.loads(f.read_text()), indent=None), result_files))

    def _format(self, string: str) -> SASTFlagSet:
        flags = map(convert_sarif, string.split(os.linesep))
        return SASTFlagSet(set(chain(*flags)))


class SanitizerRunner(SASTToolRunner):
    """
    Abstract sanitizer runner.
    """

    _report_name: ClassVar[str] = "report.csv"

    @abstractmethod
    def _env_vars(self, result_file: Path) -> Dict[str, str]:
        pass

    def _setup(self, temp_dir: Path) -> Path:
        result_file = temp_dir / self._report_name

        run_shell_command(
            f"./{app_config.BUILD_SCRIPT_NAME}",
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=self._env_vars(result_file),
        )

        if not result_file.exists():
            raise SASTToolException("Sanitizer failed to create the analysis report.")

        return temp_dir

    def _analyze(self, working_dir: Path) -> str:
        return (working_dir / self._report_name).read_text()

    def _format(self, string: str) -> SASTFlagSet:
        flags = SASTFlagSet()

        for _line in string.split(os.linesep):
            if _line != "":
                vals = _line.split(",")

                tool = vals[0]
                file = vals[1]
                line = vals[3]
                vuln = "-"

                flags.add(SASTFlag(tool, file, int(line), vuln))

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
