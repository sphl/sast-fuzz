from enum import Enum
from typing import List, Union

from sfa.logic.tools.base import SASTToolRunner
from sfa.logic.tools.clangsa import ClangSA
from sfa.logic.tools.codeql import CodeQL
from sfa.logic.tools.flawfinder import Flawfinder
from sfa.logic.tools.infer import Infer
from sfa.logic.tools.sanitizer import Sanitizer, SanitizerType


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


class SASTToolFactory:
    """Factory for creating SAST tool runners."""

    def __init__(self, subject_dir: str):
        self._creators = {
            SASTTool.FLF: Flawfinder(subject_dir),
            SASTTool.IFR: Infer(subject_dir),
            SASTTool.CQL: CodeQL(subject_dir),
            SASTTool.CSA: ClangSA(subject_dir),
            SASTTool.ASN: Sanitizer(subject_dir, SanitizerType.ASAN),
            SASTTool.MSN: Sanitizer(subject_dir, SanitizerType.MSAN)
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
