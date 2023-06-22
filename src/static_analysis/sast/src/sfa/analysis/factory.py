from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Iterable

from sfa import SASTToolConfig
from sfa.analysis.filter import ReachabilityFilter
from sfa.analysis.grouping import BasicBlockGrouping
from sfa.analysis.tool_runner import (
    AddressSanitizerRunner,
    ClangScanRunner,
    CodeQLRunner,
    FlawfinderRunner,
    InferRunner,
    MemorySanitizerRunner,
    SemgrepRunner,
)


class SASTTool(Enum):
    FLF = "flawfinder"
    SGR = "semgrep"
    IFR = "infer"
    CQL = "codeql"
    CLS = "clang-scan"
    ASN = "asan"
    MSN = "msan"


class SASTFlagFilterMode(Enum):
    REH = "reachability"


class SASTFlagGroupingMode(Enum):
    BASIC_BLOCK = "basic-block"


class Factory(ABC):
    """
    Abstract factory.
    """

    @abstractmethod
    def _create_instances(self, param: Any) -> Dict:
        pass

    def __init__(self, param: Any) -> None:
        if param is None:
            self._instances = {}
        else:
            self._instances = self._create_instances(param)

    def get_instance(self, key: Any) -> Any:
        return self._instances[key]

    def get_instances(self, keys: Iterable) -> Iterable:
        return map(self.get_instance, keys)


class SASTToolRunnerFactory(Factory):
    """
    SAST tool runner factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        subject_dir, app_config = param
        return {
            SASTTool.FLF: FlawfinderRunner(subject_dir, app_config.flawfinder),
            SASTTool.SGR: SemgrepRunner(subject_dir, app_config.semgrep),
            SASTTool.IFR: InferRunner(subject_dir, app_config.infer),
            SASTTool.CQL: CodeQLRunner(subject_dir, app_config.codeql),
            SASTTool.CLS: ClangScanRunner(subject_dir, app_config.clang_scan),
            SASTTool.ASN: AddressSanitizerRunner(subject_dir, SASTToolConfig()),
            SASTTool.MSN: MemorySanitizerRunner(subject_dir, SASTToolConfig()),
        }


class SASTFlagFilterFactory(Factory):
    """
    SAST flag filter factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        return {SASTFlagFilterMode.REH: ReachabilityFilter(param)}


class SASTFlagGroupingFactory(Factory):
    """
    SAST flag grouping factory.
    """

    def _create_instances(self, param: Any) -> Dict:
        inspec_file, app_config = param
        return {SASTFlagGroupingMode.BASIC_BLOCK: BasicBlockGrouping(inspec_file, app_config.score_weights)}
