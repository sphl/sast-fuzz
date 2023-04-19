from enum import Enum

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


class SASTToolFactory:
    """Factory for generating SAST tool runners."""

    def __init__(self, subject_dir: str):
        self._creators = {
            SASTTool.FLF: Flawfinder(subject_dir),
            SASTTool.IFR: Infer(subject_dir),
            SASTTool.CQL: CodeQL(subject_dir),
            SASTTool.CSA: ClangSA(subject_dir),
            SASTTool.ASN: Sanitizer(subject_dir, SanitizerType.ASAN),
            SASTTool.MSN: Sanitizer(subject_dir, SanitizerType.MSAN)
        }

    def get_runner(self, tool: SASTTool) -> SASTToolRunner:
        """Get SAST tool runner based on tool name.

        :param tool: SAST tool name
        :return: Tool runner
        """
        if tool not in self._creators.keys():
            raise ValueError(tool)

        return self._creators[tool]
