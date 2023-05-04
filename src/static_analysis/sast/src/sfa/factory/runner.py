from typing import Dict, Any

from sfa.factory import Factory
from sfa.tool_runner import SASTTool, SASTToolRunner
from sfa.tool_runner.clang_scan import ClangScanRunner
from sfa.tool_runner.codeql import CodeQLRunner
from sfa.tool_runner.flawfinder import FlawfinderRunner
from sfa.tool_runner.infer import InferRunner
from sfa.tool_runner.sanitizer import SanitizerRunner, SanitizerType


class RunnerFactory(Factory[SASTTool, SASTToolRunner]):
    """SAST tool runner factory."""

    def _get_creators(self, param: Any) -> Dict[SASTTool, SASTToolRunner]:
        return {
            SASTTool.FLF: FlawfinderRunner(param),
            SASTTool.IFR: InferRunner(param),
            SASTTool.CQL: CodeQLRunner(param),
            SASTTool.CLS: ClangScanRunner(param),
            SASTTool.ASN: SanitizerRunner(param, SanitizerType.ASAN),
            SASTTool.MSN: SanitizerRunner(param, SanitizerType.MSAN)
        }
