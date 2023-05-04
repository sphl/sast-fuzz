import subprocess as proc
from enum import Enum, auto
from os import linesep
from pathlib import Path
from typing import Dict, ClassVar

from sfa.config import SHELL, BUILD_SCRIPT_NAME
from sfa.tool_runner.base import SASTTool, SASTToolFlag, SASTToolOutput, SASTToolRunner
from sfa.util.io import copy_dir, read


class SanitizerType(Enum):
    ASAN = auto()
    MSAN = auto()


class SanitizerRunner(SASTToolRunner):
    """Address-/MemorySanitizer runner."""

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

    def __init__(self, subject_dir: Path, sanitizer_type: SanitizerType):
        super().__init__(subject_dir)
        self._sanitizer_type = sanitizer_type

    def _setup(self, temp_dir: Path) -> Path:
        # TODO: Check if custom LLVM version is installed!
        assert (self._subject_dir / Path(BUILD_SCRIPT_NAME)).exists()

        config = self._sanitizer_config[self._sanitizer_type]

        result_file = temp_dir / Path(self._result_file_name)

        setup_env = self._setup_env
        setup_env["CFLAGS"] = f"{setup_env['CFLAGS']} -g -fsanitize={config['opt']}"
        setup_env["CXXFLAGS"] = f"{setup_env['CXXFLAGS']} -g -fsanitize={config['opt']}"
        setup_env[config["env"]] = str(result_file)

        proc.run([SHELL, BUILD_SCRIPT_NAME], cwd=copy_dir(self._subject_dir, temp_dir), env=setup_env)

        assert result_file.exists()

        return temp_dir

    def _analyze(self, working_dir: str) -> str:
        return read(working_dir / Path(self._result_file_name))

    def _format(self, flags: str) -> SASTToolOutput:
        result_set = set()

        for _line in flags.split(linesep):
            if _line != "":
                line_vals = _line.split(",")

                if self._sanitizer_type == SanitizerType.ASAN:
                    tool = SASTTool.ASN.value
                else:
                    tool = SASTTool.MSN.value

                file = Path(line_vals[1]).name
                line = int(line_vals[3])

                result_set.add(SASTToolFlag(tool, file, line, "-"))

        return result_set
