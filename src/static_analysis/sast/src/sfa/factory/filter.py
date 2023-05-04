from pathlib import Path
from typing import Dict

from sfa.factory import Factory
from sfa.filter.base import SASTFilter, SASTOutputFilter
from sfa.filter.reachability import ReachabilityFilter


class FilterFactory(Factory[SASTFilter, SASTOutputFilter]):
    """SAST output filter factory."""

    def _get_creators(self, param: Path) -> Dict[SASTFilter, SASTOutputFilter]:
        return {
            SASTFilter.REH: ReachabilityFilter(param)
        }
