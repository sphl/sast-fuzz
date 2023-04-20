import subprocess as proc
from enum import Enum, auto
from os import path, linesep
from typing import Dict, ClassVar

from sfa.config import SHELL, BUILD_SCRIPT_NAME
from sfa.logic.tools.base import SASTToolRunner, SASTToolFlag, SASTToolOutput
from sfa.utils.io import copy_dir, read
from sfa.utils.error import log_assert


class SanitizerType(Enum):
    ASAN = auto()
    MSAN = auto()


class Sanitizer(SASTToolRunner):
    """Address-/MemorySanitizer runner implementation."""

    _result_file_name: ClassVar[str] = "report.csv"
    """Name of the sanitizer output file."""

    _sanitizer_config: ClassVar[Dict[SanitizerType, Dict[str, str]]] = {
        SanitizerType.ASAN: {
            "opt": "address",
            "env": "ASAN_OUTPUT_FILE"
        },
        SanitizerType.MSAN: {
            "opt": "memory",
            "env": "MSAN_OUTPUT_FILE"
        }
    }
    """Configuration (Clang flag, output file env. variable) of the supported sanitizers."""

    def __init__(self, subject_dir: str, sanitizer_type: SanitizerType = SanitizerType.ASAN):
        super().__init__(subject_dir)
        self._sanitizer_type = sanitizer_type

    def _setup(self, temp_dir: str) -> str:
        # TODO: Check if custom LLVM version is installed!
        log_assert(path.exists(path.join(self._subject_dir, BUILD_SCRIPT_NAME)))

        config = self._sanitizer_config[self._sanitizer_type]

        result_file = path.join(temp_dir, self._result_file_name)

        setup_env = self._setup_env
        setup_env["CFLAGS"] = f"{setup_env['CFLAGS']} -g -fsanitize={config['opt']}"
        setup_env["CXXFLAGS"] = f"{setup_env['CXXFLAGS']} -g -fsanitize={config['opt']}"
        setup_env[config["env"]] = result_file

        proc.run([SHELL, BUILD_SCRIPT_NAME], cwd=copy_dir(self._subject_dir, temp_dir), env=setup_env)

        log_assert(path.exists(result_file))

        return temp_dir

    def _analyze(self, working_dir: str) -> str:
        return read(path.join(working_dir, self._result_file_name))

    def _format(self, findings: str) -> SASTToolOutput:
        result_set = set()

        for line in findings.split(linesep):
            if line != "":
                line_vals = line.split(",")

                tool_name = line_vals[0].lower()
                file_name = path.basename(line_vals[1])
                code_line = int(line_vals[3])
                vuln_type = "-"

                result_set.add(SASTToolFlag(tool_name, file_name, code_line, vuln_type))

        return result_set
