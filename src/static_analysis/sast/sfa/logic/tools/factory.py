from enum import Enum
from typing import List, Union

from sfa.logic.tools.base import SASTToolRunner
from sfa.logic.tools.clangsa import ClangSARunner
from sfa.logic.tools.codeql import CodeQLRunner
from sfa.logic.tools.flawfinder import FlawfinderRunner
from sfa.logic.tools.infer import InferRunner
from sfa.logic.tools.sanitizer import SanitizerRunner, SanitizerType


class SASTTool(Enum):
    FLF = "flawfinder"
    IFR = "infer"
    CQL = "codeql"
    CSA = "clangsa"
    ASN = "asan"
    MSN = "msan"

    @classmethod
    def values(cls) -> List[str]:
        return [tool.value for tool in cls]


class SASTToolRunnerFactory:
    """Factory for creating SAST tool runners."""

    def __init__(self, subject_dir: str):
        self._creators = {
            SASTTool.FLF: FlawfinderRunner(subject_dir),
            SASTTool.IFR: InferRunner(subject_dir),
            SASTTool.CQL: CodeQLRunner(subject_dir),
            SASTTool.CSA: ClangSARunner(subject_dir),
            SASTTool.ASN: SanitizerRunner(subject_dir, SanitizerType.ASAN),
            SASTTool.MSN: SanitizerRunner(subject_dir, SanitizerType.MSAN)
        }

    def get_runner(self, tool: Union[str, SASTTool]) -> SASTToolRunner:
        """Get a runner for a specific SAST tool.

        :param tool: SAST tool
        :return: Runner
        """
        if type(tool) is str:
            key = SASTTool(tool)
        elif type(tool) is SASTTool:
            key = tool
        else:
            raise NotImplementedError()

        return self._creators[key]
