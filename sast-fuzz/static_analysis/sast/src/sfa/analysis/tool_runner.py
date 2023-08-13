import json
import logging
import os
import time
import traceback
from abc import ABC, abstractmethod
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar, Dict

from sfa import SASTToolConfig
from sfa.analysis import SASTFlag, SASTFlags
from sfa.utils.fs import copy_dir, find_files
from sfa.utils.proc import run_shell_command

# Build script name
BUILD_SCRIPT_NAME: str = "build.sh"

# Supported SARIF version
SARIF_VERSION: str = "2.1.0"

# SAST tool setup environment variables
SAST_SETUP_ENV: Dict[str, str] = {
    **os.environ.copy(),
    **{"CC": "clang", "CXX": "clang++", "CFLAGS": "-O0 -fno-inline", "CXXFLAGS": "-O0 -fno-inline"},
}


def convert_sarif(string: str) -> SASTFlags:
    """
    Convert SARIF data into our SAST flag format.

    :param string:
    :return:
    """
    sarif_data = json.loads(string)

    if sarif_data["version"] != SARIF_VERSION:
        raise ValueError(f"SARIF version {sarif_data['version']} is not supported.")

    flags = SASTFlags()

    for run in sarif_data["runs"]:
        tool = run["tool"]["driver"]["name"].lower()

        # Create a mapping between rule ID and vulnerability name
        rule_dict = {rule["id"]: rule["name"] for rule in run["tool"]["driver"]["rules"]}

        for flag in run["results"]:
            vuln = rule_dict[flag["ruleId"]]

            for loc in flag["locations"]:
                file = loc["physicalLocation"]["artifactLocation"]["uri"]
                line = loc["physicalLocation"]["region"]["startLine"]

                file = Path(file).name

                flags.add(SASTFlag(tool, file, line, vuln))

    return flags


class SASTToolRunner(ABC):
    """
    Abstract SAST tool runner.
    """

    def __init__(self, subject_dir: Path, config: SASTToolConfig) -> None:
        self._subject_dir = subject_dir
        self._config = config

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
    def _format(self, string: str) -> SASTFlags:
        """
        Format SAST tool output.

        :param flags:
        :return:
        """
        pass

    def run(self) -> SASTFlags:
        """
        Setup target program, run SAST tool, and format output.

        :return:
        """
        try:
            with TemporaryDirectory() as temp_dir:
                working_dir = self._setup(Path(temp_dir))
                flags = self._analyze(working_dir)

            return self._format(flags)

        except Exception as ex:
            logging.error(ex)
            logging.error(traceback.format_exc())

            return SASTFlags()


class FlawfinderRunner(SASTToolRunner):
    """
    Flawfinder runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        return self._subject_dir

    def _analyze(self, working_dir: Path) -> str:
        return run_shell_command(
            f"{self._config.path} --dataonly --sarif {' '.join(self._config.checks)} {working_dir}"
        )

    def _format(self, string: str) -> SASTFlags:
        return convert_sarif(string)


class SemgrepRunner(SASTToolRunner):
    """
    Semgrep runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        return self._subject_dir

    def _analyze(self, working_dir: Path) -> str:
        return run_shell_command(
            f"{self._config.path} scan --quiet --sarif --jobs {self._config.num_threads} {' '.join([f'--config {check}' for check in self._config.checks])} {working_dir}"
        )

    def _format(self, string: str) -> SASTFlags:
        return convert_sarif(string)


class InferRunner(SASTToolRunner):
    """
    Infer runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / "infer_res"

        run_shell_command(
            f'./{BUILD_SCRIPT_NAME} "{self._config.path} capture --results-dir {result_dir} -- make"',
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        run_shell_command(
            f"{self._config.path} analyze --results-dir {working_dir} --jobs {self._config.num_threads} --keep-going {' '.join(self._config.checks)}"
        )

        time.sleep(5)

        # By default, Infer writes the results into the 'report.json' file once the analysis is complete.
        return (working_dir / "report.json").read_text()

    def _format(self, string: str) -> SASTFlags:
        flags = SASTFlags()

        for flag in json.loads(string):
            tool = "infer"
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
            f'./{BUILD_SCRIPT_NAME} "{self._config.path} database create --language=cpp --command=make --threads={self._config.num_threads} {result_dir}"',
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_file = working_dir / "report.sarif"

        run_shell_command(
            f"{self._config.path} database analyze --output={result_file} --format=sarifv2.1.0 --threads={self._config.num_threads} {working_dir} {' '.join(self._config.checks)}"
        )

        time.sleep(5)

        return result_file.read_text()

    def _format(self, string: str) -> SASTFlags:
        return convert_sarif(string)


class ClangScanRunner(SASTToolRunner):
    """
    Clang analyzer (scan-build) runner.
    """

    def _setup(self, temp_dir: Path) -> Path:
        result_dir = temp_dir / "clang-scan_res"

        run_shell_command(
            f"./{BUILD_SCRIPT_NAME} \"{self._config.path} -o {result_dir} --keep-empty -sarif {' '.join(self._config.checks)} make\"",
            cwd=copy_dir(self._subject_dir, temp_dir),
            env=SAST_SETUP_ENV,
        )

        return result_dir

    def _analyze(self, working_dir: Path) -> str:
        result_files = find_files(working_dir, exts=[".sarif"])

        # Clang analyzer writes the results of each checker into a separate SARIF file. Therefore, we append the results
        # (JSON string) of each file as one line to the return string.
        return os.linesep.join(map(lambda file: json.dumps(json.loads(file.read_text()), indent=None), result_files))

    def _format(self, string: str) -> SASTFlags:
        nested_flags = map(convert_sarif, string.split(os.linesep))

        return SASTFlags(set(chain(*nested_flags)))


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
            f"./{BUILD_SCRIPT_NAME}", cwd=copy_dir(self._subject_dir, temp_dir), env=self._env_vars(result_file)
        )

        return temp_dir

    def _analyze(self, working_dir: Path) -> str:
        return (working_dir / self._report_name).read_text()

    def _format(self, string: str) -> SASTFlags:
        flags = SASTFlags()

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
